#!/usr/bin/env python
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

module: dnac_dns
short_description: Add or Delete DNS Server(s)
description:  Add or delete DNS Server(s) in the Cisco DNA Center Design Workflow.  \
    The DNS Severs can be different values at different levels in the group hierarchy.

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
    required: false

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

EXAMPLES = r'''

- name: create dns server
  dnac_dns:
    host: "{{ dnac.hostname }}"
    port: "{{ dnac.port }}"
    username: "{{ dnac.username }}"
    password: "{{ dnac.password }}"
    state: present
    primary_dns_server: 192.168.200.1
    secondary_dns_server: 192.168.200.2
    domain_name: dna.center.local


- name: delete dns server
  dnac_dns:
    host: "{{ dnac.hostname }}"
    port: "{{ dnac.port }}"
    username: "{{ dnac.username }}"
    password: "{{ dnac.password }}"
    state: absent


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
      instanceType: dns
      instanceUuid: 799b3bc7-61fa-41b2-8fb3-db611af9db67
      key: dns.server
      namespace: global
      type: dns.setting
      value: []
      version: 52
proprosed:
  description:  Configuration to be sent to DNA Center.
  returned: success
  type: list
  sample:
    - groupUuid: '-1'
      instanceType: dns
      key: dns.server
      namespace: global
      type: dns.setting
      value:
      - domainName: campus.wwtatc.local
        primaryIpAddress: 192.168.200.1
        secondaryIpAddress: 192.168.200.2
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.wwt.ansible_dnac.plugins.module_utils.network.dnac.dnac import DnaCenter, dnac_argument_spec

# -----------------------------------------------
#  define static required variales
# -----------------------------------------------
# -----------------------------------------------
#  main
# -----------------------------------------------


def main():
    module_args = dnac_argument_spec
    module_args.update(primary_dns_server=dict(type='str', required=False, default=''),
                       secondary_dns_server=dict(type='str', required=False),
                       domain_name=dict(type='str', required=False, default=''),
                       group_name=dict(type='str', required=False, default='-1')
                       )

    module = AnsibleModule(argument_spec=module_args,
                           supports_check_mode=True
                           )

    #  Define local variables
    state = module.params['state']
    domain_name = module.params['domain_name']
    primary_dns_server = module.params['primary_dns_server']
    secondary_dns_server = module.params['secondary_dns_server']
    group_name = module.params['group_name']

    #  Build the payload dictionary
    payload = [{"instanceType": "dns",
                "namespace": "global",
                "type": "dns.setting",
                "key": "dns.server",
                "value": [{"domainName": domain_name,
                           "primaryIpAddress": primary_dns_server,
                           "secondaryIpAddress": secondary_dns_server
                           }],
                "groupUuid": "-1",
                }
               ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)

    # Set the api_path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + '?key=dns.server'

    dnac.process_common_settings(payload, group_id)


if __name__ == "__main__":
    main()
