# Ansible Collection - wwt.ansible_dnac

## Ansible Modules for DNA Center

These modules provide declarative and idempotent access to configure the design elements of [Cisco's DNA Center](https://www.cisco.com/c/en/us/products/cloud-systems.../dna-center/index.html).

### DevNet Code Exchange

This repository is featured on the Cisco DevNet Code Exchange.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/jandiorio/ansible-dnac-modules)


### Content

The webinar below was hosted by Redhat and delivered by Jeff Andiorio of World Wide Technology on 8/7/2018.

[WWT / Redhat Ansible Webinar](https://www.ansible.com/resources/webinars-training/lab-automation-by-wwt-with-ansible-tower-and-cisco-dna-center)


Additional slides providing an overview of the modules can be found here:  [Ansible DNA Center Modules Overview](https://www.slideshare.net/secret/1l5xe5ORzTN3Uv)

### Included Modules

The documentation can be viewed using  `ansible-doc` and will provide all of the details including examples of usage.

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
- `dnac_wireless_ssid`
- `dnac_wireless_provision`
- `dnac_wireless_profile`

### Requirements

This solution requires the installation of the following python modules:

- **geopy** to resolve building addresses and populate lat/long
  `pip install geopy`
- **requests** for http requests
  `pip install requests`
- **timezonefinder** for resolving the timezone based on physical address
  `pip install timezonefinder==3.4.2`

## Installation

Follow these steps to prepare the environment and being using the modules.

**STEP 1.**  Locate your ansible library path: `ansible --version`

```shell
vagrant@ubuntu-xenial:~$ ansible --version
ansible 2.7.9
  config file = /etc/ansible/ansible.cfg
  configured module search path = [u'/home/vagrant/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/dist-packages/ansible
  executable location = /usr/bin/ansible
  python version = 2.7.12 (default, Nov 12 2018, 14:36:49) [GCC 5.4.0 20160609]
```

**STEP 2.**  Change to the ansible library path: example: `cd /Library/Python/2.7/site-packages/ansible`

```shell
vagrant@ubuntu-xenial:~$ cd /usr/lib/python2.7/dist-packages/ansible

```

**STEP 3.**  Create a new directory in module_utils/network named dnac: `mkdir module_utils/network/dnac`

```shell
vagrant@ubuntu-xenial:/usr/lib/python2.7/dist-packages/ansible$ sudo mkdir module_utils/network/dnac
```

**STEP 4.**  Copy file `dnac.py` to module_utils/network/dnac folder

```shell
vagrant@ubuntu-xenial:/usr/lib/python2.7/dist-packages/ansible$ sudo cp ~/ansible-dnac-modules/dnac.py module_utils/network/dnac/.
```

**STEP 5.**  Copy all other *.py files to the location of your ansible custom modules. (mine is /usr/share/ansible)

```shell
​```shell
vagrant@ubuntu-xenial:~/ansible-dnac-modules$ sudo mkdir -p /usr/share/ansible/plugins/modules
vagrant@ubuntu-xenial:~/ansible-dnac-modules$ sudo cp *.py /usr/share/ansible/plugins/modules
vagrant@ubuntu-xenial:~/ansible-dnac-modules$ ls /usr/share/ansible/plugins/modules
dnac_activate_credential.py  dnac_cli_credential.py       dnac_device_role.py  dnac_dns.py     dnac_netflow.py  dnac_snmp.py               dnac_timezone.py
dnac_archive_config.py       dnac_del_archived_config.py  dnac_dhcp.py         dnac_group.py   dnac_ntp.py      dnac_snmpv2_credential.py
dnac_banner.py               dnac_device_assign_site.py   dnac_discovery.py    dnac_ippool.py  dnac.py          dnac_syslog.py

```

**STEP 6.**  Validation that the modules have been installed properly can be performed by executing:

`ansible-doc dnac_dhcp`

If the results show the module documentation your installation was successful.

```shell
vagrant@ubuntu-xenial:~/ansible-dnac-modules$ ansible-doc dnac_dhcp
> DNAC_DHCP    (/home/vagrant/ansible-dnac-modules/dnac_dhcp.py)

        Add or delete DHCP Server(s) in the Cisco DNA Center Design Workflow.  The DHCP Severs can be different values \ at different
        levels in the group hierarchy.

OPTIONS (= is mandatory):

= dhcp_servers
        IP address of the DHCP Server to manipulate.

        type: list
```

## Examples

The examples below set the common-settings in the DNA Center Design workflow.  Additional examples are included in the module documentation.  `ansible-doc *module_name*`

```yaml
name: test my new module
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

## Author

**Jeff Andiorio** - World Wide Technology