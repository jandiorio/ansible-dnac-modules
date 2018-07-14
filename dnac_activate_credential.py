#/usr/bin/env python3

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status' : ['development'],
    'supported_by' : 'jandiorio'
}

"""
Copyright (c) 2018 World Wide Technology, Inc.
     All rights reserved.
     Revision history:
     22 Mar 2018  |  .1 - prototype release
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dnac import DnaCenter,dnac_argument_spec
import requests

# -----------------------------------------------
#  define static required variables
# -----------------------------------------------
# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _credential_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        credential_name=dict(type='str', required=True),
        credential_type=dict(type='str', default='SNMPV2_WRITE_COMMUNITY', \
                             choices=['SNMPV2_READ_COMMUNITY', 'SNMPV2_WRITE_COMMUNITY', 'CLI']),
        group_name=dict(type='str', default= 'Global', required=False)
        )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    # instantiate dnac object
    dnac = DnaCenter(module)

    # lookup credential id
    dnac.api_path = 'api/v1/global-credential?credentialSubType=' + module.params['credential_type']
    settings = dnac.get_obj()

    if module.params['credential_type'] == 'CLI':
        _cred_id = [user['id'] for user in settings['response'] if user['username'] == module.params['credential_name']]
    elif module.params['credential_type'] == 'SNMPV2_READ_COMMUNITY' or \
            module.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
        _cred_id = [cred['id'] for cred in settings['response'] if
                  cred['description'] == module.params['credential_name']]

    # set key string
    if module.params['credential_type'] == 'CLI':
        _credential_key = 'credential.cli'
        _credential_val_type = 'credential_cli'
    elif module.params['credential_type'] == 'SNMPV2_READ_COMMUNITY':
        _credential_key = 'credential.snmp_v2_read'
        _credential_val_type = 'credential_snmp_v2_read'
    elif module.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
        _credential_key = 'credential.snmp_v2_write'
        _credential_val_type = 'credential_snmp_v2_write'

    # lookup group id
    dnac.api_path = 'api/v1/group'
    groups = dnac.get_obj()['response']
    _group_id = [g['id'] for g in groups if g['name'] == module.params['group_name']]

    if len(_group_id) == 1:
        _group_id = _group_id[0]

    if len(_cred_id) == 1:
        _cred_id = _cred_id[0]

    # build the payload dictionary
    payload = [
        {
            "instanceUuid": "",
            "inheritedGroupName": "",
            "version": "1",
            "namespace": "global",
            "groupUuid": _group_id,
            "key": _credential_key,
            "instanceType": "reference",
            "type": "reference.setting",
            "value":
                [
                    {
                        "type": _credential_val_type ,
                        "objReferences": [
                            _cred_id
                        ], "url": ""
                    }
                ]
        }
    ]
    dnac.api_path = 'api/v1/commonsetting/global/'+ _group_id
    response = dnac.create_obj(payload)

    if type(response) == requests.models.Response:
        result['changed'] = False
        result['original_message'] = response.json()
        module.fail_json(msg='initial call failed!', **result)
    elif not response.get('isError'):
        result['changed'] = True
        result['original_message'] = response
        module.exit_json(msg='Updated credential successfully.', **result)
    elif response.get('isError'):
        result['changed'] = False
        result['original_message'] = response
        module.fail_json(msg='Failed to updated user!', **result)

if __name__ == "__main__":
  main()
