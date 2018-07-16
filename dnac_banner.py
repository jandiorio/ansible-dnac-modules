#/usr/bin/env python3
# Copyright (c) 2018 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status' : ['preview'],
    'supported_by' : 'community'
}

DOCUMENTATION='''

module: dnac_banner
short_description: Create a banner in Cisco DNA Center
description:
    - Create a banner in Cisco DNA Center at any valid level in the hierarchy. 

version_added: "2.5"
author: "Jeff Andiorio (@jandiorio)"
options:
# One or more of the following
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
    banner_message: 
        description: 
            - Enter the desired Message of the Day banner to post to Cisco DNA Center. 
        required: true
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
    - zypper >= 1.0
'''

EXAMPLES = '''

- name: create a banner
  dnac_banner:
    host: 1.1.1.1
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: present
    group_name: "Global"
    banner_message: "Welcome to DNAC/SDA Lab"
    
- name: delete a banner
  dnac_banner:
    host: 1.1.1.1
    port: 443
    username: "{{username}}"
    password: "{{password}}"
    state: absent
    banner_message: "Welcome to DNAC/SDA Lab"
        
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac import DnaCenter,dnac_argument_spec


# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _banner_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        banner_message=dict(type='str', required=True),
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
        {"instanceType":"banner",
        "instanceUuid": "",
        "namespace":"global",
        "type": "banner.setting",
        "key":"device.banner",
        "value":[module.params['banner_message']],
        "groupUuid":"-1",
        "inheritedGroupUuid": "",
        "inheritedGroupName": ""
        }
        ]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    if module.params['group_name'] == '-1':
        group_id = '-1'
    else:
        group_id = dnac.get_group_id(module.params['group_name'])

    payload[0].update({'groupUuid' : group_id})

    # set the api_path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id

    # check if the configuration is already in the desired state
    settings = dnac.get_obj()

    for setting in settings['response']:
        if setting['key'] == 'device.banner':
            _banner_exists = True
            if setting['value'] != '':
                if setting['value'] != payload[0]['value']:
                    dnac.create_obj(payload)
                    # response = dnac.create_obj(payload)
                    # if response.get('isError') == False:
                    #     result['changed'] = True
                    #     result['original_message'] = response
                    #     module.exit_json(msg='Created banner successfully.', **result)
                    # elif response.get('isError') == True:
                    #     result['changed'] = False
                    #     result['original_message'] = response
                    #     module.fail_json(msg='Failed to create banner!', **result)
                else:
                    result['changed'] = False
                    result['msg'] = 'Already in desired state.'
                    module.exit_json(**result)

    if not _banner_exists:
        response = dnac.create_obj(payload)

        if not response.get('isError'):
            result['changed'] = True
            result['original_message'] = response
            module.exit_json(msg='Banner created successfully.', **result)

        elif response.get('isError'):
            result['changed'] = False
            result['original_message'] = response
            module.fail_json(msg='Failed to create banner!', **result)

if __name__ == "__main__":
  main()
