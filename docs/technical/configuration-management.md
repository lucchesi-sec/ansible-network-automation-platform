# Configuration Management Guide

## Managing Variables, Inventory, and Secrets

This comprehensive guide covers all aspects of configuration management in the Ansible Cloud & Network Automation Platform. You'll learn how to effectively manage variables, inventory files, secrets, and environment-specific configurations across both the interactive and enterprise systems.

## Configuration Architecture Overview

### Configuration Hierarchy

The platform uses a hierarchical configuration system:

```
Configuration Priority (highest to lowest):
1. Command-line extra variables (-e)
2. Task-level variables
3. Host variables (host_vars/)
4. Group variables (group_vars/)
5. Play variables
6. Role defaults (roles/*/defaults/)
7. Inventory variables
```

### Configuration Locations

```
ansible-cloud-playbook/
├── vars/                           # Root-level environment variables
│   ├── development.yml            # Development environment
│   ├── production.yml             # Production environment
│   └── aws_config.yml            # AWS-specific configuration
├── inventory/                      # Root-level inventory files
│   ├── hosts.yml                  # Static inventory
│   └── aws_ec2.yml               # Dynamic AWS inventory
├── src/cisco_network_automation/   # Enterprise system configuration
│   ├── group_vars/                # Enterprise group variables
│   │   ├── all.yml               # Global variables
│   │   ├── core_routers.yml      # Core router specific
│   │   ├── vault.yml             # Encrypted secrets
│   │   └── [device_groups].yml   # Device group specific
│   ├── host_vars/                 # Host-specific variables
│   │   └── [hostname].yml        # Individual device config
│   └── inventory/                 # Enterprise inventory files
│       ├── production.yml        # Production inventory
│       └── security_ai.yml       # Security AI inventory
```

## Variable Management

### Understanding Variable Types

#### Global Variables (group_vars/all.yml)
```yaml
---
# Global configuration applicable to all devices
ansible_connection: network_cli
ansible_network_os: ios
ansible_become: true
ansible_become_method: enable

# Timeout settings
ansible_command_timeout: 60
ansible_connect_timeout: 30

# Logging configuration
log_path: "./logs/ansible.log"
enable_logging: true

# Default credentials (use vault for production)
default_username: "admin"
default_enable_password: "{{ vault_default_enable_password }}"

# Common network settings
ntp_servers:
  - "0.pool.ntp.org"
  - "1.pool.ntp.org"
  - "2.pool.ntp.org"

dns_servers:
  - "8.8.8.8"
  - "8.8.4.4"
  - "1.1.1.1"

# SNMP community strings
snmp_ro_community: "{{ vault_snmp_ro_community }}"
snmp_rw_community: "{{ vault_snmp_rw_community }}"
```

#### Device Group Variables (group_vars/[group].yml)
```yaml
---
# Core Router specific configuration
# File: group_vars/core_routers.yml

# BGP Configuration
bgp_asn: 65000
bgp_router_id_base: "10.0.1"

bgp_neighbors:
  - peer_ip: "10.0.1.2"
    remote_as: 65000
    description: "iBGP peer to core-rtr-02"
  - peer_ip: "10.0.2.1"
    remote_as: 65001
    description: "eBGP peer to partner AS"

# OSPF Configuration
ospf_process_id: 1
ospf_area: "0.0.0.0"
ospf_networks:
  - network: "10.0.0.0"
    wildcard: "0.0.255.255"
    area: "0.0.0.0"

# QoS Configuration
qos_policies:
  - name: "CORE_QOS_POLICY"
    classes:
      - name: "VOICE"
        priority: "high"
        bandwidth_percent: 30
      - name: "DATA"
        priority: "normal"
        bandwidth_percent: 50
      - name: "BULK"
        priority: "low"
        bandwidth_percent: 20

# Interface Configuration
core_interfaces:
  - name: "GigabitEthernet0/0/0"
    description: "Core uplink to spine-01"
    ip_address: "10.1.1.1"
    subnet_mask: "255.255.255.252"
    ospf_area: "0.0.0.0"
  - name: "GigabitEthernet0/0/1"
    description: "Core uplink to spine-02"
    ip_address: "10.1.1.5"
    subnet_mask: "255.255.255.252"
    ospf_area: "0.0.0.0"
```

#### Host-Specific Variables (host_vars/[hostname].yml)
```yaml
---
# Host-specific configuration
# File: host_vars/core-rtr-01.yml

# Device-specific settings
hostname: "core-rtr-01"
mgmt_ip: "10.0.100.1"
mgmt_interface: "GigabitEthernet0/0"

# BGP Router ID (host-specific)
bgp_router_id: "10.0.1.1"

# Device-specific interfaces
interfaces:
  - name: "GigabitEthernet0/0/0"
    description: "Uplink to dist-rtr-01"
    ip_address: "10.1.2.1"
    subnet_mask: "255.255.255.252"
    vrf: "default"
  - name: "GigabitEthernet0/0/1"
    description: "Uplink to dist-rtr-02"
    ip_address: "10.1.2.5"
    subnet_mask: "255.255.255.252"
    vrf: "default"

# VLAN configuration (if applicable)
vlans:
  - id: 100
    name: "MGMT"
    description: "Management VLAN"
  - id: 200
    name: "DATA"
    description: "Data VLAN"
  - id: 300
    name: "VOICE"
    description: "Voice VLAN"

# Device-specific credentials
ansible_user: "{{ vault_core_rtr_01_username }}"
ansible_password: "{{ vault_core_rtr_01_password }}"
ansible_become_password: "{{ vault_core_rtr_01_enable }}"
```

