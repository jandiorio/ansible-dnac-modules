# ansible_dnac

These modules provide declarative and indempotent access to configure the design elements of [Cisco's DNA Center](https://www.cisco.com/c/en/us/products/cloud-systems.../dna-center/index.html)

## Content

[WWT / Redhat Ansible Webinar](https://www.ansible.com/resources/webinars-training/lab-automation-by-wwt-with-ansible-tower-and-cisco-dna-center)

## Included Modules 

See the `ansible-doc` documentation for more details. 

- `dnac_syslog`
- `dnac_snmpv2_credential`
- `dnac_snmp`
- `dnac_ntp`
- `dnac_ippool`
- `dnac_group`
- `dnac_dns`
- `dnac_discovery`
- `dnac_dhcp`
- `dnac_device_role`
- `dnac_device_assign_site`
- `dnac_cli_credential`
- `dnac_activate_credential`
- `dnac_banner`
- `dnac_archive_config`
- `dnac_del_archived_config`
- `dnac_netflow`
- `dnac_timezone`

## Requirements
- installation of geopy to resolve building addresses and populate lat/long
`pip install geopy`
- installation of requests python module
`pip install requests`
- installation of timezonefinder python module 
`pip install timezonefinder`

## Setup
- Locate your ansible library path: `ansible --version`
- Change to the ansible library path: example: `cd /Library/Python/2.7/site-packages/ansible` 
- Create a new directory in module_utils/network named dnac: `mkdir module_utils/network/dnac` 
- Copy file `dnac.py` to module_utils/network/dnac folder
- Copy all other *.py files to the location of your ansible custom modules. (mine is /usr/share/ansible

## EXAMPLES
The examples below set the common-settings in the DNA Center Design workflow.  Additional examples are included 
in the module documentation.  `ansible-doc *module_name*`

```yaml
- name: test my new module
  connection: local
  hosts: localhost
  gather_facts: false
  no_log: true

  tasks:
    - name: set the banner  
      dnac_banner:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        banner_message: "created by a new ansible module for banners"

    - name: set the ntp server
      dnac_ntp:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        ntp_server: 192.168.200.1

    - name: set the dhcp server
      dnac_dhcp:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        dhcp_server: 192.168.200.1

    - name: set the dns server and domain name
      dnac_dns:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        primary_dns_server: 192.168.200.1
        secondary_dns_server: 192.168.200.2
        domain_name: wwtatc.local

    - name: set the syslog server
      dnac_syslog:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        syslog_server: 172.31.3.237

    - name: set the snmp server
      dnac_snmp:
        host: 10.253.176.237
        port: 443
        username: admin
        password:  *****
        snmp_server: 172.31.3.237

    - name: set the netflow
      dnac_netflow:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        netflow_collector: 172.31.3.237
        netflow_port: 6007

    - name: set the timezone
      dnac_timezone:
        host: 10.253.176.237
        port: 443
        username: admin
        password: *****
        timezone: America/Chicago

  ```
