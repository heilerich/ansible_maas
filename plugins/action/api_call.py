# -*- coding: utf-8 -*-
# MIT License
# 
# Copyright (c) 2021 Felix Heilmeyer
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible_collections.heilerich.maas.plugins.module_utils.api import APISession
from ansible_collections.heilerich.maas.plugins.module_utils.helpers import AttrDict
from ansible.utils.display import Display
from ansible.plugins.action import ActionBase
from ansible.module_utils._text import to_native
from json.decoder import JSONDecodeError

display = Display()

class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def _error(self, msg):
        self.result['failed'] = True
        self.result['msg'] = to_native(msg)
        return self.result

    def run(self, tmp=None, task_vars=None):
        self.result = super(ActionModule, self).run(tmp, task_vars)
        self.result.update(
            dict(
                changed=False,
                failed=False,
                msg='',
                skipped=False
            )
        )

        self._supports_check_mode = True
        self._supports_async = False
        
        config = AttrDict(
            check_mode = self._play_context.check_mode,
            endpoint = self._task.args.get('endpoint', None),
            api_version = self._task.args.get('api_version', '2.0'),
            method = self._task.args.get('method', 'GET'),
            parameters = self._task.args.get('parameters', {}),
            fail_on_error = self._task.args.get('fail_on_error', True),
            maas_url = self._task.args.get('maas_url', 'http://localhost:5240/MAAS/'),
            api_key = self._task.args.get('api_key', None)
        )

        def call():
            response = session.call(config.method, config.endpoint, config.parameters)
            
            self.result.update(dict(
                status_code = response.status_code,
                data = response.data,
                success = response.ok
            ))
            
            return response
        def return_if_okay():
            if not response.ok and config.fail_on_error:
                return self._error('API returned an error status code')
            else:
                return self.result

        try:
            session = APISession(config.maas_url, config.api_key, config.api_version)

            if config.check_mode:
                if config.method == 'GET':
                    response = call()
                    return_if_okay()
                else:
                    self.result['skipped'] = True
                    return self.result
                
            if config.method != 'GET':
                pre_check_response = session.call('GET', config.endpoint)

            response = call()
            if response.ok and config.method != 'GET':
                self.result['changed'] = self.result['data'] != pre_check_response.data

            return_if_okay()

        except Exception as e:
            import traceback
            display.vvv(traceback.format_exc())
            return self._error('An unexpected error occured while communicating with the MAAS: %s' % to_native(e))
        
        return self.result