### Environment-Specific Variables

#### Development Environment (vars/development.yml)
```yaml
---
# Development Environment Configuration
environment: "development"

# AWS Configuration
aws_region: "us-east-1"
availability_zone: "us-east-1a"

# EC2 Instance Configuration
instance_type: "t3.micro"
ami_id: "ami-0c55b159cbfafe1d0"  # Amazon Linux 2
key_name: "dev-keypair"

# Security Configuration (Relaxed for development)
security_group_name: "ansible-sg-dev"
security_group_rules:
  - proto: tcp
    ports: [22]
    cidr_ip: "0.0.0.0/0"
    rule_desc: "SSH access"
  - proto: tcp
    ports: [80, 443]
    cidr_ip: "0.0.0.0/0"
    rule_desc: "Web access"
  - proto: icmp
    from_port: -1
    to_port: -1
    cidr_ip: "0.0.0.0/0"
    rule_desc: "ICMP ping"

# Network Configuration
vpc_cidr: "10.10.0.0/16"
subnet_cidr: "10.10.1.0/24"

# Development-specific settings
enable_debug: true
log_level: "debug"
backup_retention_days: 7
enable_performance_monitoring: false

# Tagging
tags:
  Environment: "development"
  Project: "ansible-automation"
  Owner: "dev-team"
  CostCenter: "engineering"
```

#### Production Environment (vars/production.yml)
```yaml
---
# Production Environment Configuration
environment: "production"

# AWS Configuration
aws_region: "us-west-2"
availability_zone: "us-west-2a"

# EC2 Instance Configuration (Production-sized)
instance_type: "t3.large"
ami_id: "ami-0c55b159cbfafe1d0"
key_name: "prod-keypair"

# Enhanced Security Configuration
security_group_name: "ansible-sg-prod"
security_group_rules:
  - proto: tcp
    ports: [22]
    cidr_ip: "10.0.0.0/8"  # Restricted to internal networks
    rule_desc: "SSH access from corporate"
  - proto: tcp
    ports: [443]
    cidr_ip: "0.0.0.0/0"
    rule_desc: "HTTPS access"
  # Note: No HTTP or ICMP for production security

# Network Configuration (Production VPC)
vpc_cidr: "10.0.0.0/16"
subnet_cidr: "10.0.1.0/24"

# Production-specific settings
enable_debug: false
log_level: "info"
backup_retention_days: 90
enable_performance_monitoring: true
enable_security_monitoring: true
enable_compliance_logging: true

# High Availability Configuration
multi_az_deployment: true
enable_auto_scaling: true
min_instances: 2
max_instances: 10

# Tagging (Production)
tags:
  Environment: "production"
  Project: "ansible-automation"
  Owner: "ops-team"
  CostCenter: "operations"
  Backup: "required"
  Monitoring: "critical"
```

## Inventory Management

### Static Inventory Configuration

#### Basic Static Inventory (inventory/hosts.yml)
```yaml
---
all:
  children:
    # Network Devices
    network_devices:
      children:
        switches:
          hosts:
            switch-01:
              ansible_host: 192.168.1.10
              device_type: "catalyst_2960"
              location: "rack_a_01"
            switch-02:
              ansible_host: 192.168.1.11
              device_type: "catalyst_3560"
              location: "rack_a_02"
        routers:
          hosts:
            router-01:
              ansible_host: 192.168.1.1
              device_type: "isr_4000"
              location: "comm_room_01"
            router-02:
              ansible_host: 192.168.1.2
              device_type: "isr_4000"
              location: "comm_room_02"
    
    # AWS Infrastructure
    aws_instances:
      hosts:
        web-server-01:
          ansible_host: "{{ web_server_01_ip }}"
          instance_id: "i-1234567890abcdef0"
          instance_type: "t3.medium"
        web-server-02:
          ansible_host: "{{ web_server_02_ip }}"
          instance_id: "i-0987654321fedcba0"
          instance_type: "t3.medium"

  vars:
    # Global connection settings
    ansible_connection: network_cli
    ansible_network_os: ios
    ansible_become: true
    ansible_become_method: enable
    
    # Timeout settings
    ansible_command_timeout: 60
    ansible_connect_timeout: 30
```

