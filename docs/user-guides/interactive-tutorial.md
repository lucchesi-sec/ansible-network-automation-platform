# Interactive Automation Tutorial

## Complete Walkthrough of Root-Level Automation

This tutorial provides a comprehensive, hands-on walkthrough of the interactive automation features available at the root level of the platform. You'll learn to use the wizard-driven tools for network configuration and AWS infrastructure deployment.

## Tutorial Overview

### What You'll Learn
- How to use the interactive network configuration wizard
- AWS infrastructure deployment with environment-specific configurations
- Automatic inventory generation and management
- Testing and validation procedures
- Common troubleshooting techniques

### What You'll Build
- A complete network topology with switches and routers
- AWS EC2 infrastructure with security groups
- Ansible inventory for device management
- Validation and testing playbooks

### Prerequisites
- Completed [Getting Started Guide](getting-started.md)
- Basic understanding of networking concepts
- AWS account with appropriate permissions
- SSH access to network devices (for network tutorial)

## Part 1: Interactive Network Configuration

### Step 1: Launch the Network Wizard

The interactive network wizard guides you through creating a complete network configuration.

```bash
# Navigate to project root
cd /path/to/ansible-cloud-playbook

# Launch the interactive wizard
./network-deploy.sh
```

### Step 2: Configure Network Topology

The wizard will prompt you for various configuration options:

#### Device Configuration
```
How many switches do you want to configure? 3
How many routers do you want to configure? 2
```

**💡 Tip**: Start with 2 switches and 1 router for your first deployment

#### VLAN Configuration
```
Enter the starting VLAN ID (e.g., 10): 10
How many VLANs to create? 5
```

This creates VLANs 10-14 for network segmentation.

#### Spanning Tree Protocol
```
Select Spanning Tree Protocol:
1. PVST+ (Per-VLAN Spanning Tree Plus)
2. Rapid PVST+ (Rapid Per-VLAN Spanning Tree Plus)
3. MST (Multiple Spanning Tree)
Enter your choice (1-3): 2
```

**💡 Best Practice**: Choose Rapid PVST+ for faster convergence

#### Routing Protocol Configuration
```
Select routing protocol:
1. OSPF (Open Shortest Path First)
2. EIGRP (Enhanced Interior Gateway Routing Protocol)
3. Static routing
Enter your choice (1-3): 1

Enter OSPF area ID (e.g., 0): 0
Enter OSPF process ID (e.g., 1): 1
```

#### Management Configuration
```
Enable SSH? (y/n): y
Enter SSH version (1 or 2): 2
Enter SSH timeout (60-300 seconds): 300

Enable SNMP? (y/n): y
Enter SNMP community string: public
```

**🔐 Security Note**: Use strong community strings in production

### Step 3: Device Credentials

The wizard will prompt for device-specific credentials:

```
Enter credentials for Switch 1:
IP Address: 192.168.1.10
Username: admin
Password: [hidden input]
Enable Password: [hidden input]
```

**💡 Pro Tip**: Prepare your device inventory beforehand:
```
Device Type | IP Address    | Username | Password
Switch 1    | 192.168.1.10 | admin    | switch1pass
Switch 2    | 192.168.1.11 | admin    | switch2pass
Router 1    | 192.168.1.1  | admin    | router1pass
```

### Step 4: Review Generated Configuration

After completing the wizard, review the generated files:

```bash
# Check the generated inventory
cat configs/inventory.yml

# Review the main deployment playbook
cat configs/playbooks/deploy_network.yml

# Examine switch configuration templates
ls -la configs/templates/
```

**Example Generated Inventory**:
```yaml
---
all:
  children:
    switches:
      hosts:
        switch1:
          ansible_host: 192.168.1.10
          ansible_user: admin
          ansible_password: "{{ vault_switch1_password }}"
          ansible_become_password: "{{ vault_switch1_enable }}"
          ansible_network_os: ios
          ansible_connection: network_cli
        switch2:
          ansible_host: 192.168.1.11
          ansible_user: admin
          ansible_password: "{{ vault_switch2_password }}"
          ansible_become_password: "{{ vault_switch2_enable }}"
          ansible_network_os: ios
          ansible_connection: network_cli
    routers:
      hosts:
        router1:
          ansible_host: 192.168.1.1
          ansible_user: admin
          ansible_password: "{{ vault_router1_password }}"
          ansible_become_password: "{{ vault_router1_enable }}"
          ansible_network_os: ios
          ansible_connection: network_cli
```

