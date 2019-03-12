#/usr/bin/env python3

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status' : ['development'],
    'supported_by' : 'jandiorio'
}


DOCUMENTATION = r'''
---
module: dnac_snmpv2_credential
short_description: Manage SNMPv2 Credential(s) within Cisco DNA Center
description:  Manage SNMPv2 Credential(s) settings in Cisco DNA Center.  Based on 1.1+ version of DNAC API
author:
  - Jeff Andiorio (@jandiorio)
version_added: '2.4'
requirements:
  - DNA Center 1.2+

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
  credential_type: 
    description: Specify whether the SNMPv2 Community is READ or WRITE. 
    default:  SNMPV2_WRITE_COMMUNITY
    choices:  ['SNMPV2_READ_COMMUNITY','SNMPV2_WRITE_COMMUNITY']
    required: false
    type: string
  snmp_community: 
    description: The SNMPv2 community to be managed.
    required: true
    type: string
  snmp_description: 
    description: A description of the SNMPv2 Community.
    type: string
    required: true
  snmp_comments: 
    description: Comments about the SNMPv2 Community.
    required: true
    type: string 
        
'''

EXAMPLES = r'''

- name: create snmpv2 communities
      dnac_snmpv2_credential:
        host: "{{host}}"
        port: "{{port}}"
        username: "{{username}}"
        password: "{{password}}"
        state: present
        credential_type: SNMPV2_WRITE_COMMUNITY
        snmp_community: write-community
        snmp_description: TEST-SNMP-WRITE
        snmp_comments:  snmp write community
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.dnac.dnac import DnaCenter,dnac_argument_spec

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
            dnac.delete_obj(_creds[0][1])

    elif not _credential_exists:

        if module.params['state'] == 'present':
            dnac.api_path = 'api/v1/global-credential/' + _url_suffix
            dnac.create_obj(payload)

        elif module.params['state'] == 'absent':
            module.fail_json(msg="Credential doesn't exist.  Cannot delete or update.", **result)



if __name__ == "__main__":
  main()