#### Enterprise Static Inventory (src/cisco_network_automation/inventory/production.yml)
```yaml
---
all:
  children:
    # Core Network Infrastructure
    core_infrastructure:
      children:
        core_routers:
          hosts:
            core-rtr-01:
              ansible_host: "10.1.1.1"
              device_role: "core_router"
              site: "datacenter_01"
              rack: "core_rack_01"
              bgp_router_id: "10.0.1.1"
            core-rtr-02:
              ansible_host: "10.1.1.2"
              device_role: "core_router"
              site: "datacenter_01"
              rack: "core_rack_02"
              bgp_router_id: "10.0.1.2"
        
        distribution_routers:
          hosts:
            dist-rtr-01:
              ansible_host: "10.1.2.1"
              device_role: "distribution_router"
              site: "datacenter_01"
              rack: "dist_rack_01"
            dist-rtr-02:
              ansible_host: "10.1.2.2"
              device_role: "distribution_router"
              site: "datacenter_01"
              rack: "dist_rack_02"
        
        edge_routers:
          hosts:
            edge-rtr-01:
              ansible_host: "10.1.3.1"
              device_role: "edge_router"
              site: "branch_office_01"
            edge-rtr-02:
              ansible_host: "10.1.3.2"
              device_role: "edge_router"
              site: "branch_office_02"

    # Data Center Fabric
    datacenter_fabric:
      children:
        datacenter_fabric_switches:
          hosts:
            spine-01:
              ansible_host: "10.2.1.1"
              device_role: "spine_switch"
              fabric_role: "spine"
              asn: 65001
            spine-02:
              ansible_host: "10.2.1.2"
              device_role: "spine_switch"
              fabric_role: "spine"
              asn: 65002
            leaf-01:
              ansible_host: "10.2.2.1"
              device_role: "leaf_switch"
              fabric_role: "leaf"
              asn: 65101
            leaf-02:
              ansible_host: "10.2.2.2"
              device_role: "leaf_switch"
              fabric_role: "leaf"
              asn: 65102

    # Security Infrastructure
    security_infrastructure:
      children:
        perimeter_routers:
          hosts:
            perimeter-rtr-01:
              ansible_host: "10.3.1.1"
              device_role: "perimeter_router"
              security_zone: "dmz"
            perimeter-rtr-02:
              ansible_host: "10.3.1.2"
              device_role: "perimeter_router"
              security_zone: "dmz"
        
        microsegmentation_switches:
          hosts:
            microseg-sw-01:
              ansible_host: "10.3.2.1"
              device_role: "microsegmentation_switch"
              security_profile: "high"
            microseg-sw-02:
              ansible_host: "10.3.2.2"
              device_role: "microsegmentation_switch"
              security_profile: "high"

  vars:
    # Global enterprise settings
    ansible_connection: network_cli
    ansible_network_os: ios
    ansible_become: true
    ansible_become_method: enable
    ansible_user: "{{ vault_global_username }}"
    ansible_password: "{{ vault_global_password }}"
    ansible_become_password: "{{ vault_global_enable_password }}"
    
    # Enterprise-specific settings
    enterprise_domain: "enterprise.local"
    ntp_servers: ["10.0.100.1", "10.0.100.2"]
    syslog_servers: ["10.0.101.1", "10.0.101.2"]
    snmp_location: "Primary Datacenter"
    snmp_contact: "Network Operations Center"
```

### Dynamic Inventory Configuration

#### AWS Dynamic Inventory (inventory/aws_ec2.yml)
```yaml
---
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2

# Inventory grouping
keyed_groups:
  # Group by instance type
  - key: instance_type
    prefix: instance_type
  
  # Group by VPC
  - key: vpc_id
    prefix: vpc
  
  # Group by availability zone
  - key: placement.availability_zone
    prefix: az
  
  # Group by environment tag
  - key: tags.Environment | default('unknown')
    prefix: env
  
  # Group by project tag
  - key: tags.Project | default('unknown')
    prefix: project

# Include/exclude filters
filters:
  # Only running instances
  instance-state-name: running
  
  # Only instances with specific tags
  "tag:Project": "ansible-automation"

# Host variables to include
hostvar_templates:
  ansible_host: public_ip_address | default(private_ip_address)
  ec2_instance_id: instance_id
  ec2_instance_type: instance_type
  ec2_placement_az: placement.availability_zone
  ec2_vpc_id: vpc_id
  ec2_subnet_id: subnet_id
  ec2_security_groups: security_groups | map(attribute='group_name') | list

# Compose custom variables
compose:
  # Create a custom ansible_host based on environment
  ansible_host: |
    public_ip_address if (tags.Environment == 'development') 
    else private_ip_address
  
  # Create environment-specific connection settings
  ansible_user: |
    'ec2-user' if (platform == 'linux') 
    else 'Administrator'
  
  # Create custom grouping variables
  server_role: tags.Role | default('generic')
  environment: tags.Environment | default('unknown')
```

#### Advanced Dynamic Inventory with Custom Plugin
```python
#!/usr/bin/env python3
# inventory/custom_network_inventory.py

"""
Custom dynamic inventory for network devices
Integrates with CMDB or network discovery tools
"""

import json
import sys
import requests
from urllib.parse import urljoin

class NetworkInventory:
    def __init__(self):
        self.inventory = {
            '_meta': {
                'hostvars': {}
            }
        }
        self.cmdb_url = "https://cmdb.company.com/api/v1/"
        self.api_key = "your-api-key"
    
    def get_inventory(self):
        """Fetch inventory from CMDB"""
        devices = self._fetch_devices()
        
        for device in devices:
            self._add_device(device)
        
        return self.inventory
    
    def _fetch_devices(self):
        """Fetch devices from CMDB API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = urljoin(self.cmdb_url, 'network-devices')
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    
    def _add_device(self, device):
        """Add device to inventory"""
        hostname = device['hostname']
        device_type = device['device_type']
        location = device['location']
        
        # Create groups based on device type
        if device_type not in self.inventory:
            self.inventory[device_type] = {
                'hosts': [],
                'vars': {}
            }
        
        # Create groups based on location
        location_group = f"location_{location}"
        if location_group not in self.inventory:
            self.inventory[location_group] = {
                'hosts': [],
                'vars': {}
            }
        
        # Add host to groups
        self.inventory[device_type]['hosts'].append(hostname)
        self.inventory[location_group]['hosts'].append(hostname)
        
        # Add host variables
        self.inventory['_meta']['hostvars'][hostname] = {
            'ansible_host': device['management_ip'],
            'device_type': device_type,
            'location': location,
            'model': device['model'],
            'os_version': device['os_version'],
            'ansible_network_os': device['network_os'],
            'ansible_connection': 'network_cli',
            'ansible_become': True,
            'ansible_become_method': 'enable'
        }

if __name__ == '__main__':
    inventory = NetworkInventory()
    print(json.dumps(inventory.get_inventory(), indent=2))
```

