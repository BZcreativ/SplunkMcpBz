# Kubernetes Deployment Guide - Splunk MCP Server

## Overview
This guide provides comprehensive instructions for deploying the Splunk MCP Server on Kubernetes with enterprise-grade features including high availability, monitoring, and security.

## Prerequisites

### Required Tools
- Kubernetes cluster (v1.20+)
- kubectl configured
- Helm 3.x (optional but recommended)
- Docker registry access
- cert-manager for SSL certificates
- NGINX Ingress Controller
- Prometheus for monitoring

### Cluster Requirements
- Minimum 3 worker nodes
- 2 CPU cores per node
- 4GB RAM per node
- 10GB storage per node
- Load balancer support

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingress (HTTPS)                         │
│              splunk-mcp.example.com                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              NGINX Ingress Controller                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              Splunk MCP Service (ClusterIP)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Pod 1     │  │   Pod 2     │  │   Pod 3     │       │
│  │ (Replica 1) │  │ (Replica 2) │  │ (Replica 3) │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                │                │               │
│         └────────────────┴────────────────┘               │
│                    Pod Anti-Affinity                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              Redis Service (ClusterIP)                     │
│                    ┌─────────────┐                         │
│                    │ Redis Pod   │                         │
│                    │ (Stateful)  │                         │
│                    └──────┬──────┘                         │
│                           │                                │
│                    ┌──────┴──────┐                         │
│                    │  PVC (1GB)  │                         │
│                    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Clone and Prepare
```bash
# Clone the repository
git clone https://github.com/BZcreativ/SplunkMcpBz.git
cd SplunkMcpBz

# Create namespace
kubectl apply -f k8s/namespace.yaml
```

### 2. Configure Secrets
```bash
# Edit secrets with your actual values
kubectl create secret generic splunk-mcp-secrets \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=ADMIN_PASSWORD=$(openssl rand -hex 16) \
  --from-literal=USER_PASSWORD=$(openssl rand -hex 16) \
  --from-literal=READONLY_PASSWORD=$(openssl rand -hex 16) \
  --from-literal=SPLUNK_TOKEN="your-splunk-token" \
  -n splunk-mcp
```

### 3. Deploy Redis
```bash
kubectl apply -f k8s/redis-deployment.yaml
```

### 4. Deploy Application
```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Deploy the application
kubectl apply -f k8s/deployment.yaml

# Create services
kubectl apply -f k8s/service.yaml
```

### 5. Configure SSL (Production)
```bash
# Install cert-manager if not already installed
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Apply ingress
kubectl apply -f k8s/ingress.yaml
```

## Detailed Configuration

### Environment Variables
All configuration is managed through ConfigMaps and Secrets:

| Variable | Description | Default |
|----------|-------------|---------|
| `SPLUNK_HOST` | Splunk server hostname | `splunk.example.com` |
| `SPLUNK_PORT` | Splunk management port | `8089` |
| `SPLUNK_TOKEN` | Splunk authentication token | **Required** |
| `REDIS_HOST` | Redis service hostname | `redis-service` |
| `REDIS_PORT` | Redis port | `6379` |
| `SECRET_KEY` | JWT secret key | **Required** |
| `LOG_LEVEL` | Application log level | `INFO` |

### Resource Requirements
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Scaling Configuration
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

## Security Configuration

### Pod Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
```

### Container Security Context
```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
```

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: splunk-mcp-network-policy
  namespace: splunk-mcp
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: splunk-mcp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8334
    - protocol: TCP
      port: 9090
  egress:
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

## Monitoring Setup

### Prometheus ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: splunk-mcp-metrics
  namespace: splunk-mcp
  labels:
    app.kubernetes.io/name: splunk-mcp
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: splunk-mcp
      app.kubernetes.io/component: metrics
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Grafana Dashboard
Import the provided Grafana dashboard JSON:
```bash
kubectl create configmap grafana-dashboard-splunk-mcp \
  --from-file=dashboard.json=k8s/grafana-dashboard.json \
  -n monitoring
```

## High Availability Configuration

### Pod Disruption Budget
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: splunk-mcp-pdb
  namespace: splunk-mcp
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: splunk-mcp
```

### Pod Anti-Affinity
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - splunk-mcp
        topologyKey: kubernetes.io/hostname
```

## Backup and Disaster Recovery

### Redis Backup
```bash
# Create backup
kubectl exec -n splunk-mcp deployment/redis -- redis-cli BGSAVE

# Copy backup
kubectl cp splunk-mcp/redis-0:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

### Application State Backup
```bash
# Export configuration
kubectl get configmap splunk-mcp-config -n splunk-mcp -o yaml > config-backup.yaml
kubectl get secret splunk-mcp-secrets -n splunk-mcp -o yaml > secrets-backup.yaml
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n splunk-mcp
kubectl describe pod <pod-name> -n splunk-mcp
```

### View Logs
```bash
kubectl logs -f deployment/splunk-mcp -n splunk-mcp
```

### Check Services
```bash
kubectl get svc -n splunk-mcp
kubectl describe svc splunk-mcp-service -n splunk-mcp
```

### Test Connectivity
```bash
# Port forward for testing
kubectl port-forward svc/splunk-mcp-service 8334:8334 -n splunk-mcp

# Test health endpoint
curl http://localhost:8334/health
```

### Debug Redis Connection
```bash
kubectl exec -it deployment/redis -n splunk-mcp -- redis-cli ping
```

## Performance Tuning

### JVM Options (if applicable)
```yaml
env:
- name: JAVA_OPTS
  value: "-Xms256m -Xmx512m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

### Connection Pool Settings
```yaml
env:
- name: REDIS_MAX_CONNECTIONS
  value: "20"
- name: SPLUNK_MAX_CONNECTIONS
  value: "10"
```

## Upgrade Procedures

### Rolling Update
```bash
# Update image
kubectl set image deployment/splunk-mcp splunk-mcp=splunk-mcp:1.1.0 -n splunk-mcp

# Monitor rollout
kubectl rollout status deployment/splunk-mcp -n splunk-mcp
```

### Rollback
```bash
kubectl rollout undo deployment/splunk-mcp -n splunk-mcp
```

## Cleanup

### Remove All Resources
```bash
kubectl delete namespace splunk-mcp
```

### Remove Specific Components
```bash
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/redis-deployment.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
kubectl delete -f k8s/namespace.yaml
```

## Support

For issues or questions:
1. Check pod logs: `kubectl logs <pod-name> -n splunk-mcp`
2. Check events: `kubectl get events -n splunk-mcp`
3. Review resource usage: `kubectl top pods -n splunk-mcp`
4. Check ingress status: `kubectl get ingress -n splunk-mcp`
5. Verify secrets: `kubectl get secrets -n splunk-mcp`