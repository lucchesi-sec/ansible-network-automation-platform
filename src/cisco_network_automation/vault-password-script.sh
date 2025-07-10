#!/bin/bash

# Ansible Vault Password Management Script
# This script provides secure password management for Ansible Vault

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VAULT_DIR="vault"
VAULT_PASSWORD_FILE=".vault_password"
VAULT_PASSWORD_ENV="ANSIBLE_VAULT_PASSWORD"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if vault directory exists
check_vault_directory() {
    if [ ! -d "$VAULT_DIR" ]; then
        log_error "Vault directory '$VAULT_DIR' does not exist"
        exit 1
    fi
}

# Generate a secure random password
generate_vault_password() {
    if command -v openssl &> /dev/null; then
        openssl rand -base64 32
    elif command -v python3 &> /dev/null; then
        python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    else
        log_error "Neither openssl nor python3 available for password generation"
        exit 1
    fi
}

# Create vault password file
create_vault_password() {
    log_info "Creating vault password file..."
    
    if [ -f "$VAULT_PASSWORD_FILE" ]; then
        log_warning "Vault password file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operation cancelled"
            exit 0
        fi
    fi
    
    # Generate secure password
    VAULT_PASSWORD=$(generate_vault_password)
    
    # Write to file with restricted permissions
    echo "$VAULT_PASSWORD" > "$VAULT_PASSWORD_FILE"
    chmod 600 "$VAULT_PASSWORD_FILE"
    
    log_success "Vault password file created: $VAULT_PASSWORD_FILE"
    log_warning "Please store this password securely and consider using a password manager"
    log_info "Password: $VAULT_PASSWORD"
}

# Encrypt vault files
encrypt_vault_files() {
    log_info "Encrypting vault files..."
    
    if [ ! -f "$VAULT_PASSWORD_FILE" ]; then
        log_error "Vault password file not found. Run 'create-password' first."
        exit 1
    fi
    
    check_vault_directory
    
    # Find all .yml files in vault directory
    vault_files=$(find "$VAULT_DIR" -name "*.yml" -type f)
    
    if [ -z "$vault_files" ]; then
        log_warning "No vault files found in $VAULT_DIR"
        exit 0
    fi
    
    for file in $vault_files; do
        if ansible-vault view "$file" --vault-password-file="$VAULT_PASSWORD_FILE" &>/dev/null; then
            log_info "File $file is already encrypted"
        else
            log_info "Encrypting $file..."
            ansible-vault encrypt "$file" --vault-password-file="$VAULT_PASSWORD_FILE"
            log_success "Encrypted $file"
        fi
    done
    
    log_success "All vault files encrypted"
}

# Decrypt vault files
decrypt_vault_files() {
    log_info "Decrypting vault files..."
    
    if [ ! -f "$VAULT_PASSWORD_FILE" ]; then
        log_error "Vault password file not found"
        exit 1
    fi
    
    check_vault_directory
    
    # Find all .yml files in vault directory
    vault_files=$(find "$VAULT_DIR" -name "*.yml" -type f)
    
    if [ -z "$vault_files" ]; then
        log_warning "No vault files found in $VAULT_DIR"
        exit 0
    fi
    
    for file in $vault_files; do
        if ansible-vault view "$file" --vault-password-file="$VAULT_PASSWORD_FILE" &>/dev/null; then
            log_info "Decrypting $file..."
            ansible-vault decrypt "$file" --vault-password-file="$VAULT_PASSWORD_FILE"
            log_success "Decrypted $file"
        else
            log_info "File $file is already decrypted"
        fi
    done
    
    log_success "All vault files decrypted"
}

# View encrypted vault file
view_vault_file() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        log_error "File $file not found"
        exit 1
    fi
    
    if [ ! -f "$VAULT_PASSWORD_FILE" ]; then
        log_error "Vault password file not found"
        exit 1
    fi
    
    log_info "Viewing encrypted file: $file"
    ansible-vault view "$file" --vault-password-file="$VAULT_PASSWORD_FILE"
}

# Edit encrypted vault file
edit_vault_file() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        log_error "File $file not found"
        exit 1
    fi
    
    if [ ! -f "$VAULT_PASSWORD_FILE" ]; then
        log_error "Vault password file not found"
        exit 1
    fi
    
    log_info "Editing encrypted file: $file"
    ansible-vault edit "$file" --vault-password-file="$VAULT_PASSWORD_FILE"
}

# Setup environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    if [ ! -f "$VAULT_PASSWORD_FILE" ]; then
        log_error "Vault password file not found"
        exit 1
    fi
    
    export ANSIBLE_VAULT_PASSWORD_FILE="$(pwd)/$VAULT_PASSWORD_FILE"
    
    log_success "Environment variables set:"
    log_info "ANSIBLE_VAULT_PASSWORD_FILE=$ANSIBLE_VAULT_PASSWORD_FILE"
    log_info "Add this to your shell profile for persistent access"
}

# Show usage information
show_usage() {
    echo "Usage: $0 {create-password|encrypt|decrypt|view|edit|setup-env}"
    echo ""
    echo "Commands:"
    echo "  create-password    Create a new vault password file"
    echo "  encrypt           Encrypt all vault files"
    echo "  decrypt           Decrypt all vault files"
    echo "  view <file>       View encrypted vault file"
    echo "  edit <file>       Edit encrypted vault file"
    echo "  setup-env         Setup environment variables"
    echo ""
    echo "Examples:"
    echo "  $0 create-password"
    echo "  $0 encrypt"
    echo "  $0 view vault/network_credentials.yml"
    echo "  $0 edit vault/aws_credentials.yml"
}

# Main function
main() {
    case "${1:-}" in
        "create-password")
            create_vault_password
            ;;
        "encrypt")
            encrypt_vault_files
            ;;
        "decrypt")
            decrypt_vault_files
            ;;
        "view")
            if [ -z "${2:-}" ]; then
                log_error "Please specify a file to view"
                show_usage
                exit 1
            fi
            view_vault_file "$2"
            ;;
        "edit")
            if [ -z "${2:-}" ]; then
                log_error "Please specify a file to edit"
                show_usage
                exit 1
            fi
            edit_vault_file "$2"
            ;;
        "setup-env")
            setup_environment
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"