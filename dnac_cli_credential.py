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
    _user_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        cli_user=dict(type='str', required=True),
        cli_password=dict(type='str', required=True),
        cli_enable_password=dict(type='str', required=True),
        cli_desc=dict(type='str', required=True),
        cli_comments=dict(type='str', required=False),
        group_name=dict(type='str',default='-1')
        )

    result = dict(
        changed=False,
        original_message='',
        message='')

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = False
        )

    #  Build the payload dictionary
    payload = [
      {"username": module.params['cli_user'],
        "password": module.params['cli_password'],
        "enablePassword": module.params['cli_enable_password'],
        "description": module.params['cli_desc'],
        "comments": module.params['cli_comments']
      }
    ]

    # instansiate the dnac class
    dnac = DnaCenter(module)
    dnac.api_path = 'api/v1/global-credential?credentialSubType=CLI'

    # check if the configuration is already in the desired state
    settings = dnac.get_obj()

    _usernames = [ user['username'] for user in settings['response']]
    if module.params['cli_user'] in _usernames:
        _user_exists = True
    else:
         _user_exists = False

    '''
    check if username exists
    check state flag: present = create, absent = delete, update = change url_password
    if state = present and user doesn't exist, create user
    if state = absent and user exists, delete user
    if state = update and user exists, use put to update user '''

    for setting in settings['response']:
        if setting['username'] == payload[0]['username']:
            if module.params['state'] == 'absent':
                dnac.api_path='api/v1/global-credential/cli'
                    dnac.delete_obj(setting['id'])
                result['changed'] = True
                result['msg'] = 'User Deleted.'
                module.exit_json(**result)
            elif module.params['state'] == 'update':
                # call update function
                payload = payload[0].update({'id': setting['id']})
                dnac.api_path = 'api/v1/global-credential/cli'
                response = dnac.update_obj(payload)

                if not response.get('isError'):
                    result['changed'] = True
                    result['original_message'] = response
                    module.exit_json(msg='Updated user successfully.', **result)
                elif response.get('isError'):
                    result['changed'] = False
                    result['original_message'] = response
                    module.fail_json(msg='Failed to updated user!', **result)

    if not _user_exists and module.params['state'] == 'present':
         # call create function
         dnac.api_path = 'api/v1/global-credential/cli'
         response = dnac.create_obj(payload)
    elif not _user_exists and module.params['state'] == 'update':
        module.fail_json(msg="User doesn't exist.  Cannot delete or update.", **result)
    elif not _user_exists and module.params['state'] == 'absent':
        module.fail_json(msg="User doesn't exist.  Cannot delete or update.", **result)
    elif _user_exists and module.params['state'] == 'present':
        result['changed'] = False
        result['msg'] = 'User exists. Use state: update to change user'
        module.exit_json(**result)
    if not response.get('isError'):
        result['changed'] = True
        result['original_message'] = response
        module.exit_json(msg='Updated user successfully.', **result)
    elif response.get('isError'):
        result['changed'] = False
        result['original_message'] = response
        module.fail_json(msg='Failed to updated user!', **result)

main()

if __name__ == "__main__":
  main()
