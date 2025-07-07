# Ansible AWS Setup

Basic Ansible playbook to create EC2 instances.

## Setup

Install requirements:
```bash
pip install ansible
ansible-galaxy collection install -r requirements.yml
```

Configure AWS credentials:
```bash
aws configure
```

Create key pair in AWS console and download the .pem file to `~/.ssh/`

## Usage

Edit `create-instance.yml` and set your key pair name:
```yaml
key_name: "your-key-name"
```

Run the playbook:
```bash
ansible-playbook create-instance.yml
```

## What it does

- Creates security group allowing SSH and HTTP
- Launches t3.micro instance with latest Amazon Linux
- Outputs connection info

## Connect to instance

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@PUBLIC_IP
```