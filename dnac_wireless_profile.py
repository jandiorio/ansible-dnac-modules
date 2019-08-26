#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_wireless_profile.py
        
'''

EXAMPLES = r'''

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

def main():
    _profile_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        state=dict(type='str', choices=['absent','present']),
        name=dict(type='str', required=True), 
        sites=dict(type='list', required=False), 
        ssid_name=dict(type='str', required=False),
        ssid_type=dict(type='str',required=False, default='Enterprise',
                        choices=['Guest','Enterprise']), 
        fabric_enabled=dict(type='bool',required=False, default=False),
        flexconnect=dict(type='bool',required=False, default=False),
        flexconnect_vlan=dict(type='str',required=False), 
        interface=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        original_message='',
        message='', 
        orig_config='',
        proposed_config='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    # build the required payload data structure
    payload = {
        "profileDetails": {
            "name": module.params['name'],
            "sites": module.params['sites'], 
        }
    }
    # If ssid information is provided add to the payload 
    if module.params['ssid_name'] and module.params['ssid_type']:
        payload['profileDetails'].update(
            {"ssidDetails":[
                {
                    "name": module.params['ssid_name'],
                    "type": module.params['ssid_type'],
                    "enableFabric": module.params['fabric_enabled'],
                }
            ]
            }
        )
        if module.params['interface']: 
            payload.update(
                {"interfaceName": module.params['interface']}
            )
        #  If Flexconnect is in play, add flexconnect variables
        if module.params['flexconnect']:
            flexconnect =  {"flexConnect": {
                                "enableFlexConnect": module.params['flexconnect'], 
                                "localToVlan": module.params['flexconnect_vlan']
            }}
        else:
            flexconnect =  {"flexConnect": {
                                "enableFlexConnect": module.params['flexconnect'] }}

        
        payload['profileDetails']['ssidDetails'][0].update(flexconnect)
    

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)
    dnac.api_path = 'dna/intent/api/v1/wireless/profile'
    
    dnac.result = result
    # check if the configuration is already in the desired state

    #  get the SSIDs
    profiles = dnac.get_obj()
    
    result['orig_config'] = [profile for profile in profiles if profile['profileDetails']['name'] == module.params['name']]
    result['proposed_config'] = payload

    if len(profiles) > 0:
        _profile_names = [ profile['profileDetails']['name'] for profile in profiles ]
    else: 
        _profile_names = []

    # does pool provided exist
    if module.params['name'] in _profile_names:
        _profile_exists = True
    else:
        _profile_exists = False
    
    # actions
    if module.params['state'] == 'present' and _profile_exists:
        orig_config = dnac.result['orig_config']
        proposed_config = dnac.result['proposed_config']
        
        if len(orig_config) > 0:
            del(orig_config[0]['profileDetails']['instanceUuid'])
            if orig_config == proposed_config:    
                result['changed'] = False
                module.exit_json(msg='Wireless Profile already exists.', **result)
            else:
                dnac.update_obj(proposed_config)
                dnac.result['changed'] = True
                module.exit_json(msg='Updated Wireless Profile.', **dnac.result)
        else:
            dnac.result['changed'] = True
            dnac.update_obj(proposed_config)

        # result['changed'] = False
        # module.exit_json(msg='Wireless Profile already exists.', **result)

    elif module.params['state'] == 'present' and not _profile_exists:
        dnac.create_obj(payload)
    elif module.params['state'] == 'absent' and _profile_exists:
        # Create payload of existing profile
        payload = [profile for profile in profiles if profile['profileDetails']['name'] == module.params['name']]
        # Remove Site Assignment
        payload[0]['profileDetails']['sites'] = []
        dnac.update_obj(payload[0])
        # Delete the Wireless Profile
        dnac.delete_obj(module.params['name'])

    elif module.params['state'] == 'absent' and not _profile_exists:
        result['changed'] = False
        module.exit_json(msg='Wireless Profile Does not exist.  Cannot delete.', **result)

if __name__ == "__main__":
    main()