## Secrets Management with Ansible Vault

### Creating and Managing Vault Files

#### Creating a New Vault File
```bash
# Create new vault file
ansible-vault create group_vars/vault.yml

# Edit existing vault file
ansible-vault edit group_vars/vault.yml

# View vault file contents
ansible-vault view group_vars/vault.yml

# Change vault password
ansible-vault rekey group_vars/vault.yml
```

#### Vault File Structure (group_vars/vault.yml)
```yaml
---
# Network Device Credentials
vault_global_username: "netadmin"
vault_global_password: "SuperSecurePassword123!"
vault_global_enable_password: "SuperSecureEnable456!"

# Device-specific credentials
vault_core_rtr_01_username: "admin"
vault_core_rtr_01_password: "CoreRouter01Pass!"
vault_core_rtr_01_enable: "CoreRouter01Enable!"

vault_core_rtr_02_username: "admin"
vault_core_rtr_02_password: "CoreRouter02Pass!"
vault_core_rtr_02_enable: "CoreRouter02Enable!"

# SNMP Credentials
vault_snmp_ro_community: "ReadOnlyCommunity123"
vault_snmp_rw_community: "ReadWriteCommunity456"
vault_snmp_v3_auth_password: "SNMPv3AuthPass789"
vault_snmp_v3_priv_password: "SNMPv3PrivPass012"

# API Keys and Tokens
vault_aws_access_key: "AKIAIOSFODNN7EXAMPLE"
vault_aws_secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Database Credentials
vault_db_username: "dbadmin"
vault_db_password: "DatabasePassword789!"

# Certificate Passphrases
vault_ssl_cert_passphrase: "SSLCertPassphrase321!"

# Backup Encryption Keys
vault_backup_encryption_key: "BackupEncryptionKey654!"

# External Service Credentials
vault_monitoring_api_key: "monitoring-api-key-abc123"
vault_backup_service_token: "backup-service-token-def456"
```

### Vault Password Management

#### Setting Up Vault Password Files
```bash
# Create vault password file
echo "your-vault-password" > vault-password-script.sh
chmod 700 vault-password-script.sh

# Add to .gitignore
echo "vault-password-script.sh" >> .gitignore
echo "*.vault" >> .gitignore
```

#### Advanced Vault Password Script
```bash
#!/bin/bash
# vault-password-script.sh

# Advanced vault password script with multiple sources

# Try environment variable first
if [ -n "$ANSIBLE_VAULT_PASSWORD" ]; then
    echo "$ANSIBLE_VAULT_PASSWORD"
    exit 0
fi

# Try reading from secure file
VAULT_FILE="$HOME/.ansible/vault_password"
if [ -f "$VAULT_FILE" ]; then
    cat "$VAULT_FILE"
    exit 0
fi

# Try reading from keyring (macOS)
if command -v security >/dev/null 2>&1; then
    security find-generic-password -w -s "ansible-vault" -a "$USER" 2>/dev/null
    if [ $? -eq 0 ]; then
        exit 0
    fi
fi

# Fallback to prompting user
echo "Vault password not found in environment or keyring" >&2
read -s -p "Enter vault password: " password
echo "$password"
```

### Multiple Vault IDs

#### Using Multiple Vault Files
```bash
# Create vault files with different IDs
ansible-vault create --vault-id dev@prompt group_vars/vault_dev.yml
ansible-vault create --vault-id prod@prompt group_vars/vault_prod.yml

# Use specific vault ID
ansible-playbook -i inventory/production.yml \
  --vault-id prod@vault-password-script.sh \
  playbooks/deploy.yml
```

#### Vault ID Configuration
```ini
# ansible.cfg
[defaults]
vault_identity_list = dev@dev-vault-pass.sh, prod@prod-vault-pass.sh
```

### Encrypting Individual Variables

#### Encrypting Specific Variables
```bash
# Encrypt individual string
ansible-vault encrypt_string "sensitive-password" --name vault_password

# Result to add to YAML file:
vault_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653765386661373563343938366463646433643630623134376636353762373030626533
          3163356432643062663637366235626265616363336136380a666635613735386464363834376361
          38366431653964393734646463633765373063656135343233376138343730316233646261663164
          3866653637653936312a633964613065666536343936376338633236633937653037663361303831
          3662
```

## Configuration Templates and Customization

### Jinja2 Templates for Configuration

