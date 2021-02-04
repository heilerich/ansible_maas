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
short_description: Acquires and deploys a machine in MAAS
description:
    - Gets machine information for the machine with the provided system_id
    - Acquires the machine as the logged in MAAS user
    - Deploys the OS with the provided parameters
extends_documentation_fragment:
    - heilerich.maas.connection
options:
    system_id:
        description: ID of the system in MAAS (visible in the URL).
        type: str
        required: true
    user_data:
        description: User-data to provide to the machine when booting.
        type: str
    distro_series:
        description: "The OS to deploy. If no value is set the default value according
            to the MAAS settings is used."
        type: str
    hwe_kernel:
        description: The HWE kernel to deploy. Probably only relevant when deploying Ubuntu.
        type: str
    comment:
        description: A comment for the event log.
        type: str
    wait:
        description: If true, wait until the deploy is complete.
        type: bool
        default: no
    wait_interval:
        description: How often to poll, defaults to 5 seconds.§
        type: int
        default: 5
    install_kvm:
        description: Prepare and register the machine for use as a KVM based virtual machine host in MAAS.
        type: bool
        default: no
author:
- Felix Heilmeyer <code@fehe.eu>
'''

EXAMPLES = r'''
# Deploy a system, wait for it to become ready, gather facts and continue 
- hosts: all
  gather_facts: no
  tasks:
  - name: Deploy machine
    heilerich.maas.deploy:
      system_id: '{{ maas_id }}'
      wait: yes
      user_data: "{{ lookup('template', './cloud_init.yaml.j2') }}"
    delegate_to: localhost
  - name: Ensure system is operational
    wait_for_connection:
      timeout: 900
  - name: Gather facts for first time
    setup:
'''

RETURN = r'''
machine_info:
    description: the MAAS machine info for the deployed machine
    returned: always
    type: dict
'''

