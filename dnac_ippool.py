#!/usr/local/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_ippool.py
short_description: Manage ip pools within Cisco DNA Center
description:  Based on 1.1+ version of DNAC API
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
  
  ip_pool_name: 
    description: Name of the pool.
    required: true
    type: string
  ip_pool_subnet:
    description: Subnet represented by the pool. 
    required: true
    type: string
  ip_pool_prefix_len: 
    description: Prefix length expresses in slash notation (/24)
    required: false
    default: /8
    type: string
  ip_pool_gateway:
    description: The gateway associated with the subnet specified.
    required: true
    type: string
  ip_pool_dhcp_servers:
    description:  A list of DHCP Servers (Maximum 2)
    type: list 
    required: false 
  ip_pool_dns_servers:
    description: A list of DNS Servers (Maximum 2)
    type: list
    required: false
  ip_pool_overlapping: 
    description: Indicate if the pool has overlapping networks. 
    type: bool
    default: false
    required: false
        
'''

EXAMPLES = r'''
- name: ip pool management
  dnac_ippool:
    host: 10.253.176.237
    port: 443
    username: admin
    password: M0bility@ccess
    state: present
    ip_pool_name: TEST_IP_POOL1
    ip_pool_subnet: 172.31.102.0
    ip_pool_prefix_len: /24
    ip_pool_gateway: 172.31.102.1
    ip_pool_dhcp_servers: 192.168.200.1
    ip_pool_dns_servers: 192.168.200.1
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac import DnaCenter,dnac_argument_spec

def main():
    _ip_pool_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        # removed api_path local variable
        state=dict(type='str', default='present', choices=['absent', 'present', 'update']),
        ip_pool_name=dict(type='str', required=True),
        ip_pool_subnet=dict(type='str',required=True),
        ip_pool_prefix_len=dict(type='str', default='/8'),
        ip_pool_gateway=dict(type='str', required=True),
        ip_pool_dhcp_servers=dict(type='list'),
        ip_pool_dns_servers = dict(type='list'),
        ip_pool_overlapping=dict(type='bool', default=False)
    )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    # build the required payload data structure
    payload = {
        "ipPoolName": module.params['ip_pool_name'],
        "ipPoolCidr": module.params['ip_pool_subnet'] + module.params['ip_pool_prefix_len'],
        "gateways": module.params['ip_pool_gateway'].split(','),
        "dhcpServerIps": module.params['ip_pool_dhcp_servers'],
        "dnsServerIps": module.params['ip_pool_dns_servers'],
        "overlapping":  module.params['ip_pool_overlapping']
        }

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)
    dnac.api_path = 'api/v2/ippool'
    # check if the configuration is already in the desired state

    #  Get the ip pools
    ip_pools = dnac.get_obj()

    _ip_pool_names = [pool['ipPoolName'] for pool in ip_pools['response']]

    # does pool provided exist
    if module.params['ip_pool_name'] in _ip_pool_names:
        _ip_pool_exists = True
    else:
        _ip_pool_exists = False

    # actions
    if module.params['state'] == 'present' and _ip_pool_exists:
        result['changed'] = False
        module.exit_json(msg='IP Pool already exists.', **result)
    elif module.params['state'] == 'present' and not _ip_pool_exists:
        dnac.create_obj(payload)
    elif module.params['state'] == 'absent' and _ip_pool_exists:
        _ip_pool_id = [pool['id'] for pool in ip_pools['response'] if pool['ipPoolName'] == module.params['ip_pool_name']]
        dnac.delete_obj(_ip_pool_id[0])
    elif module.params['state'] == 'absent' and not _ip_pool_exists:
        result['changed'] = False
        module.exit_json(msg='Ip pool Does not exist.  Cannot delete.', **result)

if __name__ == "__main__":
  main()
