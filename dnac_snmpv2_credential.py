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

# -----------------------------------------------
#  define static required variales
# -----------------------------------------------
# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _credential_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        credential_type=dict(type='str', default='SNMPV2_WRITE_COMMUNITY',choices=['SNMPV2_READ_COMMUNITY','SNMPV2_WRITE_COMMUNITY']),
        snmp_community=dict(type='str', required=True),
        snmp_description=dict(type='str', required=True),
        snmp_comments=dict(type='str', required=True)
        )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )
    if module.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
        _community_key_name = 'writeCommunity'
        _url_suffix = 'snmpv2-write-community'
    elif module.params['credential_type'] == 'SNMPV2_READ_COMMUNITY':
        _community_key_name = 'readCommunity'
        _url_suffix = 'snmpv2-read-community'

    #  Build the payload dictionary
    payload = [
      {_community_key_name: module.params['snmp_community'],
        "description": module.params['snmp_description'],
        "comments": module.params['snmp_comments']
      }
    ]

    # instansiate the dnac class
    dnac = DnaCenter(module)
    dnac.api_path = 'api/v1/global-credential?credentialSubType=' + module.params['credential_type']
    #
    # check if the configuration is already in the desired state
    settings = dnac.get_obj()

#    _creds = [ cred['description'] for cred in settings['response']]
    _creds = [(cred['description'], cred['id']) for cred in settings['response'] if cred['description'] == module.params['snmp_description']]

    if len(_creds) > 1:
        module.fail_json(msg="Multiple matching entries...invalid.", **result)
    elif len(_creds) == 0:
        _credential_exists = False
    else:
        _credential_exists = True

    '''
    check if cred exists
    check state flag: present = create, absent = delete, update = change url_password
    if state = present and cred doesn't exist, create user
    if state = absent and cred exists, delete user
    if state = update and cred exists, use put to update user '''

    if _credential_exists:

        if module.params['state'] == 'present':
            # in desired state
            result['changed'] = False
            result['msg'] = 'Credential exists. Use state: update to change credential'
            module.exit_json(**result)

        elif module.params['state'] == 'absent':
            dnac.api_path = 'api/v1/global-credential/'
            response = dnac.delete_obj(_creds[0][1])
            # result['changed'] = True
            # result['msg'] = 'Credential Deleted.' + _creds[0][0]
            # module.exit_json(**result)


    elif not _credential_exists:

        if module.params['state'] == 'present':
            dnac.api_path = 'api/v1/global-credential/' + _url_suffix
            response = dnac.create_obj(payload)
            # result['changed'] = True
            # result['msg'] = 'Credential exists. Use state: update to change credential'
           # module.exit_json(**result)

        elif module.params['state'] == 'absent':
            module.fail_json(msg="Credential doesn't exist.  Cannot delete or update.", **result)

    if not response.get('isError'):
        result['changed'] = True
        result['original_message'] = response
        module.exit_json(msg='Updated credential successfully.', **result)
    elif response.get('isError'):
        result['changed'] = False
        result['original_message'] = response
        module.fail_json(msg='Failed to updated user!', **result)

main()

if __name__ == "__main__":
  main()
