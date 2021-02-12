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

import asyncio
from time import time, sleep
from ansible.utils.display import Display

display = Display()

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class MachinePoller:
    def __init__(self, config, session):
        self.config = config
        self.session = session

    def wait(self, system_id, target, acceptable_status, numeric_status=False):
        machine_endpoint = 'machines/%s/' % system_id
        try:
            iterator = iter(target)
        except TypeError: # not iterable
            target = set([target])
        else: # iterable
            if isinstance(target, str):
                target = set([target])
            else:
                target = set(target)

        acceptable_status = set(acceptable_status)
        acceptable_status = acceptable_status.union(target)

        display.vvv('Target status: %s, acceptable status: %s' % (target, acceptable_status))

        def poll_machine():
            wait_response = self.session.call('GET', machine_endpoint)
            if numeric_status:
                status = int(wait_response.data.get('status', 0))
            else:
                status = wait_response.data.get('status_name', '').lower()

            display.vvv('Waiting for machine %s: status %s, target %s (%s)' % (system_id, status, target, target == status))
            data = wait_response.data
            if not wait_response.ok or not status in acceptable_status:
               return (True, 'Waiting for machine failed. Last status: %s' % status, data)
            elif status in target:
               return (True, None, data)
            elif status in acceptable_status:
               return (False, None, data)
            else:
               return (True, 'Waiting for machine failed. Last status: %s' % status, data)
        
        start_time = time()
        done = False
        while not done:
            done, error, data = poll_machine()
            display.vvv('Waiting: done (%s), error is None (%s)' % (done, error is None))
            if error is not None:
                return (error, data)
            if time() - start_time > self.config.wait_timeout:
                return ('Timeout while waiting for machine.', data)

            if not done:
                sleep(self.config.wait_interval)

        return None, data