#### Basic Template Structure
```jinja2
{# templates/ios_base_config.j2 #}
!
! Generated by Ansible on {{ ansible_date_time.iso8601 }}
! Device: {{ inventory_hostname }}
! Role: {{ device_role | default('unknown') }}
!
hostname {{ hostname | default(inventory_hostname) }}
!
{% if domain_name is defined %}
ip domain-name {{ domain_name }}
{% endif %}

! NTP Configuration
{% for ntp_server in ntp_servers %}
ntp server {{ ntp_server }}
{% endfor %}

! DNS Configuration
{% for dns_server in dns_servers %}
ip name-server {{ dns_server }}
{% endfor %}

! SNMP Configuration
{% if snmp_ro_community is defined %}
snmp-server community {{ snmp_ro_community }} RO
{% endif %}
{% if snmp_rw_community is defined %}
snmp-server community {{ snmp_rw_community }} RW
{% endif %}
snmp-server location {{ snmp_location | default('Unknown') }}
snmp-server contact {{ snmp_contact | default('Unknown') }}

! Interface Configuration
{% for interface in interfaces | default([]) %}
interface {{ interface.name }}
 description {{ interface.description | default('') }}
 {% if interface.ip_address is defined %}
 ip address {{ interface.ip_address }} {{ interface.subnet_mask }}
 {% endif %}
 {% if interface.shutdown is defined and interface.shutdown %}
 shutdown
 {% else %}
 no shutdown
 {% endif %}
!
{% endfor %}

! VLAN Configuration (for switches)
{% if device_type is defined and 'switch' in device_type %}
{% for vlan in vlans | default([]) %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
!
{% endfor %}
{% endif %}

! BGP Configuration
{% if bgp_asn is defined %}
router bgp {{ bgp_asn }}
 bgp router-id {{ bgp_router_id }}
 bgp log-neighbor-changes
 {% for neighbor in bgp_neighbors | default([]) %}
 neighbor {{ neighbor.peer_ip }} remote-as {{ neighbor.remote_as }}
 neighbor {{ neighbor.peer_ip }} description {{ neighbor.description }}
 {% if neighbor.remote_as == bgp_asn %}
 neighbor {{ neighbor.peer_ip }} next-hop-self
 {% endif %}
 {% endfor %}
 !
 address-family ipv4
  {% for neighbor in bgp_neighbors | default([]) %}
  neighbor {{ neighbor.peer_ip }} activate
  {% endfor %}
  {% for network in bgp_networks | default([]) %}
  network {{ network.prefix }} mask {{ network.mask }}
  {% endfor %}
 exit-address-family
!
{% endif %}

! OSPF Configuration
{% if ospf_process_id is defined %}
router ospf {{ ospf_process_id }}
 router-id {{ ospf_router_id | default(ansible_host) }}
 log-adjacency-changes
 {% for network in ospf_networks | default([]) %}
 network {{ network.network }} {{ network.wildcard }} area {{ network.area }}
 {% endfor %}
!
{% endif %}

! Access Control Lists
{% for acl in access_lists | default([]) %}
ip access-list {{ acl.type }} {{ acl.name }}
{% for rule in acl.rules %}
 {{ rule }}
{% endfor %}
!
{% endfor %}

! End of configuration
end
```

#### Advanced Template with Conditionals
```jinja2
{# templates/advanced_switch_config.j2 #}

! Advanced Switch Configuration Template
! Supports multiple device types and features

{% set device_model = hostvars[inventory_hostname]['device_model'] | default('unknown') %}
{% set is_stack = 'stack' in device_model.lower() %}
{% set supports_vxlan = device_model in ['nexus_9000', 'catalyst_9000'] %}

!
hostname {{ hostname }}
!

{% if is_stack %}
! Stack Configuration
switch {{ stack_member | default(1) }} priority {{ stack_priority | default(1) }}
switch {{ stack_member | default(1) }} provision {{ device_model }}
{% endif %}

! VLAN Configuration with Enhanced Features
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
 {% if vlan.description is defined %}
 description {{ vlan.description }}
 {% endif %}
 {% if supports_vxlan and vlan.vni is defined %}
 vn-segment {{ vlan.vni }}
 {% endif %}
!
{% endfor %}

! STP Configuration based on protocol
{% if stp_mode is defined %}
spanning-tree mode {{ stp_mode }}
{% if stp_mode == 'rapid-pvst' %}
spanning-tree extend system-id
spanning-tree vlan {{ vlans | map(attribute='id') | join(',') }} priority {{ stp_priority | default(32768) }}
{% elif stp_mode == 'mst' %}
spanning-tree mst configuration
 {% for instance in mst_instances | default([]) %}
 instance {{ instance.id }} vlan {{ instance.vlans | join(',') }}
 {% endfor %}
 name {{ mst_name | default('REGION1') }}
 revision {{ mst_revision | default(1) }}
!
{% endif %}
{% endif %}

! Interface Configuration with Advanced Features
{% for interface in interfaces %}
interface {{ interface.name }}
 description {{ interface.description | default('') }}
 
 {% if interface.type == 'access' %}
 switchport mode access
 switchport access vlan {{ interface.vlan }}
 {% elif interface.type == 'trunk' %}
 switchport mode trunk
 switchport trunk allowed vlan {{ interface.allowed_vlans | default('all') }}
 {% if interface.native_vlan is defined %}
 switchport trunk native vlan {{ interface.native_vlan }}
 {% endif %}
 {% endif %}
 
 {% if interface.port_security is defined and interface.port_security %}
 switchport port-security
 switchport port-security maximum {{ interface.max_mac | default(1) }}
 switchport port-security violation {{ interface.violation_action | default('shutdown') }}
 switchport port-security mac-address sticky
 {% endif %}
 
 {% if interface.storm_control is defined %}
 storm-control broadcast level {{ interface.storm_control.broadcast | default('10.00') }}
 storm-control multicast level {{ interface.storm_control.multicast | default('10.00') }}
 storm-control unicast level {{ interface.storm_control.unicast | default('10.00') }}
 {% endif %}
 
 {% if interface.qos_policy is defined %}
 service-policy input {{ interface.qos_policy }}
 {% endif %}
 
 {% if interface.shutdown is defined and interface.shutdown %}
 shutdown
 {% else %}
 no shutdown
 {% endif %}
!
{% endfor %}

{% if supports_vxlan and enable_vxlan | default(false) %}
! VXLAN Configuration
feature vn-segment-vlan-based
feature nv overlay

interface nve1
 no shutdown
 source-interface loopback1
 {% for vlan in vlans %}
 {% if vlan.vni is defined %}
 member vni {{ vlan.vni }}
  ingress-replication protocol bgp
 {% endif %}
 {% endfor %}
!
{% endif %}

! QoS Configuration
{% for qos_policy in qos_policies | default([]) %}
class-map match-all {{ qos_policy.name }}_CLASS
 match access-group {{ qos_policy.acl }}
!
policy-map {{ qos_policy.name }}_POLICY
 class {{ qos_policy.name }}_CLASS
  set dscp {{ qos_policy.dscp | default('af31') }}
  police {{ qos_policy.rate | default('100000000') }} {{ qos_policy.burst | default('1875000') }} exceed-action drop
!
{% endfor %}

end
```

