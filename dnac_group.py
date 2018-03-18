#!/usr/local/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'jeff andiorio'}

DOCUMENTATION = r'''
---
module: dnac_group.py
short_description: Manage groups within Cisco DNA Center
description:  Based on 1.1+ version of DNAC API
author:
- Jeff Andiorio (@jandiorio)
version_added: '2.4'
requirements:
- DNA Center 1.1+
notes:
-
options:
  tenant:
    description:
    - Name of an existing tenant.
    aliases: [ tenant_name ]
  ap:
    description:
    - Name of an existing application network profile, that will contain the EPGs.
    required: yes
    aliases: [ app_proifle, app_profile_name ]
  epg:
    description:
    - Name of the end point group.
    required: yes
    aliases: [ name, epg_name ]
  bd:
    description:
    - Name of the bridge domain being associated with the EPG.
    required: yes
    aliases: [ bd_name, bridge_domain ]
  priority:
    description:
    - QoS class.
    choices: [ level1, level2, level3, unspecified ]
    default: unspecified
  intra_epg_isolation:
    description:
    - Intra EPG Isolation.
    choices: [ enforced, unenforced ]
    default: unenforced
  description:
    description:
    - Description for the EPG.
    aliases: [ descr ]
  fwd_control:
    description:
    - The forwarding control used by the EPG.
    - The APIC defaults new EPGs to C(none).
    choices: [ none, proxy-arp ]
    default: none
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    choices: [ absent, present, query ]
    default: present
extends_documentation_fragment: aci
'''

EXAMPLES = r'''
- name: Add a new group
  dnac_group:
    hostname: dnac
    username: admin
    password: SomeSecretPassword
    name: NewGroupName
    path: /Global/NewGroupName
    description: Web Intranet EPG

  aci_epg:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    tenant: production
    ap: ticketing
    epg: "{{ item.epg }}"
    description: Ticketing EPG
    bd: "{{ item.bd }}"
    priority: unspecified
    intra_epg_isolation: unenforced
    state: present
  with_items:
    - epg: web
      bd: web_bd
    - epg: database
      bd: database_bd

- name: Remove an EPG
  aci_epg:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    validate_certs: false
    tenant: production
    app_profile: intranet
    epg: web_epg
    state: absent

- name: Query an EPG
  aci_epg:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    tenant: production
    ap: ticketing
    epg: web_epg
    state: query

- name: Query all EPGs
  aci_epg:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    state: query

- name: Query all EPGs with a Specific Name
  aci_epg:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    validate_certs: false
    epg: web_epg
    state: query

- name: Query all EPGs of an App Profile
  aci_epg:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    validate_certs: false
    ap: ticketing
    state: query
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from dnac import DNACModule, dnac_argument_spec
# import DnacSession


def get_group():
    pass

def create_group():
    pass

def delete_group():
    pass

def run_module():
    module = AnsibleModule(
        argument_spec = dict(
            group_name=dict(type='str', aliases=['name'], required=True),
            state=dict(type='str', default='present', choices=['absent', 'present', 'query'],required=True),
            path=dict(type='str', default='Global', required=True),
            type=dict(type='str', default='SITE', choices=['SITE', 'BUILDING', 'FLOOR'],required=True)
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    group_name = module.params['group_name']
    path = module.params['path']
    type = module.params['type']
    priority = module.params['priority']
    intra_epg_isolation = module.params['intra_epg_isolation']
    fwd_control = module.params['fwd_control']
    state = module.params['state']

    aci = ACIModule(module)
    aci.construct_url(root_class="tenant", subclass_1="ap", subclass_2="epg", child_classes=['fvRsBd'])
    aci.get_existing()
    result = dict(changed=False)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
