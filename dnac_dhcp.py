#/usr/bin/env python3
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

module: dnac_dhcp
short_description: Add or Delete DHCP Server(s) 
description: Add or delete DHCP Server(s) in the Cisco DNA Center Design Workflow.  The DHCP Severs can be different values \ 
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
  
  dhcp_servers: 
    description: 
      - IP address of the DHCP Server to manipulate.
    required: true  
    type: list
  group_name: 
    description: 
      - group_name is the name of the group in the hierarchy where you would like to apply the dhcp_server. 
    required: false
    default: Global

'''

EXAMPLES = r'''

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
RETURN = r'''
previous:
  description:  Configuration from DNA Center prior to any changes. 
  returned: success
  type: list
  sample:
    - groupUuid: 91404471-9c8d-492c-9c4c-230c7fd54bf9
      inheritedGroupName: Global
      inheritedGroupUuid: '-1'
      instanceType: ip
      instanceUuid: d069b8ac-39c6-4379-98d9-ac198675c410
      key: dhcp.server
      namespace: global
      type: ip.address
      value:
      - 192.168.200.1
      - 192.168.200.2
      version: 48
proprosed:
  description:  Configuration to be sent to DNA Center.
  returned: success
  type: list
  sample:
    - groupUuid: 91404471-9c8d-492c-9c4c-230c7fd54bf9
      instanceType: ip
      key: dhcp.server
      namespace: global
      type: ip.address
      value:
      - 192.168.200.1
      - 192.168.200.2
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _setting_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        dhcp_servers=dict(type='list', required=False),
        group_name=dict(type='str', default='-1')
        )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
        )
    
    #  Define Local Variables 
    state = module.params['state']
    dhcp_servers = module.params['dhcp_servers']
    group_name = module.params['group_name']

    #  Build the payload dictionary
    payload = [
        {"instanceType":"ip",
        "namespace":"global",
        "type": "ip.address",
        "key":"dhcp.server",
        "value": dhcp_servers,
        "groupUuid":"-1"
        }
        ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)

    # Set the api_path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + '?key=dhcp.server'
    
    dnac.process_common_settings(payload, group_id)

if __name__ == "__main__":
    main()
