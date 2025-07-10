# Getting Started Guide

## Welcome to the Ansible Cloud & Network Automation Platform

This guide will help you get started with the platform, from initial setup to your first successful deployment. Whether you're new to Ansible or experienced with automation, this step-by-step guide will ensure you're up and running quickly.

## Prerequisites

### System Requirements

#### Required Software
```bash
# Python 3.8 or higher
python3 --version  # Should be 3.8+

# Ansible 2.12 or higher
ansible --version  # Should be 2.12+

# Git for version control
git --version

# SSH client for device connectivity
ssh -V
```

#### Installation Commands
```bash
# Install Python and pip (if not already installed)
# On macOS
brew install python3

# On Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# On CentOS/RHEL
sudo yum install python3 python3-pip

# Install Ansible
pip3 install ansible

# Verify installation
ansible --version
```

### Platform-Specific Requirements

#### AWS Prerequisites
```bash
# Install AWS CLI
pip3 install awscli

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Default region, Output format

# Verify AWS connectivity
aws sts get-caller-identity
```

#### Network Device Prerequisites
- SSH access to all target network devices
- Administrative credentials for device configuration
- Network connectivity between Ansible control node and devices
- Proper firewall rules allowing SSH traffic

## Initial Setup

### Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd ansible-cloud-playbook

# Verify project structure
ls -la

# Check git status
git status
```

### Step 2: Install Required Collections

```bash
# Install Ansible collections
ansible-galaxy collection install -r requirements.yml

# Verify collections are installed
ansible-galaxy collection list
```

Expected output should include:
- `amazon.aws`
- `cisco.ios`
- `ansible.netcommon`

### Step 3: Configure Ansible Settings

Create or verify your Ansible configuration:

```bash
# Create ansible.cfg (if not exists)
cat > ansible.cfg << 'EOF'
[defaults]
host_key_checking = False
inventory = inventory/hosts.yml
timeout = 30
stdout_callback = yaml
gathering = smart
fact_caching = memory

[ssh_connection]
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
EOF
```

### Step 4: Set Up Vault Password

```bash
# Create vault password file
echo "your-secure-password" > vault-password-script.sh
chmod +x vault-password-script.sh

# Test vault functionality
ansible-vault --help
```

⚠️ **Security Note**: Never commit vault password files to version control!

## Understanding the Platform Structure

### Project Layout
```
ansible-cloud-playbook/
├── README.md                    # Project overview
├── requirements.yml             # Ansible collections
├── docs/                        # Documentation (this guide)
├── src/
│   └── cisco_network_automation/ # Enterprise system
└── vault-password-script.sh     # Vault password script
```

### Enterprise Automation System

The platform provides enterprise-grade network automation through the `src/cisco_network_automation/` system:

- **Location**: `src/cisco_network_automation/`
- **Purpose**: Production-ready network automation
- **Features**: 19 infrastructure roles, 6-phase deployment, AI optimization
- **Entry Point**: `./deploy_enterprise.sh`

## Your First Deployment

### Enterprise Development Deployment

#### Step 1: Navigate to Enterprise System
```bash
cd src/cisco_network_automation/
```

#### Step 2: Configure Environment Variables
```bash
# Review development environment variables
vim group_vars/all.yml

# Key settings to review:
# - DNS servers
# - NTP servers
# - SNMP configuration
# - Security policies
```

#### Step 3: Deploy Enterprise Infrastructure
```bash
# Create development environment
./deploy_enterprise.sh --environment development --verbose

# Verify deployment
ansible-playbook validation_suite.yml
```

### Production Deployment

#### Step 1: Navigate to Enterprise System
```bash
cd src/cisco_network_automation/
```

#### Step 2: Validate Prerequisites
```bash
# Check enterprise system requirements
./deploy_enterprise.sh --help

# Validate inventory
ansible-inventory -i inventory/production.yml --list
```

#### Step 3: Run Production Deployment
```bash
# Start with development environment
./deploy_enterprise.sh --environment development --dry-run

# If dry-run succeeds, run actual deployment
./deploy_enterprise.sh --environment development --verbose
```

## Verification and Testing

### Verify Enterprise Deployment
```bash
# Check enterprise deployment status
cd src/cisco_network_automation/
ansible-playbook validation_suite.yml

# Test device connectivity
ansible all -m ping
```

### Verify Enterprise Deployment
```bash
# Check deployment logs
ls -la logs/

# Review deployment summary
cat logs/*/MASTER_DEPLOYMENT_SUMMARY.txt

# Verify all phases completed
grep -r "Phase.*Complete" logs/
```

## Common Initial Issues and Solutions

### Issue 1: Ansible Collection Not Found
```bash
# Error: couldn't resolve module/action 'cisco.ios.ios_command'
# Solution: Install collections
ansible-galaxy collection install cisco.ios ansible.netcommon
```

### Issue 2: SSH Connection Refused
```bash
# Error: Failed to connect to the host via ssh
# Solution: Verify SSH connectivity
ssh -o ConnectTimeout=10 username@device-ip

# Check SSH keys and credentials
ssh-keygen -t rsa -b 2048
ssh-copy-id username@device-ip
```

### Issue 3: Vault Password Issues
```bash
# Error: Decryption failed
# Solution: Check vault password file
chmod +x vault-password-script.sh
echo "correct-password" > vault-password-script.sh
```

### Issue 4: Enterprise Role Dependencies
```bash
# Error: Role dependency not found
# Solution: Ensure all roles are present
cd src/cisco_network_automation/
ls -la roles/
# Verify all 19 roles are available
```

## Next Steps

### For Enterprise System Users
1. **Deep Dive**: Study the [Enterprise Deployment Guide](enterprise-deployment.md)
2. **Configure**: Set up your production inventory and variables
3. **Deploy**: Follow the phased deployment process

### For Network Engineers
1. **Study**: Read the [Enterprise Deployment Guide](enterprise-deployment.md)
2. **Practice**: Deploy in development environment first
3. **Scale**: Progress to staging and production deployments

## Learning Path Recommendations

### Week 1: Foundation
- Complete this getting started guide
- Set up the enterprise system environment
- Deploy your first development environment

### Week 2: Exploration
- Try the enterprise system in development mode
- Experiment with different network protocols
- Learn about Ansible Vault and variable management

### Week 3: Customization
- Modify playbooks for your specific environment
- Create custom inventory configurations
- Implement security best practices

### Week 4: Production Readiness
- Study the enterprise deployment phases
- Set up production inventory and variables
- Plan your first production deployment

## Support and Resources

### Documentation
- **Platform Overview**: [README.md](../README.md)
- **API Reference**: [API_REFERENCE.md](../API_REFERENCE.md)
- **Security Guide**: [SECURITY.md](../SECURITY.md)

### Troubleshooting
- **Common Issues**: [Troubleshooting Guide](troubleshooting.md)
- **Best Practices**: [Best Practices Guide](best-practices.md)
- **Configuration Help**: [Configuration Management Guide](configuration-management.md)

### Community Resources
- **Ansible Documentation**: https://docs.ansible.com/
- **Cisco Ansible Collections**: https://galaxy.ansible.com/cisco
- **AWS Ansible Collection**: https://galaxy.ansible.com/amazon/aws

---

**Congratulations!** You've completed the getting started guide. You should now have a working Ansible environment and understand the platform's structure. Choose your next step based on your needs:

- **Enterprise Focus**: Move to the [Enterprise Deployment Guide](enterprise-deployment.md)
- **Network Specialization**: Study the [Configuration Management Guide](configuration-management.md)

*Remember: Start small, learn incrementally, and always test in development before deploying to production.*