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


from requests_oauthlib import OAuth1Session
from six.moves import urllib
from ansible.utils.display import Display

display = Display()
urlparse, urljoin = urllib.parse.urlparse, urllib.parse.urljoin


class APIError(Exception):
    pass

class APISession():
    def __init__(self, maas_url, api_key, api_version = '2.0'):
        client_key, token, token_secret = api_key.split(':')
        self.session = OAuth1Session(client_key=client_key, 
                                     resource_owner_key=token,
                                     resource_owner_secret=token_secret)
        self.base_url = urljoin(maas_url, '../')
        self.api_base = urljoin(self.base_url, '/MAAS/api/%s/' % api_version)
        self.headers = {'Accept': 'application/json'}

    def call(self, method, endpoint, params={}):
        if method == 'GET':
            http = self.session.get
        elif method == 'POST':
            http = self.session.post
        elif method == 'PUT':
            http = self.session.put
        elif method == 'DELETE':
            http = self.session.delete
        else:
            raise APIError('Invalid method: %s' % method)

        try:
            url = urljoin(self.api_base, endpoint)
            resp = http(url, json = params, headers=self.headers)
            display.vvv('Called %s: (%s) %s' % (endpoint, resp.status_code, resp.content))
            return resp
        except Exception as e:
            return APIError('Exception occured while trying to call MAAS api. The original exception was: %s' % e)

