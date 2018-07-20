#/usr/bin/env python3

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status' : ['development'],
    'supported_by' : 'jandiorio'
}


DOCUMENTATION = r'''
---
module: dnac_syslog.py
short_description: Manage Syslog server(s) within Cisco DNA Center
description:  Manage Syslog Server(s) settings in Cisco DNA Center.  Based on 1.1+ version of DNAC API
author:
- Jeff Andiorio (@jandiorio)
version_added: '2.4'
requirements:
- DNA Center 1.1+

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
      version_added: "2.5  
  syslog_servers:
      description: The ip address(es) of the syslog server(s).
      required: true
      type: list
  group_name:
      description: Name of the group where the setting will be applied.  
      required: false
      default: Global
      type: string  
'''
EXAMPLES = r'''


- name: create syslog server 
    dnac_syslog:
        host: "{{host}}"
        port: "{{port}}"
        username: "{{username}}"
        password: "{{password}}"
        state: present
        syslog_servers: [192.168.200.1, 192.168.200.2]
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac import DnaCenter,dnac_argument_spec

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
        group_name=dict(type='str',default='-1'),
        syslog_servers=dict(type='list', required=True)
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
        "key":"syslog.server",
        "value":[
                 ],
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
        module.fail_json(msg='Failed to create syslog server! Unable to locate group provided.', **result)

    # Support multiple syslog servers
    _syslog_servers = module.params['syslog_servers']
    payload[0].update({'value': _syslog_servers})

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

    if not _setting_exists:
        dnac.create_obj(payload)

if __name__ == "__main__":
  main()
