#!/usr/local/python
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''

module: dnac_discovery
short_description: Create network discovery jobs. 
description:
    - Create network discovery jobs to populate the DNA Center Inventory Database. 

version_added: "2.5"
author: "Jeff Andiorio (@jandiorio)"

options:
    host: 
        description: 
            - Host is the target Cisco DNA Center controller to execute against. 
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    port: 
        description: 
            - Port is the TCP port for the HTTP connection. 
        required: true
        default: 443
        choices: 
            - 80
            - 443
        aliases: null
        version_added: "2.5"
    username: 
        description: 
            - Provide the username for the connection to the Cisco DNA Center Controller.
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"        
    password: 
        description: 
            - Provide the password for connection to the Cisco DNA Center Controller.
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    use_proxy: 
        description: 
            - Enter a boolean value for whether to use proxy or not.  
        required: false
        default: true
        choices:
            - true
            - false
        aliases: null
        version_added: "2.5"
    use_ssl: 
        description: 
            - Enter the boolean value for whether to use SSL or not.
        required: false
        default: true
        choices: 
            - true
            - false
        aliases: null
        version_added: "2.5"
    timeout: 
        description: 
            - The timeout provides a value for how long to wait for the executed command complete.
        required: false
        default: 30
        choices: null
        aliases: null
        version_added: "2.5"
    validate_certs: 
        description: 
            - Specify if verifying the certificate is desired.
        required: false
        default: true
        choices: 
            - true
            - false
        aliases: null
        version_added: "2.5"
    state: 
        description: 
            - State provides the action to be executed using the terms present, absent, etc.
        required: true
        default: present
        choices: 
            - present
            - absent
        aliases: null
        version_added: "2.5"

    dhcp_server: 
        description: 
            - IP address of the DHCP Server to manipulate.
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    group_name: 
        description: 
            - group_name is the name of the group in the hierarchy where you would like to apply the dhcp_server. 
        required: false
        default: Global
        choices: null
        aliases: null
        version_added: "2.5"
notes: 
    - null
requirements:
    - geopy
    - TimezoneFinder
    - requests 

'''

EXAMPLES = '''

- name: create dhcp server 
  dnac_dhcp:
    host: 10.253.177.230
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: present
    dhcp_server: 192.168.200.1 192.168.200.2

- name: delete dhcp server 
  dnac_dhcp:
    host: 10.253.177.230
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: absent
    dhcp_server: 192.168.200.1 192.168.200.2

'''

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_discovery.py
short_description: Manage discovery jobs within Cisco DNA Center
description:  Based on 1.1+ version of DNAC API
author:
- Jeff Andiorio (@jandiorio)
version_added: '2.4'
requirements:
- DNA Center 1.1+

'''

EXAMPLES = r'''

!!! NEED SAMPLE  !!!

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dnac import DnaCenter,dnac_argument_spec

def main():
    _discovery_exists = False
    payload = ''
    module_args = dnac_argument_spec
    module_args.update(
        # api_path=dict(type='str',default='api/v1/discovery'),
        # state=dict(type='str', default='present', choices=['absent', 'present', 'update']),
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
        create_discovery_results = dnac.create_obj(payload)
        if not create_discovery_results.get('isError'):
            result['changed'] = True
            result['original_message'] = create_discovery_results
            module.exit_json(msg='Discovery Created Successfully.', **result)
        elif create_discovery_results.get('isError'):
            result['changed'] = False
            result['original_message'] = create_discovery_results
            module.fail_json(msg='Failed to create discovery!', **result)
    elif module.params['state'] == 'absent' and _discovery_exists:
        _discovery_id = [discovery['id'] for discovery in discoveries['response'] if discovery['name'] == module.params['discovery_name']]
        delete_discovery_results = dnac.delete_obj(_discovery_id[0])

        if not delete_discovery_results.get('isError'):
            result['changed'] = True
            result['original_message'] =  delete_discovery_results
            module.exit_json(msg='Discovery Deleted Successfully.', **result)
        elif  delete_discovery_results.get('isError') == True:
            result['changed'] = False
            result['original_message'] =  delete_discovery_results
            module.fail_json(msg='Failed to delete discovery!', **result)
    elif module.params['state'] == 'absent' and not _discovery_exists:
        result['changed'] = False
        module.exit_json(msg='Discovery Does not exist.  Cannot delete.', **result)


main()

if __name__ == "__main__":
  main()