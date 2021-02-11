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

from ansible_collections.heilerich.maas.plugins.module_utils.api import APISession, APIError
from ansible_collections.heilerich.maas.plugins.module_utils.helpers import AttrDict, MachinePoller
from ansible.utils.display import Display
from ansible.plugins.action import ActionBase
from ansible.module_utils._text import to_native
from time import time, sleep

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
            system_id = self._task.args.get('system_id', None),
            acceptable_status = self._task.args.get('acceptable_status', []),
            target = self._task.args.get('target', ''),
            wait_interval = int(self._task.args.get('wait_interval', 5)),
            wait_timeout = int(self._task.args.get('wait_timeout', 600)),
            maas_url = self._task.args.get('maas_url', 'http://localhost:5240/MAAS/'),
            api_version = self._task.args.get('api_version', '2.0'),
            api_key = self._task.args.get('api_key', None)
        )

        try:
            machine_endpoint = 'machines/%s/' % config.system_id

            session = APISession(config.maas_url, config.api_key, config.api_version)
            poller = MachinePoller(config, session)

            error, data = poller.wait(config.system_id, 
                                      target=config.target, 
                                      acceptable_status=config.acceptable_status,
                                      numeric_status=False)

            if error is not None:
                return self._error(error)

            self.result['machine'] = data

        except Exception as e:
            import traceback
            display.vvv(traceback.format_exc())
            return self._error('An error occured while waiting for machine: %s' % to_native(e))
        
        return self.result

