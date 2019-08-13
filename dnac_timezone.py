#!/usr/bin/env python

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status' : ['preview'],
    'supported_by' : 'community'
}


DOCUMENTATION = r'''
---
module: dnac_timezone
short_description: Manage Timezone Settings within Cisco DNA Center
description:  Manage Timezone Settings in Cisco DNA Center.  Based on 1.1+ version of DNAC API
author:
  - Jeff Andiorio (@jandiorio)
version_added: '2.5'
requirements:
  - DNA Center 1.1+

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
  timezone:
    description:
      - "The timezone string matching the timezone you are targeting. example: America/Chicago"
    required: false
    type: string
    version_added: "2.5"
  group_name:
    description:
      - Name of the group where the setting will be applied.  
    required: false
    default: Global
    type: string
  location: 
    description:
      - address of a location in the timezone. A lookup will be performed to resolve the timezone.
    required: false
    type: string  

'''

EXAMPLES = r'''

---

- name: create timezone 
  dnac_timezone:
    host: "{{host}}"
    port: "{{port}}"
    username: "{{username}}"
    password: "{{password}}"
    state: present
    location: 56 weldon parkway, maryland heights, mo

- name: create timezone 
  dnac_timezone:
    host: "{{host}}"
    port: "{{port}}"
    username: "{{username}}"
    password: "{{password}}"
    state: present
    timezone: "America/Chicago"
    
'''

RETURN = r'''

'''

from ansible.module_utils.basic import AnsibleModule
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
        timezone=dict(type='str', default='GMT'),
        group_name=dict(type='str', default='-1'),
        location=dict(type='str')
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
        {"instanceType":"timezone",
        "instanceUuid": "",
        "namespace":"global",
        "type": "timezone.setting",
        "key":"timezone.site",
        "value":[
            ""
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
        module.fail_json(msg='Failed to create timezone! Unable to locate group provided.', **result)

    # update payload with timezone
    if module.params['location']:
        timezone = dnac.timezone_lookup(module.params['location'])
    else:
        timezone = module.params['timezone']

    payload[0].update({'value': [timezone]})

    # # check if the configuration is already in the desired state
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id
    settings = dnac.get_obj()
    
    # parse resultset for only setting desired
    timezone_setting = [setting for setting in settings['response'] if setting['key'] == 'timezone.site']
    timezone_setting = timezone_setting[0]
    
    if len(timezone_setting['value']) > 0:
        _setting_exists = True
        if timezone_setting['value'] != payload[0]['value']:
            dnac.create_obj(payload)
        else:
            result['changed'] = False
            result['msg'] = 'Already in desired state.'
            module.exit_json(**result)
    else:
        dnac.create_obj(payload)

if __name__ == "__main__":
  main()
