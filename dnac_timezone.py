#!/usr/bin/env python

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

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

  timezone:
    description:
      - "The timezone string matching the timezone you are targeting. example: America/Chicago"
    required: false
    type: string

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
previous:
  description:  Configuration from DNA Center prior to any changes. 
  returned: success
  type: list
  sample:
    - groupUuid: 91404471-9c8d-492c-9c4c-230c7fd54bf9
      inheritedGroupName: ''
      inheritedGroupUuid: ''
      instanceType: timezone
      instanceUuid: cae8ced9-eab7-4dae-b1b9-1bd300a58311
      key: timezone.site
      namespace: global
      type: timezone.setting
      value: []
      version: 2
proprosed:
  description:  Configuration to be sent to DNA Center.
  returned: success
  type: list
  sample:
    - groupUuid: 91404471-9c8d-492c-9c4c-230c7fd54bf9
      instanceType: timezone
      instanceUuid: ''
      key: timezone.site
      namespace: global
      type: timezone.setting
      value:
      - America/Chicago
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
    module_args = dnac_argument_spec
    module_args.update(
        timezone=dict(type='str', default='GMT'),
        group_name=dict(type='str', default='-1'),
        location=dict(type='str')
        )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
        )

    #  set local variables 
    state = module.params['state']
    group_name = module.params['group_name']
    location = module.params['location']
    timezone = module.params['timezone']

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
        "groupUuid":"-1"
        }
        ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)

    # update payload with timezone
    if location:
        timezone = dnac.timezone_lookup(location)

    payload[0].update({'value': [timezone]})

    # # check if the configuration is already in the desired state
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + '?key=timezone.site'
    
    # process common settings
    dnac.process_common_settings(payload, group_id)

if __name__ == "__main__":
  main()
