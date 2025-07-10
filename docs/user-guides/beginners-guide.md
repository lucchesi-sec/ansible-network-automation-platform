# Beginner's Guide

## For Users New to Ansible or Network Automation

Welcome! This guide is specifically designed for users who are new to Ansible, network automation, or both. We'll start with the fundamentals and gradually build up to more complex topics, ensuring you have a solid foundation before moving to advanced features.

## What Is Network Automation?

### Traditional Network Management Challenges
- **Manual Configuration**: Logging into each device individually
- **Human Errors**: Typos, inconsistent configurations, forgotten steps
- **Time-Consuming**: Hours or days to configure multiple devices
- **Documentation Lag**: Configurations don't match documentation
- **Rollback Complexity**: Difficult to undo changes quickly

### Network Automation Benefits
- **Consistency**: Same configuration applied everywhere
- **Speed**: Deploy to hundreds of devices simultaneously
- **Accuracy**: Eliminate human errors
- **Repeatability**: Same process every time
- **Version Control**: Track all changes over time
- **Rollback**: Quick recovery from issues

## What Is Ansible?

### Core Concepts

#### Agentless Architecture
```
Your Computer (Control Node)
    |
    | SSH/API calls
    ↓
Network Devices (Managed Nodes)
```

**Key Point**: No software installation required on network devices!

#### Playbooks and Tasks
Think of playbooks as recipes and tasks as individual cooking steps:

```yaml
# A simple "recipe" (playbook)
- name: Configure basic switch settings
  tasks:
    - name: Set hostname
      # This is like "Step 1: Set the oven to 350°F"
    - name: Configure VLANs
      # This is like "Step 2: Mix ingredients"
    - name: Configure interfaces
      # This is like "Step 3: Bake for 30 minutes"
```

#### Inventory
Your "contact list" of devices:
```yaml
switches:
  switch-01: 192.168.1.10
  switch-02: 192.168.1.11
routers:
  router-01: 192.168.1.1
```

#### Variables
Settings you can change without modifying the main configuration:
```yaml
vlan_id: 100        # You can change this to 200 later
vlan_name: "DATA"   # You can change this to "USERS" later
```

## Understanding This Platform

### Two Systems in One

This platform provides two different approaches to automation:

#### 1. Interactive System (Your Starting Point)
- **Location**: Root directory
- **Purpose**: Learning and simple tasks
- **Style**: Wizard-driven, asks you questions
- **Best For**: 
  - Learning Ansible concepts
  - Configuring 1-5 devices
  - Prototyping configurations
  - Understanding how automation works

#### 2. Enterprise System (Your Future Goal)
- **Location**: `src/cisco_network_automation/`
- **Purpose**: Production-grade automation
- **Style**: Pre-configured, comprehensive
- **Best For**:
  - Managing hundreds of devices
  - Production environments
  - Complex, multi-step deployments
  - Enterprise-scale operations

### Learning Path Recommendation
```
Week 1-2: Interactive System Basics
Week 3-4: Understanding Ansible Concepts
Week 5-6: Advanced Interactive Features
Week 7-8: Introduction to Enterprise System
Week 9+: Advanced Enterprise Features
```

## Getting Started: Your First Hour

### Step 1: Verify Prerequisites (10 minutes)

```bash
# Check if Python is installed
python3 --version
# Should show Python 3.8 or higher

# Check if Ansible is installed
ansible --version
# Should show Ansible 2.12 or higher

# If not installed, install them:
pip3 install ansible
```

### Step 2: Understand the Project Structure (10 minutes)

```bash
# Navigate to the project
cd ansible-cloud-playbook

# Look at the structure
ls -la

# You should see:
# README.md          - Project overview
# requirements.yml   - Software dependencies
# playbooks/        - Automation scripts
# vars/             - Configuration settings
# inventory/        - Device lists
# src/              - Enterprise system
```

### Step 3: Your First Command (10 minutes)

```bash
# Test Ansible installation
ansible localhost -m ping

# Expected output:
# localhost | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

If this works, congratulations! Ansible is working.

### Step 4: Explore the Interactive System (20 minutes)

```bash
# Look at the interactive script
ls -la *.sh

# You should see files like:
# network-deploy.sh  - Interactive network wizard
```

**Note**: We'll run this in the next section after setup.

### Step 5: Review Sample Files (10 minutes)

```bash
# Look at a sample playbook
cat playbooks/create-instance.yml

# Look at sample variables
cat vars/development.yml

# Look at sample inventory
cat inventory/hosts.yml
```

Don't worry if you don't understand everything yet. Just get familiar with the file types.

## Basic Concepts Explained

### Playbooks: Your Automation Scripts

Think of playbooks as step-by-step instruction manuals:

```yaml
---
# This is a playbook
- name: Configure a switch (This is the title)
  hosts: switches (These are the devices to configure)
  tasks: (These are the steps)
    - name: Set hostname (Step 1)
      ios_config:
        lines: "hostname {{ hostname }}"
    
    - name: Create VLAN (Step 2)  
      ios_config:
        lines:
          - "vlan {{ vlan_id }}"
          - "name {{ vlan_name }}"
