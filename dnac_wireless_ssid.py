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
        
'''

EXAMPLES = r'''

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

def main():
    _ssid_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        state=dict(type='str', choices=['absent','present']),
        name=dict(type='str', required=True), 
        security_level=dict(type='str', required=True, choices=['WPA2_ENTERPRISE', 'WPA2_PERSONAL', 'OPEN']),
        passphrase=dict(type='str', required=False, no_log=True),
        enable_fastlane=dict(type='bool', required=False, default=False),
        enable_mac_filtering=dict(type='bool', required=False, default=False),
        traffic_type=dict(type='str', required=False, choices=['voicedata','data'], default='voicedata'),
        radio_policy=dict(type='str', required=False, 
                          choices=['Dual band operation (2.4GHz and 5GHz)', 'Dual band operation with band select', '5GHz only', '2.4GHz only)'],
                          default='Dual band operation (2.4GHz and 5GHz)'),
        enable_broadcast_ssid=dict(type=bool, required=False, default=True), 
        fast_transition=dict(type='str', required=False, choices=[ 'Adaptive', 'Enable', 'Disable'], default='Disable')
        
    )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
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
    dnac.api_path= 'dna/intent/api/v1/enterprise-ssid'

    # check if the configuration is already in the desired state

    #  get the SSIDs
    ssids = dnac.get_obj()
    
    _ssid_names = [ssid['ssidDetails'][0]['name'] for ssid in ssids]

    # does pool provided exist
    if module.params['name'] in _ssid_names:
        _ssid_exists = True
    else:
        _ssid_exists = False
    
    dnac.api_path= 'dna/intent/api/v1/enterprise-ssid'
    
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
