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
    _setting_exists = False
    module_args = dnac_argument_spec
    module_args.update(
        netflow_collector=dict(type='str', required=True),
        netflow_port=dict(type='str', required=True),
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
        {"instanceType":"netflow",
        "instanceUuid": "",
        "namespace":"global",
        "type": "netflow.setting",
        "key":"netflow.collector",
        "value":[{
                 "ipAddress" : module.params['netflow_collector'],
                 "port" : module.params['netflow_port']
                 }],
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

    # # check if the configuration is already in the desired state
    settings = dnac.get_obj()

    for setting in settings['response']:
        if setting['key'] == payload[0]['key']:
            _setting_exists == True
            if setting['value'] != '':
                if setting['value'][0]['ipAddress'] != payload[0]['value'][0]['ipAddress'] and \
                    setting['value'][0]['port'] != payload[0]['value'][0]['port']:
                    #execute
                    dnac.create_obj(payload)
                else:
                    result['changed'] = False
                    result['msg'] = 'Already in desired state.'
                    module.exit_json(**result)

    if not _setting_exists:
        dnac.create_obj(payload)

if __name__ == "__main__":
  main()
