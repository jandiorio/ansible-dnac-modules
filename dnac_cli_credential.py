#/usr/bin/env python3
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''

module: dnac_cli_credential
short_description: Add or Delete Global CLI credentials 
description:
    - Add or Delete Global CLI Credentials in Cisco DNA Center Controller.  These credentials can be created at any level \
    in the hierarchy.  This module creates the credential at the specified level of hierarchy only.  * Assigning the \
    credential as active in the Design Workflow will be handled in the dnac_assign_credential module.

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

    cli_user: 
        description: 
            - Global CLI username to be manipulated
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    cli_password: 
        description: 
            - Provide the Global CLI password to associate with the CLI username being created. 
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    cli_enable_password: 
        description: 
            - Provide a value for the CLI Enable password. 
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    cli_desc: 
        description: 
            - cli_desc is a friendly description of the CLI credential being created.  
        required: true
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    cli_comments: 
        description: 
            - cli_comments is space for any additional information about the CLI credential.  
        required: false
        default: null
        choices: null
        aliases: null
        version_added: "2.5"
    group_name: 
        description: 
            - group_name is the name of the group in the hierarchy where you would like to apply the banner. 
        required: false
        default: Global
        choices: null
        aliases: null
        version_added: "2.5"
notes: 
    - null
requirements:
    - geopy
    - TimezoneFinder
    - requests 
    
'''

EXAMPLES = '''

- name: create a user
  dnac_cli_credential:
    host: 10.253.177.230
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: present
    cli_user: "cisco"
    cli_password: "cisco"
    cli_enable_password: "your_password"
    cli_desc: "User Description"
    cli_comments: "some comments"

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac import DnaCenter,dnac_argument_spec

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
        cli_password=dict(type='str', required=True, no_log=True),
        cli_enable_password=dict(type='str', required=True, no_log=True),
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
                response = dnac.delete_obj(setting['id'])
                result['changed'] = True
                result['msg'] = 'User Deleted.'
                module.exit_json(**result)
            elif module.params['state'] == 'update':
                # call update function
                payload = payload[0].update({'id': setting['id']})
                dnac.api_path = 'api/v1/global-credential/cli'
                dnac.update_obj(payload)

    if not _user_exists and module.params['state'] == 'present':
         # call create function
         dnac.api_path = 'api/v1/global-credential/cli'
         dnac.create_obj(payload)
    elif not _user_exists and module.params['state'] == 'update':
        module.fail_json(msg="User doesn't exist.  Cannot delete or update.", **result)
    elif not _user_exists and module.params['state'] == 'absent':
        module.fail_json(msg="User doesn't exist.  Cannot delete or update.", **result)
    elif _user_exists and module.params['state'] == 'present':
        result['changed'] = False
        result['msg'] = 'User exists. Use state: update to change user'
        module.exit_json(**result)

if __name__ == "__main__":
  main()
