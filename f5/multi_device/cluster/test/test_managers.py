# Copyright 2016 F5 Networks Inc.

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
#

from f5.multi_device.cluster.managers import DeviceGroupManager
# from f5.multi_device.cluster.managers import TrustedPeerManager

import mock
import pytest


CLASS_LOC = 'f5.multi_device.cluster.managers.DeviceGroupManager'


class FakeDeviceInfo(object):
    def __init__(self):
        self.name = 'test'


@pytest.fixture
def DGMSyncFailover():
    root_device = mock.MagicMock()
    devices = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
    dgm = DeviceGroupManager(
        'dg_name', root_device, devices, 'part', 'sync-failover')
    device_info_mock = mock.MagicMock(return_value=FakeDeviceInfo())
    act_state_mock = mock.MagicMock(return_value=['one', 'two'])
    fail_status_mock = mock.MagicMock(return_value=['one', 'two', 'three'])
    dgm.get_device_info = device_info_mock
    dgm._get_devices_by_activation_state = act_state_mock
    dgm._get_devices_by_failover_status = fail_status_mock
    return dgm, root_device, devices


@pytest.fixture
def DGMSyncOnly():
    root_device = mock.MagicMock()
    devices = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
    dgm = DeviceGroupManager(
        'dg_name', root_device, devices, 'part', 'sync-only')
    device_info_mock = mock.MagicMock(return_value=FakeDeviceInfo())
    dgm.get_device_info = device_info_mock
    return dgm, root_device, devices


def test___init__(DGMSyncOnly):
    dgm, root_device, devices = DGMSyncOnly
    assert dgm.device_group_name == 'dg_name'
    assert dgm.partition == 'part'
    assert dgm.root_device == root_device
    assert dgm.devices == devices
    assert dgm.device_group_type == 'sync-only'


def test_create_device_group(DGMSyncFailover):
    dgm, root_device, devices = DGMSyncFailover
    with mock.patch(CLASS_LOC + '._check_all_devices_in_sync'):
        dgm.create_device_group()
        assert dgm.root_device.tm.cm.device_groups.device_group.create.\
            call_args == mock.call(
                name='dg_name', partition='part', type='sync-failover')


def test_scale_up_device_group(DGMSyncFailover):
    new_device = mock.MagicMock()
    dgm, root_device, devices = DGMSyncFailover
    # After cluster has been scaled up, ensure one more device in in
    # standby state
    dgm._get_devices_by_activation_state = mock.MagicMock(
        return_value=['one', 'two', 'three'])
    # And ensure all new devices in sync
    dgm._get_devices_by_failover_status = mock.MagicMock(
        return_value=['one', 'two', 'three', 'four'])
    dgm.scale_up_device_group(new_device)
