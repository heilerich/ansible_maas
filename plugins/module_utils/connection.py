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

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.utils.display import Display

try:
    from maas.client import login, connect
    from maas.client.bones import CallError
    LIB_INSTALLED = True 
except ImportError:
    LIB_INSTALLED = False

display = Display()

def _error(msg):
    raise AnsibleError(msg)


def get_client(config):
    if not LIB_INSTALLED:
        _error('The python-libmaas python module is required to commmunicate with MAAS: '
               'http://maas.github.io/python-libmaas/')

    if 'api_key' in config and config.api_key is not None:
        display.vvv('Authenticating to MAAS with API key')
        return connect(config.maas_url, apikey=config.api_key)
    elif 'username' in config and config.username is not None \
            and 'password' in config and config.password is not None:
        display.vvv('Authenticating to MAAS with username and password')
        return login(config.maas_url, username=config.username, password=config.password)
    else:
        supplied = ', '.join([name for name in ('api_key', 'username', 'password') if name in config and config[name] is not None])
        _error('Could not connect to MAAS. You need to either specify an API key or a username/password combination. ' +
               'The following were supplied: %s' % to_native(supplied))
