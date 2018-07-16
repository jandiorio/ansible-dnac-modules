#!/usr/local/python
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''

module: dnac_device_assign_site
short_description: Assign the device(s) to a site  
description:
    - Set the device site assignment in the DNA Center Inventory Database. 

version_added: "2.5"
author: "Jeff Andiorio (@jandiorio)"

options:
    host: 
        description: 
            - Host is the target Cisco DNA Center controller to execute against. 
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    port: 
        description: 
            - Port is the TCP port for the HTTP connection. 
        required: true
        default: 443
        choices: 
            - 80
            - 443
        aliases: null
        version_added: "2.5"
    username: 
        description: 
            - Provide the username for the connection to the Cisco DNA Center Controller.
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"        
    password: 
        description: 
            - Provide the password for connection to the Cisco DNA Center Controller.
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    use_proxy: 
        description: 
            - Enter a boolean value for whether to use proxy or not.  
        required: false
        default: true
        choices:
            - true
            - false
        aliases: null
        version_added: "2.5"
    use_ssl: 
        description: 
            - Enter the boolean value for whether to use SSL or not.
        required: false
        default: true
        choices: 
            - true
            - false
        aliases: null
        version_added: "2.5"
    timeout: 
        description: 
            - The timeout provides a value for how long to wait for the executed command complete.
        required: false
        default: 30
        choices: null
        aliases: null
        version_added: "2.5"
    validate_certs: 
        description: 
            - Specify if verifying the certificate is desired.
        required: false
        default: true
        choices: 
            - true
            - false
        aliases: null
        version_added: "2.5"
    state: 
        description: 
            - State provides the action to be executed using the terms present, absent, etc.
        required: true
        default: present
        choices: 
            - present
            - absent
        aliases: null
        version_added: "2.5"

    device_name: 
        description: 
            - name of the device in the inventory database that you would like to update
        required: false
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    device_mgmt_ip: 
        description: 
            - Management IP Address of the device you would like to update 
        required: false
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    group_name: 
        description: 
            - Short group name to assign the site to.  
        required: false
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    group_name_hierarchy: 
        description: 
            - fully qualified group hierarchy to assign the site to.  
        required: false
        default: null
        choices: null
        aliases: null
        version_added: "2.5"        
        
notes: 
    - Either device_name or device_mgmt_ip is required, but not both.  
    
requirements:
    - geopy
    - TimezoneFinder
    - requests 

'''

EXAMPLES = '''

- name: add device to site
  dnac_device_assign_site:
    host: "{{host}}"
    port: 443
    state: present
    username: "{{username}}"
    password: "{{password}}"
    device_mgmt_ip: 192.168.200.1
        group_name_hierarchy: "Global/Central/ATC56"

- name: update device site assignment
  dnac_device_assign_site:    
    host: "{{host}}"
    port: 443
    state: update
    username: "{{username}}"
    password: "{{password}}"
    device_mgmt_ip: 192.168.200.1
    group_name_hierarchy: "Global/Central/ATC56"

- name: remove device site assignment
  dnac_device_assign_site:
    host: "{{host}}"
    port: 443
    state: update
    username: "{{username}}"
    password: "{{password}}"
    device_mgmt_ip: 192.168.200.1
    group_name_hierarchy: "Global/Central/ATC56/Floor-1"

'''

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_device_assign_site.py
short_description: Manage device site assignment within Cisco DNA Center
description:  Based on 1.1+ version of DNAC API
author:
- Jeff Andiorio (@jandiorio)
version_added: '2.4'
requirements:
- DNA Center 1.1+

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac import DnaCenter,dnac_argument_spec
import requests

def main():
    _device_exists = False
    payload = ''
    module_args = dnac_argument_spec
    module_args.update(
        device_name=dict(type='str', required=False),
        device_mgmt_ip=dict(type='str',required=False),
        group_name=dict(type='str',required=False),
        group_name_hierarchy=dict(type='str',required=False)
    )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)

    # Get device details based on either the Management IP or the Name Provided
    if module.params['device_mgmt_ip'] is not None:
        dnac.api_path = 'api/v1/network-device?managementIpAddress=' + module.params['device_mgmt_ip']
    elif module.params['device_name'] is not None:
        dnac.api_path = 'api/v1/network-device?hostname=' + module.params['device_name']

    device_results = dnac.get_obj()

    try:
        device_id = device_results['response'][0]['id']
    except IndexError:
        module.fail_json(msg='Unable to find device with supplied information.')

    # get the group id
    if module.params['group_name'] is not None:
        dnac.api_path = 'api/v1/group?groupName=' + module.params['group_name']
    elif module.params['group_name_hierarchy'] is not None:
        dnac.api_path = 'api/v1/group?groupNameHierarchy=' + module.params['group_name_hierarchy']

    # dnac.api_path = 'api/v1/group?groupName=' + module.params['group_name']
    group_results = dnac.get_obj()

    try:
        group_id = group_results['response'][0]['id']
    except IndexError:
        module.fail_json(msg='Unable to find group with the supplied information.')

    #  check if the device is already a member of that group
    dnac.api_path = 'api/v1/member/group?groupType=SITE&id=' + device_id
    group_assignment = dnac.get_obj()

    payload = {'networkdevice': [device_id]}
    dnac.api_path = 'api/v1/group/' + group_id + '/member'

    if module.params['state'] == 'present':
        if group_assignment['response'][device_id]:
            if group_assignment['response'][device_id][0]['id'] == group_id:
                result['changed'] = False
                module.exit_json(msg='Device assigned to the correct group.', **result)
            else:
                result['changed'] = False
                module.fail_json(msg='Device is already assigned to another group.  Use update as the state.', **result)
        else:
            dnac.create_obj(payload)
    elif module.params['state'] == 'absent':
        if not group_assignment['response'][device_id]:
            module.fail_json(msg='Device is not assigned to a group.  Cannot remove assignment')
        elif group_assignment['response'][device_id][0]['id'] != group_id:
            module.fail_json(msg='Device is not assigned to the group provided.  Device is currently in group:' + group_assignment['response'][device_id][0]['groupNameHierarchy'])
        else:
            dnac.delete_obj(device_id)
    elif module.params['state'] == 'update':
        if not group_assignment['response'][device_id]:
            dnac.create_obj(payload)
        elif group_assignment['response'][device_id][0]['id'] == group_id:
            result['changed'] = False
            module.exit_json(msg='Device already assigned to the target group.  No changes required.')
        elif  group_assignment['response'][device_id][0]['id'] != group_id:
            _current_group_id = group_assignment['response'][device_id][0]['id']
            dnac.api_path = 'api/v1/group/' + _current_group_id + '/member'
            dnac.delete_obj(device_id)

            # change the API to the new group
            dnac.api_path = 'api/v1/group/' + group_id + '/member'
            dnac.create_obj(payload)

if __name__ == "__main__":
  main()
