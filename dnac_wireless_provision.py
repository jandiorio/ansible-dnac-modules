#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_wireless_provision.py
        
'''

EXAMPLES = r'''

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

def main():

    module_args = dnac_argument_spec
    module_args.update(
        state=dict(type='str', choices=['present']),
        name=dict(type='str', required=True), 
        site=dict(type='str', required=False), 
        managed_ap_locations=dict(type='list', required=False),
        interface_ip=dict(type='str', required=False),
        interface_prefix_length=dict(type='str', required=False),
        interface_gateway=dict(type='str', required=False), 
        lag_or_port_number=dict(type='str', required=False), 
        vlan=dict(type='str', required=False), 
        interface=dict(type='str', required=False)
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
    payload = [
    {
        "deviceName": module.params['name'],
        "site": module.params['site'],
        "managedAPLocations": module.params['managed_ap_locations'],
        # "dynamicInterfaces": [
        #     {
        #         "interfaceIPAddress": module.params['interface_ip'],
        #         "interfaceNetmaskInCIDR": module.params['interface_prefix_length'],
        #         "interfaceGateway": module.params['interface_gateway'],
        #         "lagOrPortNumber":module.params['lag_or_port_number'],
        #         "vlanId": module.params['vlan'],
        #         "interfaceName": module.params['interface'],
        #     }
        # ]
    }
]

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)
    dnac.api_path = 'dna/intent/api/v1/wireless/provision'
    
    # actions
    if module.params['state'] == 'present':
        dnac.update_obj(payload)

if __name__ == "__main__":
    main()