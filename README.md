# Ansible Collection - wwt.ansible_dnac

## Ansible Modules for DNA Center

These modules provide declarative and idempotent access to configure the design elements of [Cisco's DNA Center](https://www.cisco.com/c/en/us/products/cloud-systems.../dna-center/index.html).

### DevNet Code Exchange

This repository is featured on the Cisco DevNet Code Exchange.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/jandiorio/ansible-dnac-modules)


### Content

* The webinar below was hosted by Redhat and delivered by Jeff Andiorio of World Wide Technology on 8/7/2018.

   [WWT / Redhat Ansible Webinar](https://www.ansible.com/resources/webinars-training/lab-automation-by-wwt-with-ansible-tower-and-cisco-dna-center)

* AnsibleFest 2019 Presentation

   [DO I CHOOSE ANSIBLE, DNA CENTER OR BOTH?](https://www.ansible.com/do-i-choose-ansible-dna-center-or-both)

* Additional slides providing an overview of the modules can be found here:

   [Ansible DNA Center Modules Overview](https://www.slideshare.net/secret/1l5xe5ORzTN3Uv)

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

## Inventory Plugin

This collection also includes an inventory plugin enabling the use of DNA Center as the source of truth for inventory.

1. Install the collection
   ```shell
   ansible-galaxy install wwt.ansible.dnac
   ```
2. Configure the plugin by editing the `dna_center.yml` plugin configuration file
   ```yaml
   plugin: dna_center
   host: <your_dna_center>
   validate_certs: <true or false>
   use_dnac_mgmt_int: <true or false>
   username: <username>
   password: <vaulted password>
   ```
3. Enable the plugin by editing `ansible.cfg`

   ```ini
   [inventory]
   enable_plugins =  wwt.ansible_dnac.dna_center
   ```

4. Validate it works

   ```shell
   ansible-inventory -i plugins/inventory/ --graph --ask-vault-pass
   ```

   **Example output:**

   ```shell
    @all:
      |--@barcelona:
      |--@demo_environment:
      |  |--@data_center_1:
      |  |  |--DC1-Border-INET.campus.local
      |  |  |--DC1-Border-MPLS.campus.local
      |  |  |--csr-atc-integration.campus.local
      |  |  |--dc1-nexus-7702.campus.local
      |  |--@data_center_2:
      |--@fira:
      |--@tech_campus:
      |  |--@bldg_56:
      |  |  |--@dnac:
      |  |  |  |--dc1-9300-a.campus.local
      |  |  |  |--dc1-9300-b.campus.local
      |  |  |  |--dc1-9500-a.campus.local
      |  |  |  |--prod-9800wlc-01.campus.local
      |--@the_cloud:
      |  |--@aws:
      |  |  |--FNH-HOSP-0BMT-WLC1A.us-east-2.compute.internal
      |--@ungrouped:
    /development/wwt/ansible_dnac #
   ```

## Geo Lookup Plugin

This collection includes a lookup plugin which performs a resolution of the location provided to return the latitude and longitude.  When adding buildings in DNAC, an address is required as well as the lat/long of that address.  In the UI this resolution is performed for you.  This plugin provides that functionality in this collection.

Below is an example task using the `geo` plugin.

```yaml
# DNA Center Create Buildings
- name: create buildings
  dnac_site:
    host: "{{ inventory_hostname }}"
    port: '443'
    username: "{{ username }}"
    password: "{{ password }}"
    state: "{{ desired_state }}"
    name: "{{ item.name }}"
    site_type: "{{ item.site_type }}"
    parent_name: "{{ item.parent_name }}"
    address: "{{ item.building_address }}"
    latitude: "{{ lookup('wwt.ansible_dnac.geo',item.building_address).latitude }}"
    longitude: "{{ lookup('wwt.ansible_dnac.geo',item.building_address).longitude }}"
  loop: "{{ sites }}"
  when:  item.site_type == 'building'
```

> **NOTE:** The `geo` lookup plugin is completely optional.  Alternatively, you could manually resolve the lat/long and include them in the task.  See the `dnac_site` module documentation for more information.

## Requirements

Ansible version 2.9 or later is required for installation using Ansible Collections.

This solution requires the installation of the following python modules:

- **geopy** to resolve building addresses and populate lat/long
  `pip install geopy`
- **requests** for http requests
  `pip install requests`
- **timezonefinder** for resolving the timezone based on physical address
  `pip install timezonefinder==3.4.2`

## Installation

These Ansible modules have now been packaged into an Ansible Collection.

**STEP 1.** Install the `ansible_dnac` collection

```shell
ansible-galaxy install wwt.ansible_dnac
```

**STEP 2.**  Validation that the modules have been installed properly can be performed by executing:

`ansible-doc wwt.ansible_dnac.dnac_dhcp`

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

collections:
  - wwt.ansible_dnac

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
