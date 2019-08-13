#!/usr/bin/env python
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: dnac_group
short_description: Add or Delete groups in DNA Center
description: Add or delete groups in the network hierarchy within Cisco DNA Center controller.
version_added: "2.5"
author: 
  - Jeff Andiorio (@jandiorio)
    
requirements:
  - geopy
  - TimezoneFinder
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
from geopy.geocoders import Nominatim
import sys

__metaclass__ = type

# def parse_geo(address):
# 
#     geolocator = Nominatim(user_agent='dnac_ansible',timeout=30)
#     try:
#         location = geolocator.geocode(address)
#     except Exception as e:
#         print(e)
#         #debugging
#         module.exit_json(msg='Failed to get location.', **result)
#         sys.exit(0)
# 
#     location_parts = location.address.split(',')
#     country = location_parts[len(location_parts) -1]
#     attributes = {'address': location.address,
#                   'country':country,
#                   'latitude':location.latitude,
#                   'longitude':location.longitude,
#                   'type':'building'
#                   }
#     return attributes

def main():
    _group_exists = False
    _parent_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        state=dict(type='str', default='present', choices=['absent', 'present', 'update']),
        group_name=dict(type='str', required=True),
        group_type=dict(type='str', default='area', choices=['area','building']),
        group_parent_name=dict(type='str', default='-1'),
        group_building_address=dict(type='str', default='123')
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
        "childIds":[""],
        "groupTypeList": ["SITE"],
        "name": module.params["group_name"],
        "additionalInfo":[
            {"attributes":{
                "type":module.params["group_type"]
            },
            "nameSpace":"Location"}
         ]
    }


    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)
    dnac.api_path = 'api/v1/group'

    #  Get the groups
    groups = dnac.get_obj()
    _group_names = [group['name'] for group in groups['response']]

    # does group provided exist
    if module.params['group_name'] in _group_names:
        _group_exists = True
    else:
        _group_exists = False

    # does parent provided exist
    if module.params['group_parent_name'] in _group_names:
        _parent_exists = True
    else:
        _parent_exists = False
        module.fail_json(msg='Parent Group does not exist...')

    # find the parent Id specificed by the name
    #_parent_id = [ group['id'] for group in groups['response'] if group['name'] == module.params['group_parent_name']]
    if module.params['group_parent_name'] == 'Global' or module.params['group_parent_name'] == '-1':
        payload.update({'parentId' : ''})
    elif _parent_exists:
        _parent_id = dnac.get_group_id(module.params['group_parent_name'])
        payload.update({'parentId': _parent_id})
    else:
        result['changed'] = False
        module.fail_json(msg="Parent doesn't exist!", **result)

    #  lookup lat/long based on provided address
    if module.params['group_type'] == 'building':
        attribs = dnac.parse_geo(module.params['group_building_address'])
        payload['additionalInfo'][0]['attributes'].update(attribs)

    if module.params['state'] == 'present' and _group_exists:
        result['changed'] = False
        result['intended_payload'] = payload
        module.exit_json(msg='Group already exists.', **result)
    elif module.params['state'] == 'present' and not _group_exists:
        dnac.create_obj(payload)
    elif module.params['state'] == 'absent' and _group_exists:
        _group_id = [group['id'] for group in groups['response'] if group['name'] == module.params['group_name']]
        dnac.delete_obj(_group_id[0])
    elif module.params['state'] == 'absent' and not _group_exists:
        result['changed'] = False
        module.exit_json(msg='Group Does not exist.  Cannot delete.', **result)


    '''
    {'additionalInfo': [{'attributes': {'type': 'area'}, 'nameSpace': 'Location'}],
     'childIds': [''],
     'groupTypeList': ['SITE'],
     'id': '',
     'name': 'West',
     'parentId': 'd86d461a-8e98-4652-be96-361be5a0f6b6'}

     '''

if __name__ == "__main__":
  main()