### Step 5: Deploy Network Configuration

```bash
# Test connectivity before deployment
ansible all -i configs/inventory.yml -m ping

# Deploy the network configuration
ansible-playbook -i configs/inventory.yml configs/playbooks/deploy_network.yml

# Monitor deployment progress
tail -f /tmp/ansible.log
```

**Expected Output**:
```
PLAY [Deploy Network Configuration] ****************************

TASK [Configure VLANs on switches] *****************************
ok: [switch1]
ok: [switch2]

TASK [Configure Spanning Tree Protocol] ************************
ok: [switch1]
ok: [switch2]

TASK [Configure OSPF on routers] *******************************
ok: [router1]

PLAY RECAP ******************************************************
switch1                    : ok=15   changed=12   unreachable=0
switch2                    : ok=15   changed=12   unreachable=0
router1                    : ok=10   changed=8    unreachable=0
```

### Step 6: Validate Network Deployment

```bash
# Test network connectivity
ansible-playbook -i configs/inventory.yml configs/playbooks/test_connectivity.yml

# Verify VLAN configuration
ansible switches -i configs/inventory.yml -m ios_command -a "commands='show vlan brief'"

# Check OSPF neighbors
ansible routers -i configs/inventory.yml -m ios_command -a "commands='show ip ospf neighbor'"

# Verify spanning tree status
ansible switches -i configs/inventory.yml -m ios_command -a "commands='show spanning-tree summary'"
```

## Part 2: AWS Infrastructure Deployment

### Step 1: Understanding Environment Variables

The platform uses environment-specific variable files:

```bash
# List available environment files
cd src/cisco_network_automation/
ls -la group_vars/

# Expected files:
# - all.yml
# - core_routers.yml
# - distribution_routers.yml
```

### Step 2: Configure Development Environment

```bash
# Edit development environment variables
vim group_vars/all.yml
```

**Key Configuration Parameters**:
```yaml
---
# Network Configuration
dns_servers:
  - "8.8.8.8"
  - "8.8.4.4"

ntp_servers:
  - "pool.ntp.org"
  - "time.google.com"

# Management Configuration
logging_server: "192.168.1.100"
snmp_community: "{{ vault_snmp_community }}"

# Security Configuration
zero_trust_policy_enforcement: "enabled"
ai_automation_enabled: true

# Environment
deployment_environment: "development"
deployment_phase: "initial"
```

### Step 3: Deploy AWS Infrastructure

```bash
# Create development environment
ansible-playbook playbooks/create-instance.yml -e @vars/development.yml -v

# Monitor AWS resources
watch -n 10 "aws ec2 describe-instances --region us-east-1 --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,Tags[?Key==\`Name\`].Value|[0]]' --output table"
```

**Expected AWS Resources Created**:
- EC2 Instance with specified configuration
- Security Group with defined rules
- Instance tagged with environment and project labels

### Step 4: Validate AWS Deployment

```bash
# Get instance details
aws ec2 describe-instances --region us-east-1 --filters "Name=tag:Environment,Values=development"

# Test SSH connectivity
ssh -i ~/.ssh/your-key.pem ec2-user@<instance-public-ip>

# Run connectivity tests
ansible-playbook playbooks/test-instance.yml -e @vars/development.yml
```

### Step 5: Update Instance Configuration

```bash
# Update instance with additional software
ansible-playbook playbooks/update-instance.yml -e @vars/development.yml

# Verify updates
ansible-playbook playbooks/test-instance.yml -e @vars/development.yml
```

## Part 3: Advanced Interactive Features

### Custom Network Topologies

