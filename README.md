# Ansible Cloud Playbook Project

## Overview
This project demonstrates basic Ansible playbooks for managing cloud instances. It's designed for beginners learning infrastructure as code.

## Project Structure
- **inventory/**: Contains host definitions (e.g., production.ini).
- **playbooks/**: Main playbooks for creating and destroying instances.
- **group_vars/**: Shared variables for all hosts.
- **roles/**: Reusable roles for common tasks.

## Getting Started
1. Install Ansible: `pip install ansible`
2. Edit inventory/production.ini with your hosts.
3. Run a playbook: `ansible-playbook playbooks/create-instance.yml`

## Common Troubleshooting
- **Error: Host not found**: Check inventory file for correct hostnames.
- **Permission issues**: Ensure your user has SSH access to hosts.

For more details, see [Ansible Documentation](https://docs.ansible.com/).
