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
short_description: Provision WLC
description: Provision the wireless LAN controller(s)
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
      - Name of the wireless LAN controller as it appears in DNA Center
    required: true
    
  site: 
    description: 
      - site hierarchy path to associate the device to ('Global/Central/Maryland Heights/ATC56')
    required: false
  
  managed_ap_locations: 
    description: 
      - list of site hierarchy path of the locations of managed access points
    required: false
                            
  interface_ip: 
    description: 
      - name of the wireless management interface
    required: false
    default: 1.1.1.1


  interface_prefix_length:
    description: prefix length for netmask
    required: false
    default: 24
  
  interface_gateway: 
    description: 
      - default_gateway for the management interface
    required: false
    default: 1.1.1.2

  vlan: 
    description: 
      - vlan number for flexconnect
    required: false
  
  interface:
    description: 
      - interface for wireless management
    required: false
  
  reprovision: 
    description: 
      - bool for if this is a reprovision (false = initial provision)
      
'''

EXAMPLES = r'''
- name: provision wireless
    dnac_wireless_provision:
      host: "{{ inventory_hostname }}"
      port: '443'
      username: "{{ username }}"
      password: "{{ password }}"
      state: present
      #
      name: 'dna-3-wlc'
      site: 'Global/Central/Maryland Heights/ATC56'
      managed_ap_locations: 
        - 'Global/Central/Maryland Heights/ATC56'
        - 'Global/Central/Maryland Heights/ATC56/floor_1'
      vlan: 30
      interface: vlan_30
      reprovision: yes    

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
        interface_ip=dict(type='str', required=False, default='1.1.1.1'),
        interface_prefix_length=dict(type='str', required=False, default='24'),
        interface_gateway=dict(type='str', required=False, default='1.1.1.2'), 
        lag_or_port_number=dict(type='str', required=False), 
        vlan=dict(type='str', required=False), 
        interface=dict(type='str', required=False), 
        reprovision=dict(type='bool', required=False, default=False)
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
        "managedAPLocations": module.params['managed_ap_locations']
        
        }
    ]

    if module.params['interface']:
        payload[0].update(
            {"dynamicInterfaces": [
                    {
                        "interfaceIPAddress": module.params['interface_ip'],
                        "interfaceNetmaskInCIDR": module.params['interface_prefix_length'],
                        "interfaceGateway": module.params['interface_gateway'],
                        "lagOrPortNumber":module.params['lag_or_port_number'],
                        "vlanId": module.params['vlan'],
                        "interfaceName": module.params['interface'],
                    }
                ]
            }
            )
    
    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)
    
    # Check if Device Has been Provisioned
    # dnac.api_path = 'dna/intent/api/v1/network-device?hostname=' + module.params['name']
    # device = dnac.get_obj()

    # if device['response']:
    #     if device['response'][0]['location'] == None:
    #         _PROVISIONED = False
    #     else: 
    #         _PROVISIONED = True
    # else:
    #     _PROVISIONED = False

    if module.params['reprovision']:
        _PROVISIONED = True
    else: 
        _PROVISIONED = False
    # Reset API Path
    dnac.api_path = 'dna/intent/api/v1/wireless/provision'
    
    # actions
    if module.params['state'] == 'present' and _PROVISIONED:
        # module.exit_json(msg=payload)
        dnac.update_obj(payload)
    elif module.params['state'] == 'present' and not _PROVISIONED:
        # module.exit_json(msg='provision')
        dnac.create_obj(payload)
        
if __name__ == "__main__":
    main()