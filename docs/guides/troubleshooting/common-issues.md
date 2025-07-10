# Troubleshooting Guide

## Common Issues and Solutions

This comprehensive troubleshooting guide covers the most common issues encountered when using the Ansible Cloud & Network Automation Platform. Each section provides symptoms, root causes, diagnostic steps, and proven solutions based on real-world deployment experience.

## Diagnostic Tools and Commands

### Quick Diagnostic Commands

```bash
# System health check
./scripts/health_check.sh

# Ansible connectivity test
ansible all -i inventory/production.yml -m ping --one-line

# Verbose connection testing
ansible all -i inventory/production.yml -m ping -vvv

# Enterprise system validation
cd src/cisco_network_automation/
ansible-playbook playbooks/validation_suite.yml -i inventory/production.yml

# Security audit
ansible-playbook playbooks/security_audit.yml -i inventory/production.yml

# Check inventory syntax
ansible-inventory -i inventory/production.yml --list

# Validate playbook syntax
ansible-playbook playbooks/deploy.yml --syntax-check

# Dry run deployment
ansible-playbook playbooks/deploy.yml --check
```

### Enterprise System Diagnostics

```bash
# Enterprise system health check
cd src/cisco_network_automation/
./validate_production_readiness.sh

# Check enterprise deployment status
grep -r "Phase.*Complete\|FAILED" logs/*/

# Validate enterprise inventory
ansible-inventory -i inventory/production.yml --graph

# Test enterprise vault access
ansible-vault view group_vars/vault.yml --vault-password-file vault-password-script.sh
```

## Network Device Connectivity Issues

### Issue 1: SSH Connection Refused

#### Symptoms
```
TASK [Gathering Facts] *********************************************************
fatal: [switch-01]: UNREACHABLE! => {
    "changed": false,
    "msg": "Failed to connect to the host via ssh: ssh: connect to host 192.168.1.10 port 22: Connection refused",
    "unreachable": true
}
```

#### Diagnostic Steps
```bash
# Test basic network connectivity
ping 192.168.1.10

# Test SSH connectivity manually
ssh admin@192.168.1.10

# Check if SSH service is running on device
telnet 192.168.1.10 22

# Test with specific SSH options
ssh -o ConnectTimeout=10 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@192.168.1.10

# Check from device console (if accessible)
# show ip ssh
# show running-config | include ssh
```

#### Common Solutions

**Solution 1: Enable SSH on Device**
```bash
# Connect via console and configure SSH
configure terminal
ip domain-name company.local
crypto key generate rsa general-keys modulus 2048
ip ssh version 2
ip ssh time-out 300
line vty 0 15
 transport input ssh
 login local
username admin privilege 15 secret YourPassword
end
copy running-config startup-config
```

**Solution 2: Fix Ansible SSH Configuration**
```yaml
# In inventory or group_vars/all.yml
ansible_ssh_common_args: '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
ansible_command_timeout: 60
ansible_connect_timeout: 30
```

**Solution 3: Network Connectivity Issues**
```bash
# Check routing to device
traceroute 192.168.1.10

# Verify VPN connectivity (if using VPN)
# Check firewall rules
# Verify VLAN configuration
```

### Issue 2: Authentication Failures

#### Symptoms
```
fatal: [router-01]: FAILED! => {
    "msg": "Authentication failed: Invalid username or password"
}
```

#### Diagnostic Steps
```bash
# Test credentials manually
ssh admin@192.168.1.1

# Check vault encryption
ansible-vault view group_vars/vault.yml

# Verify variable substitution
ansible-inventory -i inventory/production.yml --host router-01 --vars | grep ansible_
```

#### Solutions

**Solution 1: Fix Credentials in Vault**
```bash
# Edit vault file
ansible-vault edit group_vars/vault.yml

# Add or update credentials
vault_router_01_username: "correct_username"
vault_router_01_password: "correct_password"
vault_router_01_enable: "correct_enable_password"
```