### Custom Configuration Modules

#### Custom Ansible Module for Advanced Configuration
```python
#!/usr/bin/python

# custom_modules/cisco_advanced_config.py

DOCUMENTATION = '''
---
module: cisco_advanced_config
short_description: Advanced Cisco device configuration
description:
    - Provides advanced configuration capabilities for Cisco devices
    - Supports template-based configuration with validation
version_added: "1.0"
author: "Network Team"
options:
    template:
        description:
            - Configuration template to apply
        required: true
        type: str
    variables:
        description:
            - Variables to use in template
        required: false
        type: dict
    validate:
        description:
            - Validate configuration before applying
        required: false
        default: true
        type: bool
    backup:
        description:
            - Create backup before applying configuration
        required: false
        default: true
        type: bool
'''

EXAMPLES = '''
- name: Apply advanced switch configuration
  cisco_advanced_config:
    template: "advanced_switch_config.j2"
    variables:
      vlans: "{{ switch_vlans }}"
      interfaces: "{{ switch_interfaces }}"
    validate: true
    backup: true
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.common.utils import ComplexDict
from ansible.module_utils.network.ios.ios import ios_argument_spec, check_args
from ansible.module_utils.network.ios.ios import load_config, run_commands

def main():
    element_spec = dict(
        template=dict(type='str', required=True),
        variables=dict(type='dict', default={}),
        validate=dict(type='bool', default=True),
        backup=dict(type='bool', default=True)
    )
    
    aggregate_spec = deepcopy(element_spec)
    
    argument_spec = dict(
        aggregate=dict(type='list', elements='dict', options=aggregate_spec),
    )
    
    argument_spec.update(element_spec)
    argument_spec.update(ios_argument_spec)
    
    module = AnsibleModule(argument_spec=argument_spec,
                         supports_check_mode=True)
    
    result = {'changed': False}
    
    # Implementation would go here
    # This is a simplified example
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

## Environment-Specific Configuration Strategies

### Configuration Inheritance

#### Base Configuration (group_vars/all.yml)
```yaml
---
# Base configuration inherited by all environments

# Global settings
ansible_connection: network_cli
ansible_network_os: ios
ansible_become: true
ansible_become_method: enable

# Common timeouts
ansible_command_timeout: 60
ansible_connect_timeout: 30

# Base network configuration
base_vlans:
  - { id: 1, name: "default" }
  - { id: 999, name: "unused" }

base_ntp_servers:
  - "0.pool.ntp.org"
  - "1.pool.ntp.org"

base_dns_servers:
  - "8.8.8.8"
  - "8.8.4.4"

# Base security settings
base_security:
  enable_ssh: true
  ssh_version: 2
  ssh_timeout: 300
  enable_secret_encrypted: true
  
# Base logging
base_logging:
  enable_local_logging: true
  log_level: "informational"
  enable_syslog: false
```

#### Development Override (group_vars/development.yml)
```yaml
---
# Development environment overrides

# Override base settings for development
environment: "development"

# Extended timeouts for development
ansible_command_timeout: 120
ansible_connect_timeout: 60

# Development-specific VLANs (extends base_vlans)
development_vlans:
  - { id: 100, name: "dev-mgmt" }
  - { id: 101, name: "dev-data" }
  - { id: 102, name: "dev-test" }

# Combine with base VLANs
vlans: "{{ base_vlans + development_vlans }}"

# Development DNS servers (higher timeout tolerance)
dns_servers: "{{ base_dns_servers + ['192.168.1.1'] }}"

# Relaxed security for development
security_settings:
  enable_ssh: "{{ base_security.enable_ssh }}"
  ssh_version: "{{ base_security.ssh_version }}"
  ssh_timeout: 600  # Longer timeout for development
  allow_telnet: true  # Only in development
  snmp_community: "public"  # Simplified SNMP

# Enhanced logging for troubleshooting
logging_settings:
  enable_local_logging: true
  log_level: "debugging"
  enable_syslog: true
  syslog_server: "192.168.1.100"
  enable_console_logging: true

# Development-specific features
development_features:
  enable_debug_commands: true
  allow_config_replacement: true
  skip_validation: false  # Still validate in development
  enable_test_interfaces: true
```

#### Production Override (group_vars/production.yml)
```yaml
---
# Production environment overrides

environment: "production"

# Production VLANs (extends base_vlans)
production_vlans:
  - { id: 10, name: "prod-mgmt" }
  - { id: 20, name: "prod-data" }
  - { id: 30, name: "prod-voice" }
  - { id: 40, name: "prod-guest" }
  - { id: 50, name: "prod-dmz" }

