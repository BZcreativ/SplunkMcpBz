#!/bin/bash
# Kubernetes Deployment Script for Splunk MCP Server
# Usage: ./deploy-to-k8s.sh [environment] [domain]

set -e

# Configuration
ENVIRONMENT=${1:-development}
DOMAIN=${2:-splunk-mcp.local}
NAMESPACE="splunk-mcp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="${SCRIPT_DIR}/../k8s"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create namespace
create_namespace() {
    log_info "Creating namespace: ${NAMESPACE}"
    
    if kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        log_warning "Namespace ${NAMESPACE} already exists"
    else
        kubectl apply -f "${K8S_DIR}/namespace.yaml"
        log_success "Namespace created"
    fi
}

# Configure secrets
configure_secrets() {
    log_info "Configuring secrets..."
    
    # Generate random secrets if not provided
    if [[ "$ENVIRONMENT" == "development" ]]; then
        SECRET_KEY=$(openssl rand -hex 32)
        ADMIN_PASSWORD="dev-admin-password"
        USER_PASSWORD="dev-user-password"
        READONLY_PASSWORD="dev-readonly-password"
        SPLUNK_TOKEN="dev-splunk-token"
    else
        # For production, secrets should be provided externally
        if [[ -z "${SECRET_KEY}" ]]; then
            SECRET_KEY=$(openssl rand -hex 32)
            log_warning "Generated random SECRET_KEY - save this for production!"
        fi
        if [[ -z "${ADMIN_PASSWORD}" ]]; then
            log_error "ADMIN_PASSWORD must be set for production deployment"
            exit 1
        fi
        if [[ -z "${USER_PASSWORD}" ]]; then
            log_error "USER_PASSWORD must be set for production deployment"
            exit 1
        fi
        if [[ -z "${READONLY_PASSWORD}" ]]; then
            log_error "READONLY_PASSWORD must be set for production deployment"
            exit 1
        fi
        if [[ -z "${SPLUNK_TOKEN}" ]]; then
            log_error "SPLUNK_TOKEN must be set for production deployment"
            exit 1
        fi
    fi
    
    # Create or update secrets
    kubectl create secret generic splunk-mcp-secrets \
        --from-literal=SECRET_KEY="${SECRET_KEY}" \
        --from-literal=ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
        --from-literal=USER_PASSWORD="${USER_PASSWORD}" \
        --from-literal=READONLY_PASSWORD="${READONLY_PASSWORD}" \
        --from-literal=SPLUNK_TOKEN="${SPLUNK_TOKEN}" \
        --namespace="${NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets configured"
}

# Deploy Redis
deploy_redis() {
    log_info "Deploying Redis..."
    
    kubectl apply -f "${K8S_DIR}/redis-deployment.yaml"
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis \
        --namespace="${NAMESPACE}" --timeout=300s
    
    log_success "Redis deployed successfully"
}

# Deploy application
deploy_application() {
    log_info "Deploying Splunk MCP Server..."
    
    # Apply ConfigMap
    kubectl apply -f "${K8S_DIR}/configmap.yaml"
    
    # Deploy the application
    kubectl apply -f "${K8S_DIR}/deployment.yaml"
    
    # Create services
    kubectl apply -f "${K8S_DIR}/service.yaml"
    
    log_success "Application deployed successfully"
}

# Configure ingress
configure_ingress() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "Configuring production ingress with SSL..."
        
        # Check if cert-manager is installed
        if ! kubectl get crd clusterissuers.cert-manager.io &> /dev/null; then
            log_info "Installing cert-manager..."
            kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
            kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=cert-manager \
                --namespace=cert-manager --timeout=300s
        fi
        
        # Create ClusterIssuer
        kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@${DOMAIN}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
        
        # Update ingress with production domain
        sed "s/splunk-mcp.example.com/${DOMAIN}/g" "${K8S_DIR}/ingress.yaml" | kubectl apply -f -
        
        log_success "Production ingress configured for ${DOMAIN}"
    else
        log_info "Configuring development ingress..."
        
        # For development, use port-forward
        kubectl apply -f "${K8S_DIR}/ingress.yaml"
        log_warning "For development access, use: kubectl port-forward svc/splunk-mcp-service 8334:8334 -n ${NAMESPACE}"
    fi
}

# Wait for deployment
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    kubectl wait --for=condition=available deployment/splunk-mcp \
        --namespace="${NAMESPACE}" --timeout=600s
    
    log_success "Deployment is ready"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pods
    kubectl get pods -n "${NAMESPACE}"
    
    # Check services
    kubectl get svc -n "${NAMESPACE}"
    
    # Check ingress
    kubectl get ingress -n "${NAMESPACE}"
    
    # Test health endpoint
    if kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/name=splunk-mcp | grep -q "Running"; then
        log_info "Testing health endpoint..."
        
        # Port forward for testing
        kubectl port-forward svc/splunk-mcp-service 8334:8334 -n "${NAMESPACE}" &
        PF_PID=$!
        sleep 5
        
        if curl -s http://localhost:8334/health | grep -q "ok"; then
            log_success "Health check passed"
        else
            log_warning "Health check failed - check logs"
        fi
        
        kill $PF_PID 2>/dev/null || true
    fi
}

# Show deployment info
show_deployment_info() {
    log_info "Deployment Information:"
    echo "=================================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Namespace: ${NAMESPACE}"
    echo "Domain: ${DOMAIN}"
    echo ""
    
    if [[ "$ENVIRONMENT" == "development" ]]; then
        echo "Development Access:"
        echo "kubectl port-forward svc/splunk-mcp-service 8334:8334 -n ${NAMESPACE}"
        echo "Then visit: http://localhost:8334"
    else
        echo "Production Access:"
        echo "https://${DOMAIN}"
    fi
    
    echo ""
    echo "Monitoring:"
    echo "kubectl port-forward svc/splunk-mcp-metrics 9090:9090 -n ${NAMESPACE}"
    echo "Then visit: http://localhost:9090/metrics"
    echo ""
    echo "Logs:"
    echo "kubectl logs -f deployment/splunk-mcp -n ${NAMESPACE}"
    echo "=================================="
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Kill any remaining port-forward processes
    pkill -f "kubectl port-forward" || true
}

# Main deployment function
main() {
    log_info "Starting Splunk MCP Kubernetes deployment..."
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Domain: ${DOMAIN}"
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Execute deployment steps
    check_prerequisites
    create_namespace
    configure_secrets
    deploy_redis
    deploy_application
    configure_ingress
    wait_for_deployment
    verify_deployment
    show_deployment_info
    
    log_success "Deployment completed successfully!"
}

# Help function
show_help() {
    echo "Splunk MCP Kubernetes Deployment Script"
    echo ""
    echo "Usage: $0 [environment] [domain]"
    echo ""
    echo "Arguments:"
    echo "  environment    Deployment environment (development|production)"
    echo "  domain        Domain name for production (default: splunk-mcp.local)"
    echo ""
    echo "Environment Variables (for production):"
    echo "  SECRET_KEY        JWT secret key"
    echo "  ADMIN_PASSWORD    Admin user password"
    echo "  USER_PASSWORD     Standard user password"
    echo "  READONLY_PASSWORD Readonly user password"
    echo "  SPLUNK_TOKEN      Splunk authentication token"
    echo ""
    echo "Examples:"
    echo "  $0 development"
    echo "  $0 production splunk-mcp.example.com"
    echo "  SECRET_KEY=\$(openssl rand -hex 32) ADMIN_PASSWORD=secure123 $0 production"
}

# Handle help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@"