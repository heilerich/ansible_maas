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
module: heilerich.maas.api_call
short_description: Make direct calls to MAAS API endpoints.
description:
    - This plugins let's you make calls directly to the maas_api.
    - It let's you use API functionality that is not yet implemented as a plugin.
    - "Keep in mind that the API is a moving target, when the spec changes you need to update
      your plays and roles yourself."
    - There are no checks and failsafes here, proceed with caution.
    - For more information please refer to the L(API Documentation,https://maas.io/docs/api)
extends_documentation_fragment:
    - heilerich.maas.connection
options:
    endpoint:
        description: "The URL of the endpoint to call relative to the API Base, e.g. I(endpoint='account/').
            Mind the slashes."
        type: str
        required: true
    api_version:
        description: The API version to use, defaults to I(api_version='2.0')
        type: str
        default: '2.0'
    method:
        description: The HTTP method to use.
        type: str
        default: 'GET'
        choices:
        - 'GET'
        - 'POST'
        - 'PUT'
        - 'DELETE'
    parameters:
        description: The parameters to send
        type: dict
        default: {}
    fail_on_error:
        description: "If I(fail_on_error=true) the action fails if a non 2xx status code is returned.
            This is the default behaviour."
        type: bool
        default: true
author:
- Felix Heilmeyer <code@fehe.eu>
'''

EXAMPLES = r'''
# TODO
'''

RETURN = r'''
data:
    description: The data returned by the API
    returned: always
    type: dict
status_code:
    description: The HTTP status code
    returned: always
    type: int
success:
    description: True if the call returned a 2xx status code
    returned: always
    type: bool
'''