# Combine with base VLANs
vlans: "{{ base_vlans + production_vlans }}"

# Production DNS with internal servers first
dns_servers:
  - "10.0.1.10"
  - "10.0.1.11"
  - "{{ base_dns_servers[0] }}"  # Fallback to public DNS

# Enhanced security for production
security_settings:
  enable_ssh: "{{ base_security.enable_ssh }}"
  ssh_version: "{{ base_security.ssh_version }}"
  ssh_timeout: "{{ base_security.ssh_timeout }}"
  allow_telnet: false  # Never in production
  snmp_community: "{{ vault_production_snmp_community }}"
  enable_port_security: true
  enable_dhcp_snooping: true
  enable_ip_source_guard: true

# Production logging
logging_settings:
  enable_local_logging: true
  log_level: "warnings"  # Less verbose
  enable_syslog: true
  syslog_servers:
    - "10.0.100.10"
    - "10.0.100.11"
  enable_console_logging: false  # Disable console logging
  enable_audit_logging: true

# Production-specific features
production_features:
  enable_debug_commands: false
  allow_config_replacement: false
  skip_validation: false
  enable_backup_validation: true
  enable_compliance_checking: true
  backup_retention_days: 90
```

### Dynamic Configuration Selection

#### Environment Detection Playbook
```yaml
---
# playbooks/detect_environment.yml
- name: Detect and Set Environment Configuration
  hosts: localhost
  gather_facts: false
  vars:
    environment_mappings:
      "192.168.1.0/24": "development"
      "10.10.0.0/16": "staging"
      "10.0.0.0/16": "production"
  
  tasks:
    - name: Detect environment based on inventory
      set_fact:
        detected_environment: >-
          {%- for subnet, env in environment_mappings.items() -%}
            {%- if ansible_host | ipaddr(subnet) -%}
              {{ env }}
            {%- endif -%}
          {%- endfor -%}
      
    - name: Set environment if not already defined
      set_fact:
        environment: "{{ detected_environment | default('unknown') }}"
      when: environment is not defined
    
    - name: Load environment-specific variables
      include_vars: "{{ environment }}.yml"
      when: environment != 'unknown'
    
    - name: Display detected environment
      debug:
        msg: "Detected environment: {{ environment }}"
```

#### Conditional Configuration Loading
```yaml
---
# In any playbook
- name: Load appropriate configuration
  include_vars: "{{ item }}"
  with_first_found:
    - "{{ environment | default('development') }}.yml"
    - "development.yml"  # Fallback
  tags: always

- name: Apply environment-specific configuration
  template:
    src: "{{ item }}"
    dest: "/tmp/{{ inventory_hostname }}_config.txt"
  with_first_found:
    - "{{ environment }}_config.j2"
    - "base_config.j2"  # Fallback template
```

## Validation and Testing

### Configuration Validation

#### Pre-Deployment Validation Playbook
```yaml
---
# playbooks/validate_configuration.yml
- name: Validate Configuration Before Deployment
  hosts: all
  gather_facts: false
  
  tasks:
    - name: Validate required variables are defined
      assert:
        that:
          - hostname is defined
          - ansible_host is defined
          - vlans is defined
          - interfaces is defined
        fail_msg: "Required variables are missing for {{ inventory_hostname }}"
    
    - name: Validate VLAN ID ranges
      assert:
        that:
          - item.id | int >= 1
          - item.id | int <= 4094
          - item.name is defined
          - item.name | length > 0
        fail_msg: "Invalid VLAN configuration: {{ item }}"
      loop: "{{ vlans }}"
    
    - name: Validate interface configuration
      assert:
        that:
          - item.name is defined
          - item.name is match('^[A-Za-z]+[0-9/]+$')
        fail_msg: "Invalid interface name: {{ item.name }}"
      loop: "{{ interfaces }}"
    
    - name: Validate IP addresses
      assert:
        that:
          - item.ip_address | ipaddr
        fail_msg: "Invalid IP address: {{ item.ip_address }}"
      loop: "{{ interfaces }}"
      when: item.ip_address is defined
    
    - name: Validate BGP configuration
      assert:
        that:
          - bgp_asn | int >= 1
          - bgp_asn | int <= 4294967295
          - bgp_router_id | ipaddr
        fail_msg: "Invalid BGP configuration"
      when: bgp_asn is defined
```

#### Syntax Validation
```bash
#!/bin/bash
# scripts/validate_configuration.sh

# Configuration validation script

echo "Starting configuration validation..."

