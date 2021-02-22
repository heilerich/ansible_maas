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
from requests_oauthlib import OAuth1Session
from six.moves import urllib
from ansible.utils.display import Display
from ansible.module_utils._text import to_native
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

display = Display()
urlparse, urljoin = urllib.parse.urlparse, urllib.parse.urljoin


class APIError(Exception):
    pass

class APISession():
    def __init__(self, maas_url, api_key, api_version = '2.0'):
        try:
            client_key, token, token_secret = api_key.split(':')
        except Exception as e:
            raise Exception('Invalid API Key: An exception was raised while parsing the MAAS API key (%s). The exception was: %s' % (api_key, e))
        self.session = OAuth1Session(client_key=client_key, 
                                     signature_method='PLAINTEXT',
                                     resource_owner_key=token,
                                     resource_owner_secret=token_secret)
        retry_strategy = Retry(total=5,backoff_factor=2)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.base_url = urljoin(maas_url, '../')
        self.api_base = urljoin(self.base_url, '/MAAS/api/%s/' % api_version)
        self.headers = {'Accept': 'application/json'}

    def decode(self, response):
        text = to_native(response.text)
        try:
            return json.loads(text)
        except Exception as e:
            display.vvv('Exception decoding JSON: %s' % to_native(e))
            return text

    def call(self, method, endpoint, params={}):
        try:
            url = urljoin(self.api_base, endpoint)
            # MAAS expects multipart/form-data and doesn't like filenames
            file_params = {k: ('', v) for k, v in params.items()}
            resp = self.session.request(method, url, files=file_params, headers=self.headers)
            display.vvvv('Called %s: (%s) %s' % (endpoint, resp.status_code, resp.content))
            resp.data = self.decode(resp)
            return resp
        except Exception as e:
            raise APIError('Exception occured while trying to call MAAS api. The original exception was: %s' % e)

