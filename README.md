# ansible_dnac

## EXAMPLES
The examples below set the common-settings in the DNA Center Design workflow

```
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
