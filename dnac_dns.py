#!/usr/bin/env python
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''

module: dnac_dns
short_description: Add or Delete DNS Server(s) 
description:  Add or delete DNS Server(s) in the Cisco DNA Center Design Workflow.  The DNS Severs can be different values \ 
    at different levels in the group hierarchy.

version_added: "2.5"
author: "Jeff Andiorio (@jandiorio)"

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
  
  primary_dns_server: 
    description: 
      - IP address of the primary DNS Server to manipulate.
    required: true
    
  secondary_dns_server: 
    description: 
      - IP address of the secondary DNS Server to manipulate.
    required: false
    
  domain_name: 
    description: 
      - DNS domain name of the environment within Cisco DNA Center
    required: true
                            
  group_name: 
    description: 
      - group_name is the name of the group in the hierarchy where you would like to apply these settings. 
    required: false
    default: Global

'''

EXAMPLES = '''

- name: create dns server 
  dnac_dns:
    host: 10.253.177.230
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: present
    primary_dns_server: 192.168.200.1
    secondary_dns_server: 192.168.200.2
    domain_name: campus.wwtatc.local


- name: delete dns server 
  dnac_dns:
    host: 10.253.177.230
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: absent
    primary_dns_server: 192.168.200.1
    secondary_dns_server: 192.168.200.2
    domain_name: campus.wwtatc.local

'''


from ansible.module_utils.basic import AnsibleModule
#import ansible.module_utils.network.dnac
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

# -----------------------------------------------
#  define static required variales
# -----------------------------------------------
# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _setting_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        primary_dns_server=dict(type='str', required=True),
        secondary_dns_server=dict(type='str', required=False),
        domain_name=dict(type='str', required=True),
        group_name=dict(type='str', default='-1')
        )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    #  Build the payload dictionary
    payload = [
        {"instanceType":"dns",
        "instanceUuid": "",
        "namespace":"global",
        "type": "dns.setting",
        "key":"dns.server",
        "value":[{
                 "domainName" : module.params['domain_name'],
                 "primaryIpAddress":module.params['primary_dns_server'],
                 "secondaryIpAddress":module.params['secondary_dns_server']
                 }],
        "groupUuid":"-1",
        "inheritedGroupUuid": "",
        "inheritedGroupName": ""
        }
        ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    if module.params['group_name'] == '-1':
        group_id = '-1'
    else:
        group_id = dnac.get_group_id(module.params['group_name'])

    if group_id:
        payload[0].update({'groupUuid': group_id})
    else:
        result['changed'] = False
        result['original_message'] = group_id
        module.fail_json(msg='Failed to create DNS server! Unable to locate group provided.', **result)

    # # check if the configuration is already in the desired state
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id
    settings = dnac.get_obj()

    for setting in settings['response']:
        if setting['key'] == payload[0]['key']:
            _setting_exists = True
            if setting['value'] != '':
                if setting['value'] != payload[0]['value']:
                    dnac.create_obj(payload)
                else:
                    result['changed'] = False
                    result['msg'] = 'Already in desired state.'
                    module.exit_json(**result)

    if _setting_exists == False:
        dnac.create_obj(payload)

if __name__ == "__main__":
  main()
