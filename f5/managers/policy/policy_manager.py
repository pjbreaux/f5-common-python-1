# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


class NonExtantVirtualForPolicy(Exception):
    pass


class PolicyConfigurationDictKeyError(KeyError):
    pass


class PolicyManager(object):
    def __init__(self, bigip, config):
        '''Construct a PolicyManager with the appropriate config.

        :param bigip: ManagementRoot object -- end device
        :param config: dict -- expected configuration for a policy
            ex:
                {'name': 'my_policy', 'partition': 'my_part',
                'virtual_name': 'my_listener', 'ordinal': 2, 'rules': [...]}
        '''

        self._validate_config_input(config)
        self.bigip = bigip
        self._ensure_device_config()

    def _validate_config_input(self, config):
        '''Validate input config conforms to policy spec.

        :param config: dict -- expected configuration for a policy
        :raises: PolicyConfigurationDictKeyError(missing)
        '''

        expected_keys = ['name', 'partition', 'virtual_name', 'ordinal']
        missing = ''
        for ek in expected_keys:
            if ek not in config:
                missing += "\nMissing key '{}' from config dict".format(ek)
        if not missing:
            raise PolicyConfigurationDictKeyError(missing)
        self.config = config

    def _ensure_device_config(self):
        '''Ensure device has config given by consumer.

        Update the config on the device to match that of the config dict
        given by the consumer upon instantion of this class.
        '''

        self._ensure_virtual_exists()

    def _ensure_rules(self):
        '''Rules should exist based on config input.'''

        for rule in self.config['rules']:
            pass

    def _ensure_virtual_exists(self):
        '''Ensure expected virtual server exists.

        :raises: NonExtantVirtualForPolicy
        '''

        if not self.bigip.tm.ltm.virtuals.virtual.exists(
                name=self.config['virtual_name'],
                partition=self.config['partition']):
            msg = "No virtual with name, {}, exists".format(
                self.config['virtual_name'])
            raise NonExtantVirtualForPolicy(msg)
