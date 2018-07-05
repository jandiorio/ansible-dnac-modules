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
from timezonefinder import TimezoneFinder
from ansible.module_utils.dnac import DnaCenter,dnac_argument_spec

# -----------------------------------------------
#  define static required variales
# -----------------------------------------------
# -----------------------------------------------
#  main
# -----------------------------------------------

def main():
    _setting_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        ntp_server=dict(type='str',required=True),
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
        {"instanceType":"ip",
        "instanceUuid": "",
        "namespace":"global",
        "type": "ip.address",
        "key":"ntp.server",
        "value":[],
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

    if group_id:
        payload[0].update({'groupUuid': group_id})
    else:
        result['changed'] = False
        result['original_message'] = group_id
        module.fail_json(msg='Failed to create NTP server! Unable to locate group provided.', **result)

    # Support multiple snmp servers
    _ntp_server = module.params['ntp_server'].split(' ')
    payload[0].update({'value': _ntp_server})

    # # check if the configuration is already in the desired state
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id
    settings = dnac.get_obj()

    for setting in settings['response']:
        if setting['key'] == payload[0]['key']:
            _setting_exists = True
            if setting['value'] != '':
                if setting['value'] != payload[0]['value']:
                    response = dnac.create_obj(payload)
                    if response.get('isError') == False:
                        result['changed'] = True
                        result['original_message'] = response
                        module.exit_json(msg='Created NTP server successfully.', **result)
                    elif response.get('isError') == True:
                        result['changed'] = False
                        result['original_message'] = response
                        module.fail_json(msg='Failed to create NTP server!', **result)
                else:
                    result['changed'] = False
                    result['msg'] = 'Already in desired state.'
                    module.exit_json(**result)

    if _setting_exists == False:
        response = dnac.create_obj(payload)

        if response.get('isError') == False:
            result['changed'] = True
            result['original_message'] = response
            module.exit_json(msg='NTP Server created successfully.', **result)

        elif response.get('isError') == True:
            result['changed'] = False
            result['original_message'] = response
            module.fail_json(msg='Failed to create NTP Server!', **result)

if __name__ == "__main__":
  main()
