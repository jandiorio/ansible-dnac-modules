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
    ip_pool_gateways: 172.31.102.1
    ip_pool_dhcp_server_ips: 192.168.200.1
    ip_pool_dns_server_ips: 192.168.200.1
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dnac import DnaCenter,dnac_argument_spec

def main():
    _ip_pool_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        api_path=dict(type='str',default='api/v2/ippool'),
        state=dict(type='str', default='present', choices=['absent', 'present', 'update']),
        ip_pool_name=dict(type='str', required=True),
        ip_pool_subnet=dict(type='str',required=True),
        ip_pool_prefix_len=dict(type='str', default='/8'),
        ip_pool_gateways=dict(type='str', required=True),
        ip_pool_dhcp_server_ips=dict(type='str'),
        ip_pool_dns_server_ips = dict(type='str'),
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
        "gateways": module.params['ip_pool_gateways'].split(','),
        "dhcpServerIps": module.params['ip_pool_dhcp_server_ips'].split(','),
        "dnsServerIps": module.params['ip_pool_dns_server_ips'].split(','),
        "overlapping":  module.params['ip_pool_overlapping']
    }

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)

    # check if the configuration is already in the desired state

    #  Get the ip pools
    ip_pools = dnac.get_ippool(payload)

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
        create_ip_pool_results = dnac.create_ippool(payload)
        if create_ip_pool_results.get('isError') == False:
            result['changed'] = True
            result['original_message'] = create_ip_pool_results['progress']
            module.exit_json(msg='Ip pool Created Successfully.', **result)
        if create_ip_pool_results.get('isError') == True:
            result['changed'] = False
            result['original_message'] = create_ip_pool_results
            module.fail_json(msg='Failed to create ip pool!', **result)
    elif module.params['state'] == 'absent' and _ip_pool_exists:
        _ip_pool_id = [pool['id'] for pool in ip_pools['response'] if pool['ipPoolName'] == module.params['ip_pool_name']]
        delete_ip_pool_results = dnac.delete_ippool(_ip_pool_id[0])
        if delete_ip_pool_results.status_code in [200,201,202]:
            result['changed'] = True
            result['status_code'] = delete_ip_pool_results.status_code
            result['original_message'] = delete_ip_pool_results.json()
            module.exit_json(msg='IP pool Deleted Successfully.', **result)
        else:
            result['changed'] = False
            result['status_code'] = delete_ip_pool_results.status_code
            result['original_message'] = delete_ip_pool_results.json()
            module.fail_json(msg='Failed to delete ip pool.', **result)
    elif module.params['state'] == 'absent' and not _ip_pool_exists:
        result['changed'] = False
        module.exit_json(msg='Ip pool Does not exist.  Cannot delete.', **result)


main()

if __name__ == "__main__":
  main()
