# Enterprise Cisco Network Automation Platform

Simple, powerful Ansible automation for Cisco enterprise networks.

## What This Does

Automates Cisco network infrastructure deployment across:
- Core, distribution, and edge routers
- Datacenter fabric switches  
- Zero-trust security policies
- AI-powered network monitoring
- Performance optimization
- Micro-segmentation

## Quick Start

1. **Install Requirements**
   ```bash
   pip install ansible
   ansible-galaxy install -r requirements.yml
   ```

2. **Configure Inventory**
   ```bash
   cp src/cisco_network_automation/inventory/production.yml.example inventory.yml
   # Edit inventory.yml with your devices
   ```

3. **Set Vault Password**
   ```bash
   echo "your-vault-password" > .vault_password
   chmod 600 .vault_password
   ```

4. **Deploy Network**
   ```bash
   cd src/cisco_network_automation
   ansible-playbook playbooks/master_enterprise_deployment.yml
   ```

## Project Structure

```
src/cisco_network_automation/
├── playbooks/           # Main deployment playbooks
├── roles/              # 19 specialized network roles
├── inventory/          # Device inventories
├── group_vars/         # Configuration variables
└── logs/              # Deployment logs
```

## Key Features

- **19 Specialized Roles**: BGP, VXLAN, QoS, Security, AI monitoring
- **Phased Deployment**: 6-phase rollout with validation
- **Zero-Trust Security**: Advanced micro-segmentation  
- **AI Integration**: Predictive analytics and self-healing
- **Enterprise Ready**: Backup, rollback, and audit trails

## Core Roles

| Role | Purpose |
|------|---------|
| `cisco_router` | Basic router configuration |
| `bgp_configuration` | BGP routing and policies |
| `leaf_spine_architecture` | Datacenter fabric |
| `vxlan_overlay` | VXLAN overlay networks |
| `security_hardening` | Security baseline |
| `zero_trust_core` | Zero-trust policies |
| `micro_segmentation` | Network segmentation |
| `ai_network_intelligence` | AI monitoring |
| `performance_optimization` | Performance tuning |

## Requirements

- Ansible 2.9+
- Python 3.7+
- Cisco devices with SSH access
- Network connectivity to all devices

## Configuration

1. **Inventory**: Define devices in `inventory/production.yml`
2. **Variables**: Set parameters in `group_vars/`
3. **Vault**: Store secrets in `group_vars/vault.yml`

## Deployment Phases

1. **Phase 1**: Infrastructure validation
2. **Phase 2**: Core network deployment  
3. **Phase 3**: Advanced features
4. **Phase 4**: Security and AI
5. **Phase 5**: Final validation
6. **Phase 6**: Summary and reporting

## Validation

Run validation before deployment:
```bash
ansible-playbook playbooks/validate_pre_deployment.yml
```

## Troubleshooting

- Check logs in `logs/ansible.log`
- Validate connectivity: `ansible all -m ping`
- Test configuration: `ansible-playbook playbooks/validation_suite.yml`

## Support

This platform automates enterprise Cisco networks with industry best practices for security, performance, and reliability.