```

### Variables: Your Configuration Settings

Variables let you reuse the same playbook with different settings:

```yaml
# For Switch 1:
hostname: "SWITCH-01"
vlan_id: 100
vlan_name: "USERS"

# For Switch 2 (same playbook, different variables):
hostname: "SWITCH-02"  
vlan_id: 200
vlan_name: "SERVERS"
```

### Inventory: Your Device Directory

```yaml
---
# This lists all your devices
all:
  children:
    switches:  # Group of switches
      hosts:
        switch-01:
          ansible_host: 192.168.1.10  # IP address
          device_type: catalyst_2960
        switch-02:
          ansible_host: 192.168.1.11
          device_type: catalyst_3560
    
    routers:  # Group of routers
      hosts:
        router-01:
          ansible_host: 192.168.1.1
          device_type: isr_4000
```

### Templates: Configuration Generators

Templates generate actual device configurations:

```jinja2
{# This is a template file #}
hostname {{ hostname }}
!
vlan {{ vlan_id }}
 name {{ vlan_name }}
!
interface GigabitEthernet0/1
 description Uplink to {{ uplink_device }}
 switchport access vlan {{ vlan_id }}
!
```

When Ansible processes this template with variables:
- `hostname = "SWITCH-01"`
- `vlan_id = 100`
- `vlan_name = "USERS"`
- `uplink_device = "ROUTER-01"`

It generates:
```
hostname SWITCH-01
!
vlan 100
 name USERS
!
interface GigabitEthernet0/1
 description Uplink to ROUTER-01
 switchport access vlan 100
!
```

## Your First Network Configuration

### Scenario: Configure a Simple Network

Let's configure a basic network with:
- 1 router
- 2 switches  
- 3 VLANs (Users, Servers, Management)

### Step 1: Plan Your Network

```
Network Plan:
- Router: 192.168.1.1 (gateway for all VLANs)
- Switch 1: 192.168.1.10 (access switch)
- Switch 2: 192.168.1.11 (access switch)

VLANs:
- VLAN 10: Users (192.168.10.0/24)
- VLAN 20: Servers (192.168.20.0/24)  
- VLAN 99: Management (192.168.99.0/24)
```

### Step 2: Use the Interactive Wizard

```bash
# Run the interactive network wizard
./network-deploy.sh
```

The wizard will ask you questions:

```
How many switches do you want to configure? 2
How many routers do you want to configure? 1

Enter the starting VLAN ID: 10
How many VLANs to create? 3

VLAN 10 name: Users
VLAN 11 name: Servers  
VLAN 12 name: Management

Select Spanning Tree Protocol:
1. PVST+
2. Rapid PVST+
3. MST
Enter your choice: 2

Select routing protocol:
1. OSPF
2. EIGRP
3. Static routing
Enter your choice: 1

Enable SSH? (y/n): y
Enable SNMP? (y/n): y

Enter credentials for Switch 1:
IP Address: 192.168.1.10
Username: admin
Password: [hidden]
Enable Password: [hidden]

[Repeat for all devices...]
```

### Step 3: Review Generated Configuration

```bash
# Look at what the wizard created
ls -la configs/

# Check the inventory
cat configs/inventory.yml

# Check the playbook
cat configs/playbooks/deploy_network.yml

# Check the generated templates
ls -la configs/templates/
```

### Step 4: Deploy the Configuration

```bash
# Test connectivity first
ansible all -i configs/inventory.yml -m ping

# Deploy the configuration
ansible-playbook -i configs/inventory.yml configs/playbooks/deploy_network.yml

# Test the deployment
ansible-playbook -i configs/inventory.yml configs/playbooks/test_connectivity.yml
```

### Step 5: Verify the Results

```bash
# Check VLAN configuration on switches
ansible switches -i configs/inventory.yml -m ios_command -a "commands='show vlan brief'"

# Check routing on router
ansible routers -i configs/inventory.yml -m ios_command -a "commands='show ip route'"

# Check interface status
ansible all -i configs/inventory.yml -m ios_command -a "commands='show ip interface brief'"
```

## Understanding What Happened

### The Wizard Process

1. **Collected Information**: Asked you about your network requirements
2. **Generated Inventory**: Created a list of your devices and their credentials
3. **Generated Variables**: Created configuration settings based on your inputs
4. **Generated Templates**: Created device configuration templates
5. **Created Playbook**: Created automation script to deploy everything

### The Deployment Process

1. **Connectivity Test**: Verified Ansible can reach all devices
2. **Backup**: Saved current device configurations (safety first!)
3. **Deploy Base Config**: Applied hostname, management settings
4. **Deploy VLANs**: Created VLANs on switches
5. **Deploy Interfaces**: Configured switch ports
6. **Deploy Routing**: Configured routing protocol on router
7. **Verify**: Tested that everything works

### Files Created

```
configs/
├── inventory.yml              # Your device list
├── group_vars/
│   └── all.yml               # Global settings
├── host_vars/
│   ├── switch-01.yml         # Switch 1 specific settings  
│   ├── switch-02.yml         # Switch 2 specific settings
│   └── router-01.yml         # Router specific settings
├── playbooks/
│   ├── deploy_network.yml    # Main deployment script
│   └── test_connectivity.yml # Testing script
└── templates/
    ├── switch_config.j2      # Switch configuration template
    └── router_config.j2      # Router configuration template
```

## Common Beginner Mistakes and How to Avoid Them

### Mistake 1: Not Testing Connectivity First

**Wrong Way**:
```bash
# Immediately running deployment without testing
ansible-playbook configs/playbooks/deploy_network.yml
```

**Right Way**:
```bash
# Always test connectivity first
ansible all -i configs/inventory.yml -m ping
# Only proceed if all devices respond
```

### Mistake 2: Not Backing Up Configurations

**Prevention**: The platform automatically creates backups, but you can manually create them:
```bash
# Create manual backup
ansible all -i configs/inventory.yml -m ios_command -a "commands='show running-config'" > backup.txt
```

### Mistake 3: Running in Production Without Testing

**Learning Environment Setup**:
```bash
# Use packet tracer, GNS3, or lab devices
# Never test on production devices initially
```

### Mistake 4: Not Understanding Idempotency

**What is Idempotency?**
Running the same playbook multiple times should produce the same result without causing problems.

**Example**:
```yaml
# This is idempotent (safe to run multiple times)
- name: Create VLAN 10
  ios_config:
    lines:
      - "vlan 10"
      - "name USERS"

# This is NOT idempotent (could cause problems)
- name: Add VLAN (wrong way)
  ios_command:
    commands: "vlan 10; name USERS"
```

### Mistake 5: Hardcoding Values

**Wrong Way**:
```yaml
- name: Configure hostname
  ios_config:
    lines: "hostname SWITCH-01"  # Hardcoded
```

**Right Way**:
```yaml
- name: Configure hostname  
  ios_config:
    lines: "hostname {{ hostname }}"  # Uses variable
```

## Troubleshooting Your First Issues

### Issue: "Connection Refused"

**Symptoms**:
```
fatal: [switch-01]: UNREACHABLE! => {
    "msg": "Failed to connect to the host via ssh: ssh: connect to host 192.168.1.10 port 22: Connection refused"
}
```

**Solutions**:
1. **Check IP Address**: Can you ping the device?
   ```bash
   ping 192.168.1.10
   ```

2. **Check SSH**: Is SSH enabled on the device?
   ```bash
   telnet 192.168.1.10 22
   ```

3. **Enable SSH on Device** (via console):
   ```
   configure terminal
   ip domain-name company.local
   crypto key generate rsa general-keys modulus 2048
   ip ssh version 2
   username admin privilege 15 secret YourPassword
   line vty 0 15
   transport input ssh
   login local
   end
   copy running-config startup-config
   ```

### Issue: "Authentication Failed"

**Symptoms**:
```
fatal: [switch-01]: FAILED! => {
    "msg": "Authentication failed: Invalid username or password"
}
```

**Solutions**:
1. **Check Credentials**: Are username/password correct?
2. **Check Enable Password**: Is the enable password correct?
3. **Test Manually**:
   ```bash
   ssh admin@192.168.1.10
   enable
   # Enter enable password
   ```

### Issue: "Module Not Found"

**Symptoms**:
```
fatal: [switch-01]: FAILED! => {
    "msg": "couldn't resolve module/action 'ios_config'"
}
```

**Solution**:
```bash
# Install required collections
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install -r requirements.yml
```

### Issue: "Template Error"

**Symptoms**:
```
fatal: [switch-01]: FAILED! => {
    "msg": "TemplateSyntaxError: unexpected char '!' at 45"
}
```

**Solution**: Check your template files for Cisco IOS comments (`!`) inside Jinja2 template blocks. Use Jinja2 comments instead:
```jinja2
{# This is a Jinja2 comment - GOOD #}
! This is a Cisco comment - GOOD when outside template blocks

{% for vlan in vlans %}
{# This comment is safe inside template blocks #}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
```

## Practice Exercises

### Exercise 1: Modify VLAN Names

1. Look at your generated `host_vars/switch-01.yml`
2. Change the VLAN names
3. Re-run the deployment
4. Verify the changes

```bash
# Edit the file
vim configs/host_vars/switch-01.yml

# Change:
vlans:
  - id: 10
    name: "USERS"        # Change this
  - id: 11  
    name: "SERVERS"      # Change this

# Re-deploy
ansible-playbook -i configs/inventory.yml configs/playbooks/deploy_network.yml

# Verify
ansible switches -i configs/inventory.yml -m ios_command -a "commands='show vlan brief'"
```

### Exercise 2: Add a New VLAN

1. Add VLAN 30 for "GUESTS"
2. Deploy the change
3. Verify it was created

### Exercise 3: Add Management Configuration

1. Add NTP server configuration
2. Add SNMP community strings
3. Deploy and verify

### Exercise 4: Create a New Playbook

Create a simple playbook that only shows device information:

```yaml
---
# File: show_device_info.yml
- name: Show Device Information
  hosts: all
  gather_facts: false
  
  tasks:
    - name: Show device version
      ios_command:
        commands: "show version"
      register: version_output
    
    - name: Display version information
      debug:
        var: version_output.stdout_lines[0]
```

Run it:
```bash
ansible-playbook -i configs/inventory.yml show_device_info.yml
```

## Moving to the Next Level

### When You're Ready for More

You're ready to move beyond the basics when you can:

✅ Successfully run the interactive wizard
✅ Understand the generated files
✅ Modify variables and re-deploy
✅ Troubleshoot basic connectivity issues
✅ Create simple playbooks
✅ Understand the difference between playbooks, inventory, and variables

### Next Steps

1. **Advanced Interactive Features**: Learn about the AWS automation features
2. **Understanding Enterprise System**: Explore the enterprise-grade automation
3. **Custom Playbooks**: Write your own automation scripts
4. **Advanced Templates**: Create more sophisticated configuration templates
5. **Integration**: Connect with monitoring and backup systems

### Recommended Learning Path

```
✅ Beginner's Guide (You are here)
→ Interactive Automation Tutorial (Next: hands-on practice)
→ Configuration Management Guide (Learn advanced variable management)
→ Enterprise Deployment Guide (Production-grade automation)
→ Best Practices Guide (Professional techniques)
```

## Getting Help

### Documentation Resources
- **Interactive Tutorial**: [interactive-tutorial.md](interactive-tutorial.md) - Detailed hands-on guide
- **Troubleshooting Guide**: [troubleshooting.md](troubleshooting.md) - Common issues and solutions
- **Configuration Management**: [configuration-management.md](configuration-management.md) - Advanced variable usage

### Community Resources
- **Ansible Documentation**: https://docs.ansible.com/
- **Cisco Ansible Modules**: https://docs.ansible.com/ansible/latest/collections/cisco/ios/
- **Network Automation Community**: https://www.reddit.com/r/networking/

### Practice Tips

1. **Start Small**: Begin with 1-2 devices
2. **Use Lab Equipment**: Never practice on production
3. **Read Error Messages**: They usually tell you exactly what's wrong
4. **Take Backups**: Always backup before making changes
5. **Version Control**: Use git to track your changes
6. **Document Everything**: Write down what works

### Common Beginner Questions

**Q: Can I break my network devices with Ansible?**
A: Yes, if you deploy incorrect configurations. Always test in a lab first and take backups.

**Q: How long does it take to learn network automation?**
A: Basic competency: 2-4 weeks. Professional proficiency: 3-6 months. Mastery: 1-2 years.

**Q: Do I need to be a programmer?**
A: No, but basic scripting knowledge helps. Ansible uses YAML, which is human-readable.

**Q: What if I make a mistake?**
A: The platform creates automatic backups. You can also practice rollback procedures.

**Q: Can I use this with non-Cisco equipment?**
A: The platform is designed for Cisco, but Ansible supports many vendors. You'd need to modify the templates and modules.

## Conclusion

Congratulations on starting your network automation journey! Remember:

🎯 **Key Concepts Learned**:
- What network automation is and why it's valuable
- Basic Ansible concepts (playbooks, inventory, variables, templates)
- How to use the interactive wizard
- Common troubleshooting steps
- Basic file structure and organization

🚀 **You Can Now**:
- Run the interactive network wizard
- Understand generated configuration files
- Make basic modifications to deployments
- Troubleshoot common connectivity issues
- Create simple automation scripts

📚 **Next Learning Steps**:
- Practice with the exercises above
- Explore the Interactive Automation Tutorial
- Experiment with different network topologies
- Learn about AWS automation features
- Begin understanding the enterprise system

Remember: Every expert was once a beginner. Take your time, practice regularly, and don't be afraid to experiment in your lab environment.

---

**🌟 Welcome to Network Automation!** You've taken the first step into a powerful world of infrastructure automation. Continue with the [Interactive Automation Tutorial](interactive-tutorial.md) to gain hands-on experience with more advanced features.