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
module: dnac_netflow.py
short_description: Manage netflow exporters within Cisco DNA Center
description:  Based on 1.1+ version of DNAC API
author:
- Jeff Andiorio (@jandiorio)
version_added: 'x.x'
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

  netflow_collector:
        description: The ip address of the netflow collector.
        required: false
        type: string
  netflow_port:
        description: The port used for the target netflow collector.
        type: string
        required: false
        type: string
  group_name:
        description: Name of the group where the setting will be applied.
        required: false
        default: Global
        type: string

'''
EXAMPLES = r'''
- name: create a netflow
      dnac_netflow:
        host: "{{host}}"
        port: "{{port}}"
        username: "{{username}}"
        password: "{{password}}"
        state: present
        netflow_collector: "{{nf_ip}}"
        netflow_port: "{{nf_port}}"
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
      instanceType: netflow
      instanceUuid: e1fae968-18e7-456a-98dd-06db3fe475e8
      key: netflow.collector
      namespace: global
      type: netflow.setting
      value: []
      version: 64
proprosed:
  description:  Configuration to be sent to DNA Center.
  returned: success
  type: list
  sample:
    - groupUuid: '-1'
      instanceType: netflow
      key: netflow.collector
      namespace: global
      type: netflow.setting
      value:
      - ipAddress: 192.168.91.150
        port: '6007'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.wwt.ansible_dnac.plugins.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

# -----------------------------------------------
#  define static required variales
# -----------------------------------------------
# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    module_args = dnac_argument_spec
    module_args.update(
        netflow_collector=dict(type='str', required=False),
        netflow_port=dict(type='str', required=False),
        group_name=dict(type='str',default='-1')
        )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
        )

    #  Define local variables
    state = module.params['state']
    group_name = module.params['group_name']
    netflow_collector = module.params['netflow_collector']
    netflow_port = module.params['netflow_port']

    #  Build the payload dictionary
    payload = [
        {"instanceType":"netflow",
        "namespace":"global",
        "type": "netflow.setting",
        "key":"netflow.collector",
        "value":[{
                 "ipAddress" : netflow_collector,
                 "port" : netflow_port
                 }],
        "groupUuid":"-1"
        }
        ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)

    # set the api_path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + '?key=netflow.collector'

    dnac.process_common_settings(payload, group_id)

if __name__ == "__main__":
  main()
