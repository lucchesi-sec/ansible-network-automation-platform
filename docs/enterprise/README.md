# Enterprise Network Deployment System
*Quick reference for the cisco_network_automation implementation*

> 📖 **Complete Documentation**: See [Documentation Index](../../DOCUMENTATION_INDEX.md) for comprehensive guides
> 
> **API Reference**: [API_REFERENCE.md](../../API_REFERENCE.md)  
> **Architecture Guide**: [ARCHITECTURE.md](../../ARCHITECTURE.md)  
> **User Guide**: [docs/enterprise-deployment.md](../../docs/enterprise-deployment.md)  
> **Security Guide**: [SECURITY_IMPLEMENTATION_GUIDE.md](../../SECURITY_IMPLEMENTATION_GUIDE.md)

## Quick Start

```bash
# Production deployment
./deploy_enterprise.sh --environment production --vault-password vault-password-script.sh

# Development with verbose output
./deploy_enterprise.sh --environment development --verbose

# Emergency rollback
./deploy_enterprise.sh --rollback --environment production
```

## Directory Structure

```
src/cisco_network_automation/
├── deploy_enterprise.sh                # Main deployment script
├── playbooks/                          # 12 orchestration playbooks
├── roles/                              # 19 infrastructure roles
├── inventory/                          # Production & security inventories
├── group_vars/                         # Environment variables
├── logs/                              # Deployment artifacts
└── archive/                           # Historical documentation
```

## Infrastructure Overview

- **19 Infrastructure Roles** across 4 categories
- **6-Phase Deployment** with validation gates
- **Multi-Environment Support** (dev/staging/production)
- **Backup & Rollback** automation
- **Comprehensive Logging** and audit trails

## Command Reference

### Deployment Options
- `-e, --environment ENV`: Deployment environment (development|staging|production)
- `-i, --inventory FILE`: Inventory file (default: production.yml)
- `-v, --vault-password FILE`: Vault password file path
- `-d, --dry-run`: Check mode
- `-V, --verbose`: Verbose output
- `-r, --rollback`: Emergency rollback

### Emergency Procedures
```bash
# Quick validation
ansible-playbook playbooks/validation_suite.yml -i inventory/production.yml

# Security audit
ansible-playbook playbooks/security_audit.yml -i inventory/production.yml

# Manual rollback
ansible-playbook playbooks/rollback_deployment.yml -i inventory/production.yml
```

## Production Checklist

See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for detailed deployment validation.

---

**For complete documentation, troubleshooting, and best practices**, refer to the [comprehensive documentation suite](../../DOCUMENTATION_INDEX.md) in the project root.