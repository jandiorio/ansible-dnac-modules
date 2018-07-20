#/usr/bin/env python3
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''

module: dnac_dhcp
short_description: Add or Delete DHCP Server(s) 
description:
    - Add or delete DHCP Server(s) in the Cisco DNA Center Design Workflow.  The DHCP Severs can be different values \ 
    at different levels in the group hierarchy.

version_added: "2.5"
author: "Jeff Andiorio (@jandiorio)"

options:
  host: 
    description: 
    - Host is the target Cisco DNA Center controller to execute against. 
    required: true
    version_added: "2.5"
  port: 
      description: 
          - Port is the TCP port for the HTTP connection. 
      required: false
      default: 443
      choices: 
          - 80
          - 443
      version_added: "2.5"
  username: 
      description: 
          - Provide the username for the connection to the Cisco DNA Center Controller.
      required: true
      version_added: "2.5"        
  password: 
      description: 
          - Provide the password for connection to the Cisco DNA Center Controller.
      required: true
      version_added: "2.5"
  use_proxy: 
      description: 
          - Enter a boolean value for whether to use proxy or not.  
      required: false
      default: true
      choices:
          - true
          - false
      version_added: "2.5"
  use_ssl: 
      description: 
          - Enter the boolean value for whether to use SSL or not.
      required: false
      default: true
      choices: 
          - true
          - false
      version_added: "2.5"
  timeout: 
      description: 
          - The timeout provides a value for how long to wait for the executed command complete.
      required: false
      default: 30
      version_added: "2.5"
  validate_certs: 
      description: 
          - Specify if verifying the certificate is desired.
      required: false
      default: true
      choices: 
          - true
          - false
      version_added: "2.5"
  state: 
      description: 
          - State provides the action to be executed using the terms present, absent, etc.
      required: false
      default: present
      choices: 
          - present
          - absent
      version_added: "2.5"
    dhcp_servers: 
        description: 
            - IP address of the DHCP Server to manipulate.
        required: true
        version_added: "2.5"
        type: list
    group_name: 
        description: 
            - group_name is the name of the group in the hierarchy where you would like to apply the dhcp_server. 
        required: false
        default: Global
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac import DnaCenter,dnac_argument_spec

# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _setting_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        dhcp_servers=dict(type='list', required=True),
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
        {"instanceType":"ip",
        "instanceUuid": "",
        "namespace":"global",
        "type": "ip.address",
        "key":"dhcp.server",
        "value": "",
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
        module.fail_json(msg='Failed to create DHCP server! Unable to locate group provided.', **result)

    # Support multiple DHCP servers
    _dhcp_servers = module.params['dhcp_servers']
    payload[0].update({'value': _dhcp_servers})

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