**Solution 2: Update Inventory Variables**
```yaml
# In inventory/production.yml or host_vars/router-01.yml
router-01:
  ansible_host: "192.168.1.1"
  ansible_user: "{{ vault_router_01_username }}"
  ansible_password: "{{ vault_router_01_password }}"
  ansible_become_password: "{{ vault_router_01_enable }}"
  ansible_network_os: ios
  ansible_connection: network_cli
  ansible_become: true
  ansible_become_method: enable
```

**Solution 3: AAA Configuration Issues**
```bash
# Check device AAA configuration via console
show running-config | section aaa
show users

# Common AAA fix
configure terminal
aaa new-model
aaa authentication login default local
aaa authorization exec default local
username admin privilege 15 secret YourPassword
end
```

### Issue 3: Enable Mode Access Denied

#### Symptoms
```
fatal: [switch-01]: FAILED! => {
    "msg": "unable to elevate privilege to enable mode, at prompt [Password: ]"
}
```

#### Diagnostic Steps
```bash
# Test enable password manually
ssh admin@192.168.1.10
enable
# Enter enable password

# Check enable secret configuration on device
show running-config | include enable
```

#### Solutions

**Solution 1: Correct Enable Password**
```bash
# Update vault with correct enable password
ansible-vault edit group_vars/vault.yml

# Ensure enable password is correct
vault_switch_01_enable: "correct_enable_password"
```

**Solution 2: Configure Enable Secret on Device**
```bash
# Via console access
configure terminal
enable secret YourEnablePassword
end
copy running-config startup-config
```

**Solution 3: Use Same Password for Login and Enable**
```yaml
# If using same password for login and enable
ansible_password: "{{ vault_device_password }}"
ansible_become_password: "{{ vault_device_password }}"
```

### Issue 4: Timeout Errors

#### Symptoms
```
fatal: [core-rtr-01]: FAILED! => {
    "msg": "command timeout triggered, timeout value is 30 secs"
}
```

#### Solutions

**Solution 1: Increase Timeout Values**
```yaml
# In group_vars/all.yml or ansible.cfg
ansible_command_timeout: 120
ansible_connect_timeout: 60

# For specific slow commands
- name: Execute slow command
  ios_command:
    commands: "show tech-support"
    timeout: 300
```

**Solution 2: Optimize Device Performance**
```bash
# Check device CPU and memory
show processes cpu sorted
show memory summary

# Disable unnecessary services
configure terminal
no ip http server
no ip http secure-server
end
```

## AWS Infrastructure Issues

### Issue 5: AWS Credentials Not Found

#### Symptoms
```
fatal: [localhost]: FAILED! => {
    "msg": "Unable to locate credentials. You can configure credentials by running \"aws configure\"."
}
```

#### Diagnostic Steps
```bash
# Check AWS CLI configuration
aws configure list

# Test AWS connectivity
aws sts get-caller-identity

# Check environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION
```

#### Solutions

**Solution 1: Configure AWS CLI**
```bash
# Interactive configuration
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Solution 2: Use IAM Roles (Recommended)**
```bash
# If running on EC2, attach IAM role
# If using local development, use AWS SSO
aws sso login --profile your-profile
export AWS_PROFILE=your-profile
```

**Solution 3: Credential File Configuration**
```bash
# ~/.aws/credentials
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key

# ~/.aws/config
[default]
region = us-east-1
output = json
```

### Issue 6: EC2 Instance Launch Failures

#### Symptoms
```
fatal: [localhost]: FAILED! => {
    "msg": "InvalidAMIID.NotFound: The image id '[ami-12345678]' does not exist"
}
```

#### Diagnostic Steps
```bash
# Check AMI availability in region
aws ec2 describe-images --image-ids ami-12345678 --region us-east-1

# List available AMIs
aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*" --query 'Images[*].[ImageId,Name,CreationDate]' --output table