#### Hub and Spoke Configuration
```bash
# Create hub and spoke topology
./network-deploy.sh --topology hub-and-spoke

# Configuration options:
# - Hub router: 192.168.1.1
# - Spoke routers: 192.168.1.2, 192.168.1.3, 192.168.1.4
# - Hub-to-spoke routing with EIGRP
```

#### Leaf-Spine Architecture
```bash
# Create leaf-spine topology
./network-deploy.sh --topology leaf-spine

# Configuration options:
# - Spine switches: 2
# - Leaf switches: 4
# - BGP fabric with ECMP
```

### Multi-Environment AWS Deployments

#### Production Environment
```bash
# Configure production environment
cp vars/development.yml vars/production.yml
vim vars/production.yml

# Key changes for production:
# - Larger instance types
# - Enhanced security groups
# - Backup and monitoring configuration
```

```yaml
---
# Production-specific configurations
instance_type: "t3.large"
environment: "production"
enable_monitoring: true
backup_retention_days: 30

# Enhanced security
security_group_rules:
  - proto: tcp
    ports:
      - 22
    cidr_ip: "10.0.0.0/8"  # Restrict SSH to internal networks
    rule_desc: "SSH access from internal"
```

```bash
# Deploy production environment
ansible-playbook playbooks/create-instance.yml -e @vars/production.yml
```

### Automated Inventory Generation

The platform automatically generates Ansible inventory files:

```bash
# Generate AWS inventory
ansible-playbook playbooks/generate-aws-inventory.yml -e @vars/development.yml

# Generated inventory location
cat inventory/aws_ec2.yml

# Dynamic inventory usage
ansible -i inventory/aws_ec2.yml all -m ping
```

## Part 4: Testing and Validation

### Network Testing Scenarios

#### Connectivity Tests
```bash
# Basic connectivity
ansible-playbook configs/playbooks/test_connectivity.yml

# VLAN connectivity
ansible-playbook configs/playbooks/test_vlan_connectivity.yml

# Routing protocol convergence
ansible-playbook configs/playbooks/test_routing_convergence.yml
```

#### Performance Testing
```bash
# Network performance tests
ansible-playbook configs/playbooks/performance_tests.yml

# Generate performance report
ansible-playbook configs/playbooks/generate_performance_report.yml
```

### AWS Testing Scenarios

#### Security Group Testing
```bash
# Test security group rules
ansible-playbook playbooks/test-security-groups.yml -e @vars/development.yml

# Network ACL testing
ansible-playbook playbooks/test-network-acls.yml -e @vars/development.yml
```

#### Application Deployment Testing
```bash
# Deploy test application
ansible-playbook playbooks/deploy-test-app.yml -e @vars/development.yml

# Test application functionality
ansible-playbook playbooks/test-app-functionality.yml -e @vars/development.yml
```

## Part 5: Troubleshooting Common Issues

### Network Configuration Issues

#### Issue: Device Not Reachable
```bash
# Debug steps
ansible switches -i configs/inventory.yml -m ping -vvv

# Check SSH connectivity
ssh -o ConnectTimeout=10 admin@192.168.1.10

# Verify credentials
ansible-vault view configs/group_vars/all.yml
```

#### Issue: Configuration Not Applied
```bash
# Check for syntax errors
ansible-playbook configs/playbooks/deploy_network.yml --syntax-check

# Verify device compatibility
ansible switches -i configs/inventory.yml -m ios_command -a "commands='show version'"

# Check configuration idempotency
ansible-playbook configs/playbooks/deploy_network.yml --check
```

### AWS Deployment Issues

#### Issue: Instance Launch Failure
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify region and availability zone
aws ec2 describe-availability-zones --region us-east-1

# Check AMI availability
aws ec2 describe-images --image-ids ami-0c55b159cbfafe1d0 --region us-east-1
```

#### Issue: Security Group Issues
```bash
# List security groups
aws ec2 describe-security-groups --region us-east-1

