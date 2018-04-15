#!/usr/local/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_group.py
short_description: Manage groups within Cisco DNA Center
description:  Based on 1.1+ version of DNAC API
author:
- Jeff Andiorio (@jandiorio)
version_added: '2.4'
requirements:
- DNA Center 1.1+

'''

EXAMPLES = r'''
- name: Add a new group
  dnac_group:
    hostname: dnac
    username: admin
    password: SomeSecretPassword
    name: NewGroupName
    path: /Global/NewGroupName


'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dnac import DnaCenter,dnac_argument_spec
import json
from geopy.geocoders import Nominatim

def parse_geo(address):

    geolocator = Nominatim()
    try:
        location = geolocator.geocode(address)
    except Exception as e:
        print(e)
        sys.exit(0)

    location_parts = location.address.split(',')
    country = location_parts[len(location_parts) -1]
    attributes = {'address': location.address,
                  'country':country,
                  'latitude':location.latitude,
                  'longitude':location.longitude,
                  'type':'building'
                  }
    return attributes

def main():
    _group_exists = False
    _parent_exists = False

    module_args = dnac_argument_spec
    module_args.update(
        api_path=dict(type='str',default='api/v1/group'),
        state=dict(type='str', default='present', choices=['absent', 'present', 'update']),
        group_name=dict(type='str', required=True),
        #group_type=dict(type='str', default='SITE', choices=['SITE', 'BUILDING', 'FLOOR']),
        group_type=dict(type='str', default='area', choices=['area','building']),
        group_parent_name=dict(type='str', default='Global'),
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
        'childIds':[''],
        'groupTypeList': ['SITE'],
        'name': module.params['group_name'],
        'parentId':'',
        'additionalInfo':[
            {'attributes':{'type':module.params['group_type']},
                           'nameSpace':'Location'}
        ]
    }

    # Instantiate the DnaCenter class object
    dnac = DnaCenter(module)

    # check if the configuration is already in the desired state

    #  Get the groups
    groups = dnac.get_group(payload)

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
    _parent_id = [ group['id'] for group in groups['response'] if group['name'] == module.params['group_parent_name']]
    payload['parentId'] = _parent_id[0]

    #  do some cool Geo stuffs
    if module.params['group_type'] == 'building':
        attribs = parse_geo(module.params['group_building_address'])
        payload['additionalInfo'][0]['attributes'].update(attribs)


    if module.params['state'] == 'present' and _group_exists:
        result['changed'] = False
        module.exit_json(msg='Group already exists.', **result)
    elif module.params['state'] == 'present' and not _group_exists:
        create_group_results = dnac.create_group(payload)
        result['changed'] = True
        result['status_code'] = create_group_results.status_code
        result['original_message'] = create_group_results.json()
        if result['status_code'] not in [200, 201, 202]:
            module.fail_json(msg='Failed to create group!', **result)
        module.exit_json(msg='Group Created Successfully.', **result)
    elif module.params['state'] == 'absent' and _group_exists:
        _group_id = [group['id'] for group in groups['response'] if group['name'] == module.params['group_name']]
        delete_group_results = dnac.delete_group(_group_id[0])

        if delete_group_results.status_code in [200,201,202]:
            result['changed'] = True
            result['status_code'] = delete_group_results.status_code
            result['original_message'] = delete_group_results.json()
            module.exit_json(msg='Group Deleted Successfully.', **result)
        else:
            result['changed'] = False
            result['status_code'] = delete_group_results.status_code
            result['original_message'] = delete_group_results.json()
            module.fail_json(msg='Failed to delete group.', **result)
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

main()

if __name__ == "__main__":
  main()
