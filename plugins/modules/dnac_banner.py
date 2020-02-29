#!/usr/bin/env python

# Copyright (c) 2018, World Wide Technology, Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''

---

module: dnac_banner
short_description: Create a banner in Cisco DNA Center
description:
- Create a banner in Cisco DNA Center at any valid level in the hierarchy.
version_added: "2.5"
author: "Jeff Andiorio (@jandiorio)"
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
          - Provide the username for the connection to the
            Cisco DNA Center Controller.
      required: true
  password:
      description:
          - Provide the password for connection to the
            Cisco DNA Center Controller.
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
          - The timeout provides a value for how long to wait for the executed
            command complete.
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
          - State provides the action to be executed using the terms present,
            absent, etc.
      required: false
      default: present
      choices:
          - present
          - absent
  banner_message:
      description:
          - Enter the desired Message of the Day banner to post to
            Cisco DNA Center.
      required: false
      default: ''
  group_name:
      description:
          - group_name is the name of the group in the hierarchy where
            you would like to apply the banner.
      required: false
      default: Global
  retain_banner:
      description:
          - Boolean attribute for whether to overwrite the device existing
            banner or not.
      required: false
      default: true
notes:
requirements:
    - geopy
    - TimezoneFinder
    - requests
'''

EXAMPLES = r'''
---

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

RETURN = r'''
---
previous:
  description:  Configuration from DNA Center prior to any changes.
  returned: success
  type: list
  sample:
      - groupUuid: '-1'
        inheritedGroupName: ''
        inheritedGroupUuid: ''
        instanceType: banner
        instanceUuid: 6a8bbd9c-2346-46ae-8948-2010aad18f77
        key: device.banner
        namespace: global
        type: banner.setting
        value:
        - bannerMessage: We are testing the new dnac.py logic
          retainExistingBanner: true
        version: 5
      version: '1.0'
proposed:
  description:  Configuration to be sent to DNA Center.
  returned: success
  sample:
    - groupUuid: '-1'
      instanceType: banner
      key: device.banner
      namespace: global
      type: banner.setting
      value:
      - bannerMessage: We are testing the new dnac.py logic
        retainExistingBanner: true
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.wwt.ansible_dnac.plugins.module_utils.network.dnac.dnac import DnaCenter, dnac_argument_spec


# -----------------------------------------------
#  main
# -----------------------------------------------

def main():

    module_args = dnac_argument_spec
    module_args.update(
        banner_message=dict(type='str', default='', required=False),
        group_name=dict(type='str', default='-1'),
        retain_banner=dict(type='bool', default=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    #  Set Local Variables
    banner_message = module.params['banner_message']
    retain_banner = module.params['retain_banner']
    group_name = module.params['group_name']
    # state = module.params['state']

    #  Build the payload dictionary
    payload = [{"instanceType": "banner",
                "namespace": "global",
                "type": "banner.setting",
                "key": "device.banner",
                "value": [{"bannerMessage": banner_message,
                           "retainExistingBanner": retain_banner
                           }],
                "groupUuid": "-1"
                }]

    # instansiate the dnac class
    dnac = DnaCenter(module)

    # obtain the groupUuid and update the payload dictionary
    group_id = dnac.get_group_id(group_name)

    # set the retain banner attribute
    if retain_banner:
        payload[0]['value'][0]['retainExistingBanner'] = True
    else:
        payload[0]['value'][0]['retainExistingBanner'] = False

    # set the api_path
    dnac.api_path = 'api/v1/commonsetting/global/' + group_id + \
        '?key=device.banner'

    dnac.process_common_settings(payload, group_id)


if __name__ == "__main__":
    main()
