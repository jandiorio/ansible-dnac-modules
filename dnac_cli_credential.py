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
#import ansible.module_utils.dnac
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
        api_path = dict(required=False, default='api/v1/global-credential', type='str'),
        credential_type=dict(type='str', default='CLI'),
        cli_user=dict(type='str', required=True),
        cli_password=dict(type='str', required=True),
        cli_enable_password=dict(type='str', required=True),
        cli_desc=dict(type='str', required=True),
        cli_comments=dict(type='str', required=False)
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
    #
    # # check if the configuration is already in the desired state
    #settings = dnac.get_global_credentials(payload)
    settings = dnac.get_global_credentials(payload)
    settings = settings
    #settings = json.loads(settings)

    '''
    check if username exists
    check state flag: present = create, absent = delete, update = change url_password
    if state = present and user doesn't exist, create user
    if state = absent and user exists, delete user
    if state = update and user exists, use put to update user

    '''

    for setting in settings['response']:
        if setting['username'] == payload[0]['username']:
            _user_exists = True
            if module.params['state'] == 'absent':
                dnac.delete_global_credentials(setting['id'])
                result['changed'] = True
                result['msg'] = 'User Deleted.'
                module.exit_json(**result)
            elif module.params['state'] == 'update':
                # call update function
                payload = payload[0].update({'id': setting['id']})
                response = dnac.update_global_credential(payload)

                if response.status_code not in [200, 201, 202]:
                    result['changed'] = False
                    result['status_code'] = response.status_code
                    result['original_message'] = response.json()
                    module.fail_json(msg="Status Code not 200", **result)
                else:
                    result['changed'] = True
                    result['msg'] = response.json()
                    result['status_code'] = response.status_code
                    module.exit_json(**result)

                # result['changed'] = True
                # result['msg'] = 'User updated.'
                # module.exit_json(**result)

    if _user_exists == False and module.params['state'] == 'present':
         # call create function
        response = dnac.create_global_credential(payload)
    elif _user_exists == False and module.params['state'] == 'update':
        module.fail_json(msg="User doesn't exist.  Cannot delete or update.", **result)
    elif _user_exists == False and module.params['state'] == 'absent':
        module.fail_json(msg="User doesn't exist.  Cannot delete or update.", **result)
    elif _user_exists == True and module.params['state'] == 'present':
        result['changed'] = False
        result['msg'] = 'User exists. Use state: update to change user'
        module.exit_json(**result)

    if response.status_code not in [200, 201, 202]:
        result['changed'] = False
        result['status_code'] = response.status_code
        result['original_message'] = response.json()
        module.fail_json(msg="Status Code not 200", **result)
    else:
        result['changed'] = True
        result['msg'] = response.json()
        result['status_code'] = response.status_code
        module.exit_json(**result)

main()

if __name__ == "__main__":
  main()
