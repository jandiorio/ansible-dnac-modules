#!/usr/bin/env python

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status' : ['development'],
    'supported_by' : 'jandiorio'
}


DOCUMENTATION = r'''
---
module: dnac_snmp.py
short_description: Manage SNMP server(s) within Cisco DNA Center
description:  Manage SNMP Server(s) settings in Cisco DNA Center.  Based on 1.1+ version of DNAC API
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

  snmp_servers:
    description:
      - The ip address(es) of the snmp server(s).
    required: false
    type: list
  group_name:
    description:
      - Name of the group where the setting will be applied.  
    required: false
    default: Global
    type: string  
'''
EXAMPLES = r'''


- name: create snmp server 
    dnac_snmp:
        host: "{{host}}"
        port: "{{port}}"
        username: "{{username}}"
        password: "{{password}}"
        state: present
        snmp_servers: [192.168.200.1, 192.168.200.2]
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
      instanceUuid: beebe744-8a95-4688-b396-b33ce952e458
      key: snmp.trap.receiver
      namespace: global
      type: ip.address
      value:
      - 192.168.200.1
      - 192.168.200.2
      version: 67
proprosed:
  description:  Configuration to be sent to DNA Center.
  returned: success
  type: list
  sample:
    - groupUuid: '-1'
      instanceType: ip
      key: snmp.trap.receiver
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
        group_name=dict(type='str',default='-1', required=False),
        snmp_servers=dict(type='list', required=False)
        )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
        )
    #  Set Local Variables
    state = module.params['state']
    snmp_servers = module.params['snmp_servers']
    group_name = module.params['group_name']

    #  Build the payload dictionary
    payload = [
        {"instanceType":"ip",
        "namespace":"global",
        "type": "ip.address",
        "key":"snmp.trap.receiver",
        "value": snmp_servers,
        "groupUuid":"-1",
        }
    ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)

    # Set the api path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + '?key=snmp.trap.receiver'

    # Process Setting Changes
    dnac.process_common_settings(payload, group_id)

if __name__ == "__main__":
  main()
