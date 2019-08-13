#!/usr/bin/env python
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---

module: dnac_discovery
short_description: Create network discovery jobs. 
description: Create network discovery jobs to populate the DNA Center Inventory Database. 

version_added: "2.5"
author: 
  - Jeff Andiorio (@jandiorio)

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
  
  discovery_name:
    description:  
      - A name for the discovery.
    required: true 
    alias: name
    type: string
  discovery_type:
    description: 
      - Type of Discovery.  Either Range or CDP.
    type: string
    choices:
      - Range
      - CDP
    required: true
  discovery_cdp_level:
    description: 
      - If type is CDP, a cdp level of depth is needed.  This is how many hops away from the seed device.
    alias: cdp_level
    type: string
    required: false
  discovery_preferred_ip_method:
    description:  
      - Specify to use the Loopback for management or not. 
    alias: preferred_ip_method
    type: string
    choices: 
      - None
      - UseLoopBack
    required: false

  discovery_ip_filter_list:
    description: 
      - A string of IP addresses to exclude from the discovery.  (Example 192.168.200.1-192.168.200.100)
    type: string
    required: false 

  discovery_ip_address_list:
    description: 
      - A string of IP addresses to include in the discovery.  (Example 192.168.200.101-192.168.200.200)
    type: string
    required: false 

  global_cli_cred:
    description:  
      - The CLI Username to utilize during discovery. 
    type: string
    required: true

  global_snmp_cred:
    description:  
      - The SNMP credential to use for discovery. 
    type: string
    required: true

'''

EXAMPLES = r'''

---

- name: create discovery
  dnac_discovery:
    host: "{{host}}"
    port: "{{port}}"
    username: "{{username}}"
    password: "{{password}}"
    state: present
    discovery_name: test-1
    discovery_type: Range
    discovery_preferred_ip_method: UseLoopBack
    discovery_ip_addr_list: 192.168.90.50-192.168.90.50
    global_cli_cred: wwt
    global_snmp_cred: SNMP-RW

'''

RETURN = r'''

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

def main():
    _discovery_exists = False
    payload = ''
    module_args = dnac_argument_spec
    module_args.update(

        discovery_name=dict(alias='name',type='str', required=True),
        discovery_type=dict(type='str',required=True, choices=['CDP','Range']),
        discovery_cdp_level=dict(alias='cdp_level',type='str',required=False),
        discovery_preferred_ip_method=dict(alias='preferred_ip_method',type='str',required=False,default='None', choices=['None','UseLoopBack']),
        discovery_ip_filter_list=dict(type='str',required=False),
        discovery_ip_addr_list=dict(type='str',required=True),
        global_cli_cred=dict(type='str', required=True),
        global_snmp_cred=dict(type='str',required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)


    # build the required payload data structure

    # lookup global credentials.
    dnac.api_path = 'api/v1/global-credential?credentialSubType=CLI'
    cli_cred = dnac.get_obj()
    for cli in cli_cred['response']:
        if cli['username'] == module.params['global_cli_cred']:
            cli_id = cli['id']

    dnac.api_path = 'api/v1/global-credential?credentialSubType=SNMPV2_WRITE_COMMUNITY'
    snmp_cred = dnac.get_obj()
    for snmp in snmp_cred['response']:
        if snmp['description'] == module.params['global_snmp_cred']:
            snmp_id = snmp['id']

    payload = {
        "preferredMgmtIPMethod": module.params['discovery_preferred_ip_method'],
        "name":  module.params['discovery_name'],
        "cdpLevel": module.params['discovery_cdp_level'],
        "globalCredentialIdList": [
            cli_id,
            snmp_id
        ],
        "ipFilterList": module.params['discovery_ip_filter_list'],
        "ipAddressList": module.params['discovery_ip_addr_list'],
        "discoveryType": module.params['discovery_type'],
        "protocolOrder": "ssh",
        "retry": 3,
        "timeout": 5,
        "lldpLevel":"16",

        }

    '''
    {
  "preferredMgmtIPMethod": module.params['discovery_preferred_ip_method'],
  "name":  module.params['discovery_name'],
  "snmpROCommunityDesc": "",
  "snmpRWCommunityDesc": "",
  "parentDiscoveryId": "",
  "globalCredentialIdList": [
    ""
  ],
  "httpReadCredential": {
    "port": 0,
    "password": "",
    "username": "",
    "secure": false,
    "description": "",
    "credentialType": "",
    "comments": "",
    "instanceUuid": "",
    "id": ""
  },
  "httpWriteCredential": {
    "port": 0,
    "password": "",
    "username": "",
    "secure": false,
    "description": "",
    "credentialType": "",
    "comments": "",
    "instanceUuid": "",
    "id": ""
  },
  "snmpUserName": "",
  "snmpMode": "",
  "netconfPort": "",
  "cdpLevel": 0,
  "enablePasswordList": [
    ""
  ],
  "ipFilterList": [
    ""
  ],
  "passwordList": [
    ""
  ],
  "protocolOrder": "",
  "reDiscovery": false,
  "retry": 0,
  "snmpAuthPassphrase": "",
  "snmpAuthProtocol": "",
  "snmpPrivPassphrase": "",
  "snmpPrivProtocol": "",
  "snmpROCommunity": "",
  "snmpRWCommunity": "",
  "userNameList": [
    ""
  ],
  "ipAddressList": "",
  "snmpVersion": "",
  "timeout": 0,
  "discoveryType": ""
}
    '''

    #  Get the discoveries
    dnac.api_path = 'api/v1/discovery'
    discoveries = dnac.get_obj()

    _discovery_names = [discovery['name'] for discovery in discoveries['response']]

    # does discovery provided exist
    if module.params['discovery_name'] in _discovery_names:
        _discovery_exists = True
    else:
        _discovery_exists = False

    # actions
    if module.params['state'] == 'present' and _discovery_exists:
        result['changed'] = False
        module.exit_json(msg='Discovery already exists.', **result)
    elif module.params['state'] == 'present' and not _discovery_exists:
        dnac.create_obj(payload)

    elif module.params['state'] == 'absent' and _discovery_exists:
        _discovery_id = [discovery['id'] for discovery in discoveries['response'] if discovery['name'] == module.params['discovery_name']]
        dnac.delete_obj(_discovery_id[0])

    elif module.params['state'] == 'absent' and not _discovery_exists:
        result['changed'] = False
        module.exit_json(msg='Discovery Does not exist.  Cannot delete.', **result)

if __name__ == "__main__":
  main()
