#\!/bin/bash

# Network Deployment Orchestration Script
# Executes master network deployment with comprehensive automation

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYBOOK_DIR="${SCRIPT_DIR}/playbooks"
INVENTORY_DIR="${SCRIPT_DIR}/inventory"
LOG_DIR="${SCRIPT_DIR}/logs"

# Default values
ENVIRONMENT="production"
INVENTORY_FILE="production.yml"
VAULT_PASSWORD_FILE=""
DRY_RUN=false
VERBOSE=false
SKIP_VALIDATION=false
FORCE_ROLLBACK=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    cat << 'USAGE_EOF'
Network Deployment Orchestration Script

Usage: ./deploy_network.sh [OPTIONS]

OPTIONS:
    -e, --environment ENV       Deployment environment (development|staging|production)
                               Default: production
    -i, --inventory FILE        Inventory file to use
                               Default: production.yml
    -v, --vault-password FILE   Vault password file path
    -d, --dry-run              Perform dry run (check mode)
    -V, --verbose              Enable verbose output
    -s, --skip-validation      Skip pre-deployment validation
    -r, --rollback             Force rollback to previous configuration
    -h, --help                 Display this help message

EXAMPLES:
    # Standard production deployment
    ./deploy_network.sh --environment production --vault-password vault-password-script.sh

    # Development deployment with verbose output
    ./deploy_network.sh --environment development --verbose

    # Dry run for staging environment
    ./deploy_network.sh --environment staging --dry-run

    # Emergency rollback
    ./deploy_network.sh --rollback --environment production

USAGE_EOF
}

# Function to validate prerequisites
validate_prerequisites() {
    print_status "Validating deployment prerequisites..."
    
    if [[ \! -f "${PLAYBOOK_DIR}/master_network_deployment.yml" ]]; then
        print_error "Master deployment playbook not found. Please run from the correct directory."
        exit 1
    fi
    
    if [[ \! -f "${INVENTORY_DIR}/${INVENTORY_FILE}" ]]; then
        print_error "Inventory file ${INVENTORY_FILE} not found in ${INVENTORY_DIR}"
        exit 1
    fi
    
    if \! command -v ansible-playbook &> /dev/null; then
        print_error "ansible-playbook command not found. Please install Ansible."
        exit 1
    fi
    
    if [[ -n "${VAULT_PASSWORD_FILE}" && \! -f "${VAULT_PASSWORD_FILE}" ]]; then
        print_error "Vault password file ${VAULT_PASSWORD_FILE} not found."
        exit 1
    fi
    
    mkdir -p "${LOG_DIR}"
    
    print_success "Prerequisites validation completed"
}

# Function to execute deployment
execute_deployment() {
    print_status "Starting network deployment for environment: ${ENVIRONMENT}"
    
    local ansible_cmd="ansible-playbook"
    local playbook="${PLAYBOOK_DIR}/master_network_deployment.yml"
    local inventory_arg="-i ${INVENTORY_DIR}/${INVENTORY_FILE}"
    local extra_vars="-e environment=${ENVIRONMENT}"
    
    if [[ -n "${VAULT_PASSWORD_FILE}" ]]; then
        ansible_cmd="${ansible_cmd} --vault-password-file ${VAULT_PASSWORD_FILE}"
    fi
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        ansible_cmd="${ansible_cmd} --check --diff"
        print_warning "Running in DRY RUN mode - no changes will be made"
    fi
    
    if [[ "${VERBOSE}" == "true" ]]; then
        ansible_cmd="${ansible_cmd} -vvv"
    fi
    
    local full_cmd="${ansible_cmd} ${inventory_arg} ${extra_vars} ${playbook}"
    
    print_status "Executing: ${full_cmd}"
    
    if eval "${full_cmd}"; then
        print_success "Network deployment completed successfully"
        return 0
    else
        print_error "Network deployment failed"
        return 1
    fi
}

# Function to execute rollback
execute_rollback() {
    print_warning "Initiating emergency rollback procedure..."
    
    local ansible_cmd="ansible-playbook"
    local playbook="${PLAYBOOK_DIR}/rollback_deployment.yml"
    local inventory_arg="-i ${INVENTORY_DIR}/${INVENTORY_FILE}"
    local extra_vars="-e rollback_reason='Emergency rollback requested by user'"
    
    if [[ -n "${VAULT_PASSWORD_FILE}" ]]; then
        ansible_cmd="${ansible_cmd} --vault-password-file ${VAULT_PASSWORD_FILE}"
    fi
    
    if [[ "${VERBOSE}" == "true" ]]; then
        ansible_cmd="${ansible_cmd} -vvv"
    fi
    
    local full_cmd="${ansible_cmd} ${inventory_arg} ${extra_vars} ${playbook}"
    
    print_status "Executing rollback: ${full_cmd}"
    
    if eval "${full_cmd}"; then
        print_success "Emergency rollback completed successfully"
        return 0
    else
        print_error "Emergency rollback failed"
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -i|--inventory)
            INVENTORY_FILE="$2"
            shift 2
            ;;
        -v|--vault-password)
            VAULT_PASSWORD_FILE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -V|--verbose)
            VERBOSE=true
            shift
            ;;
        -s|--skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        -r|--rollback)
            FORCE_ROLLBACK=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ \! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: ${ENVIRONMENT}. Must be development, staging, or production."
    exit 1
fi

# Main execution
main() {
    print_status "Network Deployment Orchestration Starting..."
    print_status "Environment: ${ENVIRONMENT}"
    print_status "Inventory: ${INVENTORY_FILE}"
    
    validate_prerequisites
    
    if [[ "${FORCE_ROLLBACK}" == "true" ]]; then
        execute_rollback
        exit $?
    fi
    
    if [[ "${SKIP_VALIDATION}" == "true" ]]; then
        print_warning "Pre-deployment validation will be skipped as requested"
    fi
    
    if execute_deployment; then
        print_success "=== NETWORK DEPLOYMENT ORCHESTRATION COMPLETE ==="
        print_success "Environment: ${ENVIRONMENT}"
        print_success "All 19 infrastructure roles deployed successfully"
        print_success "Check deployment logs in: ${LOG_DIR}"
        exit 0
    else
        print_error "=== NETWORK DEPLOYMENT FAILED ==="
        print_error "Check logs for details and consider running rollback"
        exit 1
    fi
}

main "$@"
