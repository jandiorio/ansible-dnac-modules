#!/usr/bin/env python

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

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

---

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
previous:
  description:  Configuration from DNA Center prior to any changes. 
  returned: success
  type: list
  sample: 
    - groupUuid: '-1'
      inheritedGroupName: ''
      inheritedGroupUuid: ''
      instanceType: ip
      instanceUuid: 1ca3a703-4720-472d-9314-ba1fbe48e139
      key: syslog.server
      namespace: global
      type: ip.address
      value:
      - 192.168.200.1
      version: 32
proposed: 
  description:  Configuration to be sent to DNA Center.
  returned: success
  type: list
  sample: 
    - groupUuid: '-1'
      instanceType: ip
      key: syslog.server
      namespace: global
      type: ip.address
      value:
      - 192.168.200.1
      - 192.168.200.2
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
        group_name=dict(type='str',default='-1'),
        syslog_servers=dict(type='list', required=False, default='')
        )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
        )

    #  Define Local Variables 
    state = module.params['state']
    group_name = module.params['group_name']
    syslog_servers = module.params['syslog_servers']

    #  Build the payload dictionary
    payload = [
        {
          "instanceType":"ip",
          "namespace":"global",
          "type": "ip.address",
          "key":"syslog.server",
          "value": syslog_servers,
          "groupUuid":"-1",
        }
      ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)
    
    # Set API Path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + '?key=syslog.server'
    
    dnac.process_common_settings(payload, group_id)

if __name__ == "__main__":
  main()
