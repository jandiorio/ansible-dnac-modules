#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_wireless_ssid.py
short_description: Manage SSID
description: manage the create/update/delete of SSIDs in DNAC
version_added: "2.8"
author:
  - Jeff Andiorio (@jandiorio)

requirements:
  - requests

options:
  host:
    description:
      - Host is the target Cisco DNA Center controller to execute against.
    required: true

  port:
    description:
      - Port is the TCP port for the HTTP connection.
    required: false
    default: 443
    choices:
      - 80
      - 443

  username:
    description:
      - Provide the username for the connection to the Cisco DNA Center Controller.
    required: true

  password:
    description:
      - Provide the password for connection to the Cisco DNA Center Controller.
    required: true

  use_proxy:
    description:
      - Enter a boolean value for whether to use proxy or not.
    required: false
    default: true
    choices:
      - true
      - false

  use_ssl:
    description:
      - Enter the boolean value for whether to use SSL or not.
    required: false
    default: true
    choices:
      - true
      - false

  timeout:
    description:
      - The timeout provides a value for how long to wait for the executed command complete.
    required: false
    default: 30

  validate_certs:
    description:
      - Specify if verifying the certificate is desired.
    required: false
    default: true
    choices:
      - true
      - false

  state:
    description:
      - State provides the action to be executed using the terms present, absent, etc.
    required: false
    default: present
    choices:
      - present
      - absent

  name:
    description:
      - Name of the wireless SSID
    required: true

  security_level:
    description:
      - security level for the SSID
    required: true
    choices:
      - WPA2_ENTERPRISE
      - WPA2_PERSONAL
      - OPEN

  passphrase:
    description:
      - secret passphrase for WPA2_PERSONAL
    required: false

  enable_fastlane:
    description:
      - boolean to enable fastlane
    required: false
    default: false

  enable_mac_filtering:
    description:
      - boolean for enableing MAC filtering
    required: false
    default: false

  traffic_type:
    description:
      - type of traffic for SSID
    required: false
    choices:
      - voicedata
      - data
    default: voicedata

  radio_policy:
    description:
      - SSID radio policy to associate
    required: false
    choices:
      - 'Dual band operation (2.4GHz and 5GHz)'
      - 'Dual band operation with band select'
      - '5GHz only'
      - '2.4GHz only'

  enable_broadcast_ssid:
    description:
      - boolean for SSID broadcast
    required: false
    default: true

  fast_transition:
    description:
      - configuration of fast transition
    required: false
    choices:
      - 'Adaptive'
      - 'Enable'
      - 'Disable'
    default: 'Disable'

'''

EXAMPLES = r'''

- name: build wireless ssid
  dnac_wireless_ssid:
    host: "{{ inventory_hostname }}"
    port: '443'
    username: "{{ username }}"
    password: "{{ password }}"
    state: present
    #
    name: 'SSID-1'
    security_level: 'WPA2_PERSONAL'
    passphrase: SUPERSECRET

'''


RETURN = r'''
    #
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.wwt.ansible_dnac.plugins.module_utils.network.dnac.dnac import DnaCenter, dnac_argument_spec


def main():
    _ssid_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        state=dict(type='str', choices=['absent', 'present']),
        name=dict(type='str', required=True),
        security_level=dict(type='str', required=True, choices=['WPA2_ENTERPRISE', 'WPA2_PERSONAL', 'OPEN']),
        passphrase=dict(type='str', required=False, no_log=True),
        enable_fastlane=dict(type='bool', required=False, default=False),
        enable_mac_filtering=dict(type='bool', required=False, default=False),
        traffic_type=dict(type='str', required=False, choices=['voicedata', 'data'], default='voicedata'),
        radio_policy=dict(type='str', required=False,
                          choices=['Dual band operation (2.4GHz and 5GHz)',
                                   'Dual band operation with band select',
                                   '5GHz only',
                                   '2.4GHz only)'],
                          default='Dual band operation (2.4GHz and 5GHz)'),
        enable_broadcast_ssid=dict(type=bool, required=False, default=True),
        fast_transition=dict(type='str', required=False, choices=['Adaptive', 'Enable', 'Disable'], default='Disable')

    )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # build the required payload data structure
    payload = {
        "name": module.params['name'],
        "securityLevel": module.params['security_level'],
        "passphrase": module.params['passphrase'],
        "enableFastLane": module.params['enable_fastlane'],
        "enableMACFiltering": module.params['enable_mac_filtering'],
        "trafficType": module.params['traffic_type'],
        "radioPolicy": module.params['radio_policy'],
        "enableBroadcastSSID": module.params['enable_broadcast_ssid'],
        "fastTransition": module.params['fast_transition']
    }

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)
    dnac.api_path = 'dna/intent/api/v1/enterprise-ssid'

    # check if the configuration is already in the desired state

    #  get the SSIDs
    ssids = dnac.get_obj()

    _ssid_names = [ssid['ssidDetails'][0]['name'] for ssid in ssids]

    # does pool provided exist
    if module.params['name'] in _ssid_names:
        _ssid_exists = True
    else:
        _ssid_exists = False

    dnac.api_path = 'dna/intent/api/v1/enterprise-ssid'

    # actions
    if module.params['state'] == 'present' and _ssid_exists:
        result['changed'] = False
        module.exit_json(msg='SSID already exists.', **result)
    elif module.params['state'] == 'present' and not _ssid_exists:
        dnac.create_obj(payload)
    elif module.params['state'] == 'absent' and _ssid_exists:
        # _ssid_id = [ssid['instanceUuid'] for ssid in ssids if ssid['ssidDetails'][0]['name'] == module.params['name']]
        # dnac.delete_obj(_ssid_id[0])
        dnac.delete_obj(module.params['name'])
    elif module.params['state'] == 'absent' and not _ssid_exists:
        result['changed'] = False
        module.exit_json(msg='SSID Does not exist.  Cannot delete.', **result)


if __name__ == "__main__":
    main()
