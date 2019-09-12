#!/usr/bin/env python
# Copyright (c) 2019 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: dnac_site
short_description: Add or Delete groups in DNA Center
description: Add or delete groups in the network hierarchy within Cisco DNA Center controller.
version_added: "2.5"
author: 
  - Jeff Andiorio (@jandiorio)
    
requirements:
  - requests 

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
  
  group_name: 
    description: 
      - Name of the group to modify.  
    required: true
    
  group_type: 
    description: 
      - Manages the sites in DNAC
    required: true
    default: area
    choices: 
      - area
      - building
    
  group_parent_name: 
    description: 
      - DNS domain name of the environment within Cisco DNA Center
    required: true
                            
  group_building_address: 
    description: 
      - group_name is the name of the group in the hierarchy where you would like to apply these settings. 
    required: false
    default: Global

'''

EXAMPLES = r'''

- name: add group 
  dnac_group:
    host: 1.1.1.1
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: present
    group_name: "{{group_name}}"
    group_type: "{{group_type}}"
    group_parent_name: "{{group_parent_name}}"
    group_building_address: "{{group_building_address}}"

- name: delete group 
  dnac_group:
    host: 1.1.1.1
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: absent
    group_name: "{{group_name}}"
    group_type: "{{group_type}}"
    group_parent_name: "{{group_parent_name}}"
    group_building_address: "{{group_building_address}}"

'''


RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec


__metaclass__ = type

def main():
    _site_exists = False
    _parent_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        state=dict(type='str', default='present', choices=['absent', 'present', 'update']),
        name=dict(type='str', required=True),
        site_type=dict(type='str', default='area', choices=['area','building','floor']),
        parent_name=dict(type='str', default='Global'),
        address=dict(type='str'), 
        latitude=dict(type='str',required=False),
        longitude=dict(type='str',required=False),
        rf_model=dict(type='str',choices=['Cubes And Walled Offices','Drywall Office Only', 'Indoor High Ceiling', 'Outdoor Open Space]']),
        width=dict(type='str', required=False),
        length=dict(type='str', required=False),
        height=dict(type='str', required=False),
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
    dnac.api_path = 'api/v1/group'

    #  Get the sites
    sites = dnac.get_obj()
    try: 
        _site_names = [site['name'] for site in sites['response']]
    except TypeError: 
        module.fail_json(msg=sites)
      
    # does site provided exist
    if module.params['name'] in _site_names:
        _site_exists = True
    else:
        _site_exists = False

    # does parent provided exist
    if module.params['parent_name'] in _site_names or module.params['parent_name'] == 'Global':
        _parent_exists = True
    else:
        _parent_exists = False
        module.fail_json(msg='Parent Site does not exist...')

    # Obtain Parent groupNameHierarchy
    if module.params['parent_name'] == "Global":
        parent_hierarchy = "Global"
    else:
        parent_hierarchy = [ site['groupNameHierarchy'] for site in sites['response'] if site['name'] == module.params['parent_name'] ][0]
    
      # build the required payload data structure
    if module.params['site_type'] == 'area':
        payload = {
            "type": "area",
            "site": {
                "area": {
                    "name": module.params['name'],
                    "parentName": parent_hierarchy
                    }
            }
        }

    elif module.params['site_type'] == 'building':
        payload = {
            "type": "building",
            "site": {
                "building": {
                    "name": module.params['name'],
                    "address": module.params['address'],
                    "parentName": parent_hierarchy,
                    "latitude": module.params['latitude'],
                    "longitude": module.params['longitude']
                }
            }
        }
    elif module.params['site_type'] == 'floor':
        payload = {
            "type": "floor",
            "site": {
                "floor": {
                    "name": module.params['name'],
                    "parentName": parent_hierarchy,
                    "rfModel": module.params['rf_model'],
                    "width": module.params['width'],
                    "length": module.params['length'],
                    "height": module.params['height']
                  }
              }
          }
    
    # Do the stuff
    dnac.api_path = 'dna/intent/api/v1/site'
    if module.params['state'] == 'present' and _site_exists:
        result['changed'] = False
        result['intended_payload'] = payload
        module.exit_json(msg='Site already exists.', **result)
    elif module.params['state'] == 'present' and not _site_exists:
        dnac.create_obj(payload)
    elif module.params['state'] == 'absent' and _site_exists:
        _site_id = [site['id'] for site in sites['response'] if site['name'] == module.params['name']]
        dnac.delete_obj(_site_id[0])
    elif module.params['state'] == 'absent' and not _site_exists:
        result['changed'] = False
        module.exit_json(msg='Site Does not exist.  Cannot delete.', **result)

if __name__ == "__main__":
  main()
