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

from ansible_collections.heilerich.maas.plugins.module_utils.connection import get_client, CallError
from ansible_collections.heilerich.maas.plugins.module_utils.helpers import AttrDict
from ansible.utils.display import Display
from ansible.plugins.action import ActionBase
from ansible.module_utils._text import to_native

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
            install_kvm = self._task.args.get('install_kvm', False),
            maas_url = self._task.args.get('maas_url', 'http://localhost:5240/MAAS/'),
            api_key = self._task.args.get('api_key', None),
            username = self._task.args.get('username', None),
            password = self._task.args.get('password', None)
        )

        try:
            client = get_client(config)
            try:
                machine = client.machines.get(system_id=str(config.system_id))
                self.result['machine'] = machine._orig_data
            except CallError as e:
                return self._error('Could not get the machine. The error was: %s' % to_native(e))

            if machine.status.value != 4:
                current_user = client.users.whoami().username
                if machine.status.value == 10:
                    if machine.owner.username != current_user:
                        return self._error('Machine is not allocated for current user (%s) but for user %s.' \
                                           % (to_native(current_user), to_native(machine.owner.username)))
                    else:
                        pass
                elif machine.status.value in [6, 9]:
                    # Deployed or deploying
                    return self.result
                else:
                    return self._error('Machine must be in ready or allocated state to be deployed. Current status is: %s' \
                                       % to_native(machine.status_name))

            if config.check_mode:
                self.result['changed'] = True
                return self.result

            machine.deploy(
                user_data = config.user_data,
                distro_series = config.distro_series,
                hwe_kernel = config.hwe_kernel,
                comment = config.comment,
                wait = config.wait,
                wait_interval = config.wait_interval,
                install_kvm = config.install_kvm
            )

            self.result['changed'] = True
            self.result['machine'] = machine._data

        except Exception as e:
            import traceback
            display.vvv(traceback.format_exc())
            return self._error('An error occured while deploying machine: %s' % to_native(e))
        
        return self.result
