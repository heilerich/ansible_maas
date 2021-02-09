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
from ansible_collections.heilerich.maas.plugins.module_utils.helpers import AttrDict
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
            user_data = self._task.args.get('user_data', None),
            distro_series = self._task.args.get('distro_series', None),
            hwe_kernel = self._task.args.get('hwe_kernel', None),
            comment = self._task.args.get('comment', None),
            wait = self._task.args.get('wait', False),
            wait_interval = int(self._task.args.get('wait_interval', 5)),
            wait_timeout = int(self._task.args.get('wait_timeout', 600)),
            install_kvm = self._task.args.get('install_kvm', False),
            maas_url = self._task.args.get('maas_url', 'http://localhost:5240/MAAS/'),
            api_key = self._task.args.get('api_key', None)
        )

        try:
            machine_endpoint = 'machines/%s/' % config.system_id
            try:
                session = APISession(config.maas_url, config.api_key)
                machine_response = session.call('GET', machine_endpoint)
                machine = machine_response.data
                self.result['machine'] = machine_response.data
                user_response = session.call('GET', 'users/?op=whoami')
                self.user = user_response.data
                if not machine_response.ok or not user_response.ok:
                    return self._error('API call failed')
            except APIError as e:
                return self._error('Could not get the machine. The error was: %s' % to_native(e))

            if machine['status'] != 4:
                current_user = self.user['username']
                if machine['status'] == 10:
                    if machine['owner'] != current_user:
                        return self._error('Machine is not allocated for current user (%s) but for user %s.' \
                                           % (to_native(current_user), to_native(machine.owner.username)))
                    else:
                        pass
                elif machine['status'] in [6, 9]:
                    # Deployed or deploying
                    return self.result
                else:
                    return self._error('Machine must be in ready or allocated state to be deployed. Current status is: %s' \
                                       % to_native(machine['status_name']))

            if config.check_mode:
                self.result['changed'] = True
                return self.result

            deploy_response = session.call('POST', '%s?op=deploy' % machine_endpoint, dict(
                user_data = config.user_data,
                distro_series = config.distro_series,
                hwe_kernel = config.hwe_kernel,
                comment = config.comment,
                install_kvm = config.install_kvm
            ))

            if not deploy_response.ok:
                return self._error('Deployment API call returned error: %s' % deploy_response.data)

            self.result['changed'] = True
            self.result['machine'] = deploy_response.data

            def poll_machine():
                wait_response = session.call('GET', machine_endpoint)
                status = wait_response.data['status']
                data = wait_response.data
                if not wait_response.ok or not status in [6, 9]:
                   return (True, self._error('Polling for deployment status failed with: %s' % wait_response.data), data)
                elif status == 9:
                   return (False, None, data)
                elif status == 6:
                   return (True, None, data)
                else:
                   return (True, self._error('Deployment failed with machine state: %s' % wait_response.data), data)
            
            if config.wait:
                start_time = time()
                done = False
                while not done:
                    done, error, data = poll_machine()
                    if error is not None:
                        return error
                    if time() - start_time > config.wait_timeout:
                        return self._error('Timeout while waiting for machine to finish deployment')

                    self.result['machine'] = data
                    sleep(config.wait_interval)

        except Exception as e:
            import traceback
            display.vvv(traceback.format_exc())
            return self._error('An error occured while deploying machine: %s' % to_native(e))
        
        return self.result