# Check YAML syntax
echo "Validating YAML syntax..."
for file in vars/*.yml group_vars/*.yml host_vars/*.yml inventory/*.yml; do
    if [ -f "$file" ]; then
        python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✓ $file"
        else
            echo "✗ $file - YAML syntax error"
            exit 1
        fi
    fi
done

# Check Jinja2 template syntax
echo "Validating Jinja2 templates..."
for template in templates/*.j2; do
    if [ -f "$template" ]; then
        python3 -c "
from jinja2 import Template, Environment
import sys
try:
    with open('$template', 'r') as f:
        Template(f.read())
    print('✓ $template')
except Exception as e:
    print('✗ $template - Template error:', e)
    sys.exit(1)
"
    fi
done

# Validate inventory syntax
echo "Validating inventory files..."
for inventory in inventory/*.yml; do
    if [ -f "$inventory" ]; then
        ansible-inventory -i "$inventory" --list > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✓ $inventory"
        else
            echo "✗ $inventory - Inventory syntax error"
            exit 1
        fi
    fi
done

# Check for undefined variables in templates
echo "Checking for undefined variables..."
ansible-playbook playbooks/validate_configuration.yml --syntax-check
if [ $? -eq 0 ]; then
    echo "✓ Playbook syntax validation passed"
else
    echo "✗ Playbook syntax validation failed"
    exit 1
fi

echo "All validation checks passed!"
```

### Testing Configuration Changes

#### Configuration Testing Framework
```yaml
---
# playbooks/test_configuration.yml
- name: Test Configuration Changes
  hosts: all
  gather_facts: false
  
  vars:
    test_results: []
  
  tasks:
    - name: Test basic connectivity
      ios_ping:
        dest: "{{ ansible_host }}"
      register: ping_result
      delegate_to: localhost
    
    - name: Add connectivity test result
      set_fact:
        test_results: "{{ test_results + [{'test': 'connectivity', 'host': inventory_hostname, 'result': ping_result.ping_results[0].success}] }}"
    
    - name: Test VLAN configuration
      ios_command:
        commands: "show vlan brief"
      register: vlan_output
    
    - name: Verify VLANs exist
      set_fact:
        vlan_test_passed: "{{ item.id | string in vlan_output.stdout[0] }}"
      loop: "{{ vlans }}"
      register: vlan_tests
    
    - name: Test interface status
      ios_command:
        commands: "show interfaces status"
      register: interface_output
    
    - name: Test routing protocols
      ios_command:
        commands:
          - "show ip route summary"
          - "show ip bgp summary"
          - "show ip ospf neighbor"
      register: routing_output
      ignore_errors: true
    
    - name: Generate test report
      template:
        src: test_report.j2
        dest: "{{ playbook_dir }}/reports/{{ inventory_hostname }}_test_report.txt"
      delegate_to: localhost
```

## Best Practices and Recommendations

### Configuration Management Best Practices

1. **Version Control**
   ```bash
   # Always commit configuration changes
   git add .
   git commit -m "Update production VLAN configuration for security enhancement"
   git tag -a v1.2.3 -m "Production deployment v1.2.3"
   ```

2. **Environment Separation**
   - Use separate inventory files for each environment
   - Implement environment-specific variable files
   - Use Ansible Vault for environment-specific secrets

3. **Variable Naming Conventions**
   ```yaml
   # Good naming conventions
   core_router_bgp_asn: 65000
   distribution_switch_vlans: [10, 20, 30]
   production_snmp_community: "{{ vault_prod_snmp_ro }}"
   
   # Avoid generic names
   asn: 65000  # Too generic
   vlans: [10, 20, 30]  # Context unclear
   community: "public"  # Unclear purpose
   ```

4. **Documentation Standards**
   ```yaml
   ---
   # Core Router Configuration Variables
   # Last updated: 2023-12-10
   # Owner: Network Team
   # Purpose: BGP and OSPF configuration for core routers
   
   # BGP Configuration
   core_router_bgp_asn: 65000          # Primary AS number
   core_router_bgp_router_id: "10.0.1.1"  # BGP router ID
   
   # OSPF Configuration  
   core_router_ospf_process_id: 1       # OSPF process ID
   core_router_ospf_area: "0.0.0.0"    # Backbone area
   ```

5. **Security Best Practices**
   - Always use Ansible Vault for sensitive data
   - Implement least-privilege access
   - Regular rotation of credentials
   - Use SSH keys instead of passwords where possible

### Troubleshooting Configuration Issues

#### Common Issues and Solutions

1. **Variable Precedence Issues**
   ```bash
   # Debug variable values
   ansible-playbook -i inventory/production.yml \
     -e debug_variables=true \
     playbooks/debug_variables.yml
   
   # Check variable precedence
   ansible-inventory -i inventory/production.yml \
     --host core-rtr-01 --vars
   ```

2. **Template Rendering Issues**
   ```bash
   # Test template rendering
   ansible localhost -m template \
     -a "src=templates/ios_config.j2 dest=/tmp/test_config.txt" \
     -e @group_vars/all.yml
   ```

3. **Vault Access Issues**
   ```bash
   # Test vault access
   ansible-vault view group_vars/vault.yml \
     --vault-password-file vault-password-script.sh
   
   # Re-encrypt with new password
   ansible-vault rekey group_vars/vault.yml
   ```

## Conclusion

Effective configuration management is crucial for successful automation at scale. This guide has covered:

✅ **Variable Management**: Hierarchical variable structure and inheritance
✅ **Inventory Management**: Static and dynamic inventory configurations  
✅ **Secrets Management**: Ansible Vault implementation and best practices
✅ **Template System**: Jinja2 templates for configuration generation
✅ **Environment Strategy**: Multi-environment configuration management
✅ **Validation Framework**: Configuration testing and validation procedures

### Next Steps

1. **Implement Gradual Adoption**: Start with simple variable management and gradually adopt advanced features
2. **Establish Standards**: Create organization-specific naming conventions and documentation standards
3. **Automate Validation**: Implement automated testing pipelines for configuration changes
4. **Monitor and Iterate**: Continuously improve configuration management practices based on operational experience

Continue with the [Troubleshooting Guide](troubleshooting.md) to learn how to resolve common configuration issues, or explore the [Best Practices Guide](best-practices.md) for advanced operational techniques.

---

**🔧 Configuration Management Mastery Achieved!** You now have the tools and knowledge to effectively manage complex configurations across multiple environments and device types.