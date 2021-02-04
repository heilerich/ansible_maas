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

DOCUMENTATION = '''
    name: maas_machines
    author:
      - Felix Heilmeyer <code@fehe.eu>
    short_description: Ansible dynamic inventory plugin for MAAS. 
    requirements:
        - python >= 2.7
        - L(python-libmaas,https://maas.github.io/python-libmaas/) >= 0.6.6
    extends_documentation_fragment:
        - heilerich.maas.connection
        - constructed
        - inventory_cache
    description:
        - Reads inventories from the MAAS API
        - Uses a YAML configuration file [*]maas.[yml|yaml].
    options:
        plugin:
            description: The name of this plugin, it should always be set to C(heilerich.maas.maas_machines)
            type: str
            required: true
            choices: [ maas_machines, heilerich.maas.maas_machines]
        include_vms:
            description: If set to (no) only physical machnies will be returned
            type: bool
            default: yes
'''

EXAMPLES = '''
# Minimal example using maas on a machine named controller
plugin: heilerich.maas.maas_machines
maas_url: http://controller:5240/MAAS/
api_key: xxx

# Example using constructed features and data returned from the MAAS api machine endpoint
plugin: heilerich.maas.maas_machines
maas_url: http://controller:5240/MAAS/
api_key: xxx
# You might need to set strict to false since some keys are not set when 
# machines are not deployed yet
strict: False
keyed_groups:
  # add e.g. x86_64 hosts to an arch_amd64_generic group
  - prefix: arch
    key: 'architecture'
  # group by os
  - prefix: os
    key: 'osystem'
groups:
    ready: status_name == 'Ready'
# Add custom hostvars
compose:
    block_devices: physicalblockdevice_set | map(attribute='name')

'''

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display
from ansible_collections.heilerich.maas.plugins.module_utils.connection import get_client
from ansible_collections.heilerich.maas.plugins.module_utils.helpers import AttrDict, cleanup


display = Display()


class Host(object):
    @classmethod
    def from_machine(cls, maas_machine):
        data = dict(
            name = to_native(maas_machine.fqdn),
            status = to_native(maas_machine.status.name.lower()),
            maas_id = to_native(maas_machine.system_id),
            zone = 'zone_%s' % to_native(maas_machine.zone.name),
            domain = 'domain_%s' % to_native(maas_machine.domain.name),
            pool = 'pool_%s' % to_native(maas_machine.pool.name),
            tags = [t.name for t in maas_machine.tags],
            maas_data = maas_machine._orig_data
        )
        data['metal'] = 'virtual' not in data['tags']
        data['host'] = to_native(maas_machine.ip_addresses[0] if len(maas_machine.ip_addresses)>0 else data['name'])

        return cls(data)
    
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data[name]
    
    def groups(self):
        return ['metal' if self.metal else 'virtual', self.zone, self.domain, self.pool, self.status]
    
    def attrs(self):
        return self.maas_data
    
    def add_to_inventory(self, inventory):
        inventory.add_host(self.name)
        
        for group in self.groups():
            inventory.add_group(group)
            inventory.add_host(self.name, group)
        
        inventory.set_variable(self.name, 'ansible_host', self.host)
        inventory.set_variable(self.name, 'maas_id', self.maas_id)


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using the MAAS API as source. '''

    NAME = 'heilerich.maas.maas_machines'

    def _error(self, msg):
        raise AnsibleError(msg)

    def _fetch(self):
        display.vvv(u'Fetching data from MAAS API')
        try:
            client = get_client(self._config) 
            return [Host.from_machine(m) for m in client.machines.list()]
        except Exception as e:
            raise AnsibleError('Unable to fetch data from the MAAS API, this was the original exception: %s' %
                               to_native(e))

    def _populate(self, hosts):
        self.inventory.add_group('all')
        self.inventory.add_group('metal')
        self.inventory.add_group('virtual')

        try:
            for host in hosts:
                if not self._config.include_vms and 'virtual' in host.groups():
                    continue

                host.add_to_inventory(self.inventory)

                strict = self.get_option('strict')
                self._set_composite_vars(self.get_option('compose'),
                                         host.attrs(),
                                         host.name,
                                         strict=strict)
                self._add_host_to_composed_groups(self.get_option('groups'),
                                                  host.attrs(),
                                                  host.name,
                                                  strict=strict)
                self._add_host_to_keyed_groups(self.get_option('keyed_groups'),
                                               host.attrs(),
                                               host.name,
                                               strict=strict)
        except Exception as e:
            raise AnsibleError('Unable to parse data from the MAAS API, this was the original exception: %s' %
                               to_native(e))

    def verify_file(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return (
            super(InventoryModule, self).verify_file(path) and
            path.endswith(('maas.yaml', 'maas.yml')))

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)

        self._config = AttrDict(
            maas_url=self.get_option('maas_url'),
            api_key=self.get_option('api_key'),
            username=self.get_option('username'),
            password=self.get_option('password'),
            include_vms=self.get_option('include_vms'),
            debug=None,
        )

        cache_key = self.get_cache_key(path)
        user_cache_setting = self.get_option('cache')
        attempt_to_read_cache = user_cache_setting and cache
        cache_needs_update = user_cache_setting and not cache

        if attempt_to_read_cache:
            try:
                display.vvv(u'Attempting to read cache')
                cached_data = self._cache[cache_key]
                results = [Host(host_data) for host_data in cached_data]
            except KeyError:
                display.vvv(u'Cache needs update')
                cache_needs_update = True

        if cache_needs_update or not user_cache_setting:
            results = self._fetch()

        if cache_needs_update:
            cache_data = [host._data for host in results]
            self._cache[cache_key] = cache_data

        self._populate(results)

        cleanup()

