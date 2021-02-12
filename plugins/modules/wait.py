#!/usr/bin/python
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


DOCUMENTATION = r'''
---
module: heilerich.maas.deploy
short_description: Waits for a machine
description:
    - Waits for a machine to change it's status to the desired value.
    - The API is polled in the defined interval to determine the status.
extends_documentation_fragment:
    - heilerich.maas.api
    - heilerich.maas.wait
options:
    system_id:
        description: ID of the system in MAAS (visible in the URL).
        type: str
        required: true
    target:
        description: The desired machine status (e.g. 'ready')
        type: [str, list]
        required: true
    acceptable_status:
        description: "List of acceptable status (e.g. ['comissioning']). If the machine status changes to a status that is neither the target nor in acceptable_status the task will fail"
        type: list
        required: true
author:
- Felix Heilmeyer <code@fehe.eu>
'''

EXAMPLES = r'''
# Wait for a system to reach the ready state after comissioning
- hosts: all
  gather_facts: no
  tasks:
  - name: Wait for the machine to be ready
    heilerich.maas.wait:
      system_id: '{{ maas_id }}'
      target: 'ready'
      acceptable_status: ['commissioning']
      wait_interval: 10
      wait_timeout: 900
    delegate_to: localhost
'''

RETURN = r'''
machine_info:
    description: the MAAS machine info for the deployed machine
    returned: always
    type: dict
'''