# Check security group rules
aws ec2 describe-security-groups --group-names ansible-sg-dev --region us-east-1
```

## Part 6: Customization and Extension

### Creating Custom Network Templates

```bash
# Create custom template directory
mkdir -p configs/templates/custom

# Create custom switch template
cat > configs/templates/custom/switch_template.j2 << 'EOF'
!
hostname {{ inventory_hostname }}
!
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
!
{% endfor %}
!
{% for interface in interfaces %}
interface {{ interface.name }}
 description {{ interface.description }}
 switchport mode {{ interface.mode }}
 switchport access vlan {{ interface.vlan }}
!
{% endfor %}
EOF
```

### Creating Custom AWS Playbooks

```bash
# Create custom playbook directory
mkdir -p playbooks/custom

# Create custom EC2 playbook
cat > playbooks/custom/custom-ec2-deployment.yml << 'EOF'
---
- name: Custom EC2 Deployment
  hosts: localhost
  gather_facts: false
  vars:
    custom_instance_type: "{{ instance_type | default('t3.micro') }}"
    custom_security_groups: "{{ security_groups | default(['default']) }}"
  
  tasks:
    - name: Launch EC2 instance with custom configuration
      amazon.aws.ec2_instance:
        name: "{{ instance_name }}"
        instance_type: "{{ custom_instance_type }}"
        image_id: "{{ ami_id }}"
        security_groups: "{{ custom_security_groups }}"
        region: "{{ aws_region }}"
        wait: true
        wait_timeout: 600
        tags:
          Environment: "{{ environment }}"
          Project: "{{ project }}"
          CustomTag: "{{ custom_tag | default('interactive-deployment') }}"
EOF
```

## Part 7: Best Practices and Tips

### Network Configuration Best Practices

1. **Start Simple**: Begin with basic configurations and gradually add complexity
2. **Use Version Control**: Commit generated configurations to track changes
3. **Test Incrementally**: Validate each configuration step before proceeding
4. **Document Changes**: Maintain clear documentation of network topology
5. **Backup Configurations**: Always backup device configurations before changes

### AWS Deployment Best Practices

1. **Use Environment-Specific Variables**: Separate development, staging, and production configurations
2. **Implement Proper Security**: Use least-privilege security group rules
3. **Monitor Resources**: Enable CloudWatch monitoring for all resources
4. **Cost Optimization**: Use appropriate instance types and implement auto-scaling
5. **Disaster Recovery**: Plan for backup and recovery procedures

### Automation Best Practices

1. **Idempotent Playbooks**: Ensure playbooks can be run multiple times safely
2. **Error Handling**: Implement proper error handling and rollback procedures
3. **Logging**: Maintain comprehensive logs for troubleshooting
4. **Testing**: Validate all automation before production deployment
5. **Documentation**: Keep playbooks and configurations well-documented

## Next Steps

### Intermediate Users
- Explore the [Enterprise Deployment Guide](enterprise-deployment.md)
- Learn advanced [Configuration Management](configuration-management.md)
- Study [Best Practices](best-practices.md)

### Advanced Users
- Customize roles and playbooks for specific requirements
- Implement CI/CD pipelines for automated deployments
- Integrate with monitoring and alerting systems

### Production Deployment
- Plan production network topology
- Implement security hardening
- Set up backup and recovery procedures
- Establish monitoring and maintenance schedules

## Conclusion

This interactive tutorial has walked you through the complete process of using the root-level automation features. You've learned to:

- Configure network devices using interactive wizards
- Deploy AWS infrastructure with environment-specific configurations
- Validate and test deployments
- Troubleshoot common issues
- Customize and extend the platform

The interactive automation system provides an excellent foundation for learning and development. As your requirements grow, consider transitioning to the enterprise deployment system for production-grade automation.

---

**🎉 Congratulations!** You've completed the interactive automation tutorial. You're now equipped to:
- Deploy and manage network configurations
- Automate AWS infrastructure deployments
- Customize the platform for your specific needs
- Troubleshoot and resolve common issues

Continue your journey with the [Enterprise Deployment Guide](enterprise-deployment.md) or explore specific areas of interest in the specialized guides.