# Check instance type availability
aws ec2 describe-instance-type-offerings --location-type availability-zone --filters Name=location,Values=us-east-1a
```

#### Solutions

**Solution 1: Update AMI ID**
```yaml
# In vars/development.yml or vars/production.yml
ami_id: "ami-0c02fb55956c7d316"  # Update to current Amazon Linux 2 AMI
```

**Solution 2: Dynamic AMI Selection**
```yaml
- name: Get latest Amazon Linux 2 AMI
  amazon.aws.ec2_ami_info:
    owners: amazon
    filters:
      name: "amzn2-ami-hvm-*"
      architecture: x86_64
      virtualization-type: hvm
      state: available
  register: amis

- name: Set AMI ID to latest
  set_fact:
    ami_id: "{{ (amis.images | sort(attribute='creation_date') | last).image_id }}"
```

### Issue 7: Security Group Configuration Errors

#### Symptoms
```
fatal: [localhost]: FAILED! => {
    "msg": "InvalidGroup.NotFound: The security group 'sg-12345678' does not exist"
}
```

#### Solutions

**Solution 1: Create Security Group**
```yaml
- name: Create security group
  amazon.aws.ec2_security_group:
    name: "{{ security_group_name }}"
    description: "{{ security_group_description }}"
    region: "{{ aws_region }}"
    rules: "{{ security_group_rules }}"
    state: present
  register: security_group
```

**Solution 2: Use Default Security Group**
```yaml
# Use default security group temporarily
security_groups: ["default"]
```

## Ansible Vault Issues

### Issue 8: Vault Decryption Failed

#### Symptoms
```
ERROR! Decryption failed (no vault secrets would found that could decrypt)
```

#### Diagnostic Steps
```bash
# Check vault password file exists
ls -la vault-password-script.sh

# Test vault password manually
ansible-vault view group_vars/vault.yml --ask-vault-pass

# Check file permissions
ls -la vault-password-script.sh
```

#### Solutions

**Solution 1: Fix Vault Password File**
```bash
# Recreate vault password file
echo "your-vault-password" > vault-password-script.sh
chmod 700 vault-password-script.sh

# Test vault access
ansible-vault view group_vars/vault.yml --vault-password-file vault-password-script.sh
```

**Solution 2: Re-encrypt Vault File**
```bash
# If password is lost, re-encrypt with new password
ansible-vault decrypt group_vars/vault.yml --ask-vault-pass
ansible-vault encrypt group_vars/vault.yml --ask-vault-pass
```

**Solution 3: Multiple Vault IDs**
```bash
# If using multiple vault IDs
ansible-playbook -i inventory/production.yml \
  --vault-id prod@vault-password-script.sh \
  playbooks/deploy.yml
```

### Issue 9: Vault File Corruption

#### Symptoms
```
ERROR! Attempting to decrypt but no vault secrets found
```

#### Solutions

**Solution 1: Restore from Backup**
```bash
# Restore vault file from backup
cp backups/vault.yml.backup group_vars/vault.yml
```

**Solution 2: Recreate Vault File**
```bash
# Create new vault file
ansible-vault create group_vars/vault_new.yml
# Add all required variables
# Replace old vault file
mv group_vars/vault_new.yml group_vars/vault.yml
```

## Playbook Execution Issues

### Issue 10: Undefined Variable Errors

#### Symptoms
```
fatal: [router-01]: FAILED! => {
    "msg": "'bgp_asn' is undefined"
}
```

#### Diagnostic Steps
```bash
# Check variable definition
ansible-inventory -i inventory/production.yml --host router-01 --vars | grep bgp

# List all variables for host
ansible all -i inventory/production.yml -m debug -a "var=hostvars[inventory_hostname]"
```

#### Solutions

**Solution 1: Define Missing Variables**
```yaml
# In group_vars/core_routers.yml
bgp_asn: 65000
bgp_router_id: "{{ ansible_host }}"
```

**Solution 2: Use Default Values**
```jinja2
# In templates
bgp {{ bgp_asn | default(65000) }}
router-id {{ bgp_router_id | default(ansible_host) }}
```

**Solution 3: Conditional Configuration**
```yaml
- name: Configure BGP
  ios_config:
    lines:
      - "router bgp {{ bgp_asn }}"
      - "router-id {{ bgp_router_id }}"
  when: 
    - bgp_asn is defined
    - bgp_router_id is defined
```

### Issue 11: Template Rendering Errors

#### Symptoms
```
fatal: [switch-01]: FAILED! => {
    "msg": "TemplateSyntaxError: unexpected char '!' at 45"
}
```

#### Solutions

**Solution 1: Fix Template Syntax**
```jinja2
{# Correct Jinja2 syntax #}
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}

{# Avoid Cisco IOS comments in templates #}
{# Use Jinja2 comments instead of ! #}
```

**Solution 2: Escape Special Characters**
```jinja2
{# For literal exclamation marks #}
{{ '!' }} This is a literal exclamation mark
```

### Issue 12: Module Not Found Errors

#### Symptoms
```
fatal: [router-01]: FAILED! => {
    "msg": "couldn't resolve module/action 'cisco.ios.ios_command'"
}
```

#### Solutions

**Solution 1: Install Required Collections**
```bash
# Install missing collections
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible-galaxy collection list
```

**Solution 2: Update Collection Versions**
```yaml
# requirements.yml
collections:
  - name: cisco.ios
    version: ">=5.0.0"
  - name: ansible.netcommon
    version: ">=5.0.0"
```

## Enterprise System Issues

### Issue 13: Phase Deployment Failures

#### Symptoms
```
PLAY RECAP *********************************************************************
core-rtr-01               : ok=10   changed=5    unreachable=0    failed=1
```

#### Diagnostic Steps
```bash
# Check phase-specific logs
cd src/cisco_network_automation/
ls -la logs/*/phase_reports/

# Review failed phase details
grep -r "FAILED\|ERROR" logs/*/phase_reports/

# Check device-specific logs
cat logs/*/core-rtr-01_phase2_*.txt
```

#### Solutions

**Solution 1: Re-run Specific Phase**
```bash
# Re-run from failed phase
ansible-playbook -i inventory/production.yml \
  --vault-password-file vault-password-script.sh \
  -e environment=production \
  -e start_from_phase=2 \
  playbooks/master_enterprise_deployment.yml
```

**Solution 2: Skip Failed Devices**
```bash
# Continue deployment without failed devices
ansible-playbook -i inventory/production.yml \
  --vault-password-file vault-password-script.sh \
  -e environment=production \
  --limit 'all:!core-rtr-01' \
  playbooks/master_enterprise_deployment.yml
```

### Issue 14: Backup and Rollback Issues

#### Symptoms
```
fatal: [core-rtr-01]: FAILED! => {
    "msg": "Backup file not found: /backup/core-rtr-01_config.txt"
}
```

#### Solutions

**Solution 1: Create Manual Backup**
```bash
# Create immediate backup
ansible-playbook -i inventory/production.yml \
  --vault-password-file vault-password-script.sh \
  playbooks/backup_configurations.yml
```

**Solution 2: Verify Backup Directory**
```bash
# Check backup location
ls -la logs/*/backups/

# Create backup directory if missing
mkdir -p logs/$(date +%Y%m%d_%H%M%S)/backups
```

### Issue 15: Serial Deployment Limits

#### Symptoms
- Deployment taking too long
- High device resource utilization
- Network congestion

#### Solutions

**Solution 1: Adjust Serial Limits**
```yaml
# In group_vars/[environment].yml
serial_limit: 5  # Increase for faster deployment
serial_limit: 1  # Decrease for safety
```

**Solution 2: Implement Deployment Batching**
```yaml
- name: Deploy in batches
  include_tasks: deploy_batch.yml
  vars:
    batch_devices: "{{ groups['all'] | batch(5) | list }}"
  loop: "{{ batch_devices }}"
```

## Performance and Resource Issues

### Issue 16: High Memory Usage

#### Symptoms
- Ansible process consuming excessive memory
- System becomes unresponsive
- Out of memory errors

#### Solutions

**Solution 1: Reduce Fact Gathering**
```yaml
# Disable unnecessary fact gathering
gather_facts: false

# Or use smart gathering
gathering = smart
fact_caching = memory
fact_caching_timeout = 3600
```

**Solution 2: Optimize Inventory Size**
```bash
# Split large inventories
# Use dynamic inventories
# Limit deployment scope
ansible-playbook --limit "core_routers" playbooks/deploy.yml
```

**Solution 3: Increase System Resources**
```bash
# Monitor memory usage
free -h
htop

# Increase swap space if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue 17: Slow Deployment Performance

#### Solutions

**Solution 1: Optimize Ansible Configuration**
```ini
# ansible.cfg
[defaults]
forks = 20
host_key_checking = False
gathering = smart
fact_caching = memory

[ssh_connection]
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
pipelining = True
```

**Solution 2: Use Strategy Plugins**
```yaml
- hosts: all
  strategy: free  # Don't wait for all hosts
  tasks:
    - name: Configure device
      ios_config:
        src: config.j2
```

## Network Protocol Issues

### Issue 18: BGP Neighbor Issues

#### Symptoms
- BGP neighbors not establishing
- Routing table incomplete
- Network connectivity issues

#### Diagnostic Commands
```bash
# Check BGP status
ansible routers -i inventory/production.yml \
  -m ios_command -a "commands='show ip bgp summary'"

# Check BGP neighbors
ansible routers -i inventory/production.yml \
  -m ios_command -a "commands='show ip bgp neighbors'"

# Check routing table
ansible routers -i inventory/production.yml \
  -m ios_command -a "commands='show ip route bgp'"
```

#### Solutions

**Solution 1: Verify BGP Configuration**
```yaml
# Check BGP variables
bgp_asn: 65000
bgp_router_id: "10.0.1.1"
bgp_neighbors:
  - peer_ip: "10.0.1.2"
    remote_as: 65000
    description: "iBGP peer"
```

**Solution 2: Check Network Connectivity**
```bash
# Test connectivity between BGP peers
ansible core_routers -i inventory/production.yml \
  -m ios_command -a "commands='ping 10.0.1.2 source 10.0.1.1'"
```

### Issue 19: VLAN Configuration Issues

#### Symptoms
- VLANs not created
- VLAN membership incorrect
- Inter-VLAN routing problems

#### Solutions

**Solution 1: Verify VLAN Configuration**
```yaml
vlans:
  - id: 10
    name: "DATA"
  - id: 20
    name: "VOICE"
  - id: 30
    name: "GUEST"
```

**Solution 2: Check Interface Configuration**
```bash
# Verify VLAN assignment
ansible switches -i inventory/production.yml \
  -m ios_command -a "commands='show vlan brief'"

# Check interface status
ansible switches -i inventory/production.yml \
  -m ios_command -a "commands='show interfaces status'"
```

## Security and Compliance Issues

### Issue 20: Security Policy Violations

#### Symptoms
- Access denied errors
- Security alerts
- Compliance failures

#### Solutions

**Solution 1: Review Security Configuration**
```bash
# Check access lists
ansible all -i inventory/production.yml \
  -m ios_command -a "commands='show access-lists'"

# Verify security settings
ansible all -i inventory/production.yml \
  -m ios_command -a "commands='show running-config | include security'"
```

**Solution 2: Update Security Policies**
```yaml
# Enhanced security configuration
security_settings:
  enable_port_security: true
  max_mac_addresses: 1
  violation_action: "shutdown"
  enable_dhcp_snooping: true
  enable_ip_source_guard: true
```

## Monitoring and Logging Issues

### Issue 21: Missing Logs

#### Symptoms
- No deployment logs generated
- Incomplete logging information
- Cannot troubleshoot issues

#### Solutions

**Solution 1: Enable Comprehensive Logging**
```yaml
# In ansible.cfg
[defaults]
log_path = ./logs/ansible.log
stdout_callback = yaml
```

**Solution 2: Configure Syslog**
```yaml
# Enable syslog on devices
syslog_configuration:
  enable: true
  servers:
    - "10.0.100.10"
    - "10.0.100.11"
  facility: "local0"
  severity: "informational"
```

## Emergency Procedures

### Emergency Rollback

```bash
# Immediate rollback (Enterprise system)
cd src/cisco_network_automation/
./deploy_enterprise.sh --rollback --environment production

# Manual rollback
ansible-playbook -i inventory/production.yml \
  --vault-password-file vault-password-script.sh \
  -e rollback_reason="Emergency rollback due to connectivity issues" \
  playbooks/rollback_deployment.yml
```

### Emergency Configuration Recovery

```bash
# Restore from backup
ansible-playbook -i inventory/production.yml \
  --vault-password-file vault-password-script.sh \
  -e restore_from_backup=true \
  -e backup_date="20231210_142305" \
  playbooks/restore_configuration.yml
```

### Network Isolation Procedure

```bash
# Isolate problematic device
ansible-playbook -i inventory/production.yml \
  --vault-password-file vault-password-script.sh \
  -e target_device="problematic-device" \
  -e isolation_action="shutdown_interfaces" \
  playbooks/emergency_isolation.yml
```

## Prevention Strategies

### Pre-Deployment Validation

```bash
# Comprehensive pre-deployment checks
./scripts/pre_deployment_validation.sh

# Syntax validation
ansible-playbook playbooks/deploy.yml --syntax-check

# Dry run testing
ansible-playbook playbooks/deploy.yml --check --diff
```

### Monitoring and Alerting

```yaml
# Implement monitoring playbook
- name: Monitor deployment health
  include_tasks: monitoring_tasks.yml
  tags: monitoring

# Set up automated alerts
- name: Configure alerting
  include_tasks: alerting_setup.yml
  tags: alerting
```

### Documentation and Training

1. **Maintain Updated Documentation**
   - Keep troubleshooting guides current
   - Document new issues and solutions
   - Create environment-specific guides

2. **Regular Training**
   - Train team on common issues
   - Practice emergency procedures
   - Update troubleshooting workflows

3. **Automated Testing**
   - Implement CI/CD pipelines
   - Regular validation testing
   - Performance monitoring

## Getting Additional Help

### Internal Resources

1. **Log Analysis**
   ```bash
   # Check comprehensive logs
   cd src/cisco_network_automation/logs/
   find . -name "*.txt" -exec grep -l "ERROR\|FAILED" {} \;
   ```

2. **Community Resources**
   - Ansible documentation: https://docs.ansible.com/
   - Cisco Ansible collection: https://galaxy.ansible.com/cisco
   - Network automation community forums

3. **Professional Support**
   - Engage vendor support for device-specific issues
   - Consider professional services for complex deployments
   - Network automation consulting services

### Escalation Procedures

1. **Level 1**: Use this troubleshooting guide
2. **Level 2**: Engage senior network engineers
3. **Level 3**: Vendor support and professional services
4. **Emergency**: Implement rollback procedures immediately

---

**🔧 Troubleshooting Mastery Complete!** You now have comprehensive knowledge to diagnose and resolve common issues with the Ansible Cloud & Network Automation Platform. Remember: when in doubt, test in development first, maintain good backups, and always have a rollback plan ready.

Continue with the [Best Practices Guide](best-practices.md) to learn how to prevent many of these issues through proper operational procedures.