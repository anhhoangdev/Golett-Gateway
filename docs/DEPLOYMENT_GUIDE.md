# Golett AI - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying Golett AI in various environments, from development setups to production-grade deployments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Security Considerations](#security-considerations)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

#### Minimum Requirements (Development)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Linux, macOS, or Windows with WSL2

#### Recommended Requirements (Production)
- **CPU**: 8+ cores
- **RAM**: 32+ GB
- **Storage**: 200+ GB SSD
- **OS**: Linux (Ubuntu 20.04+ or CentOS 8+)

### Software Dependencies

#### Core Dependencies
- **Python**: 3.9+
- **PostgreSQL**: 13+
- **Qdrant**: 1.7+
- **Redis**: 6+ (optional, for caching)

#### Development Dependencies
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

---

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/golett-gateway.git
cd golett-gateway
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 3. Database Setup

#### PostgreSQL Setup

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE golett_db;
CREATE USER golett_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE golett_db TO golett_user;
\q
```

#### Qdrant Setup

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant:latest

# Or install locally
wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz
tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz
./qdrant
```

### 4. Environment Configuration

Create `.env` file:

```bash
# Database Configuration
POSTGRES_CONNECTION=postgresql://golett_user:your_password@localhost:5432/golett_db
QDRANT_URL=http://localhost:6333

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Memory Configuration
POSTGRES_BASE_TABLE=golett_memories
QDRANT_BASE_COLLECTION=golett_vectors
EMBEDDING_MODEL=text-embedding-3-small

# Layer Configuration
ENABLE_NORMALIZED_LAYERS=true
LONG_TERM_RETENTION_DAYS=365
SHORT_TERM_RETENTION_DAYS=30
IN_SESSION_RETENTION_DAYS=1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 5. Initialize Database

```bash
# Run database migrations
python scripts/init_database.py

# Verify setup
python scripts/verify_setup.py
```

### 6. Run Development Server

```bash
# Start the application
python examples/demo_crew_chat.py

# Or run specific demos
python examples/golett_native_knowledge_demo.py
python examples/normalized_memory_layers_demo.py
```

---

## Docker Deployment

### 1. Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  golett-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_CONNECTION=postgresql://golett:password@postgres:5432/golett
      - QDRANT_URL=http://qdrant:6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - qdrant
      - redis
    volumes:
      - ./knowledge:/app/knowledge
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=golett
      - POSTGRES_USER=golett
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:v1.7.4
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - golett-api
    restart: unless-stopped

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

### 2. Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 golett && chown -R golett:golett /app
USER golett

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "golett.api.server"]
```

### 3. Build and Deploy

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f golett-api

# Scale services
docker-compose up -d --scale golett-api=3

# Stop services
docker-compose down
```

### 4. Docker Health Checks

```bash
# Check service health
docker-compose ps

# Check individual container health
docker inspect --format='{{.State.Health.Status}}' golett-gateway_golett-api_1

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' golett-gateway_golett-api_1
```

---

## Kubernetes Deployment

### 1. Namespace and ConfigMap

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: golett

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: golett-config
  namespace: golett
data:
  POSTGRES_BASE_TABLE: "golett_memories"
  QDRANT_BASE_COLLECTION: "golett_vectors"
  EMBEDDING_MODEL: "text-embedding-3-small"
  ENABLE_NORMALIZED_LAYERS: "true"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
```

### 2. Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: golett-secrets
  namespace: golett
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-key>
  POSTGRES_PASSWORD: <base64-encoded-password>
```

### 3. PostgreSQL Deployment

```yaml
# postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: golett
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: golett
        - name: POSTGRES_USER
          value: golett
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: golett-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: golett
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: golett
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### 4. Qdrant Deployment

```yaml
# qdrant.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: golett
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:v1.7.4
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: qdrant
  namespace: golett
spec:
  selector:
    app: qdrant
  ports:
  - port: 6333
    targetPort: 6333

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-pvc
  namespace: golett
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

### 5. Golett API Deployment

```yaml
# golett-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: golett-api
  namespace: golett
spec:
  replicas: 3
  selector:
    matchLabels:
      app: golett-api
  template:
    metadata:
      labels:
        app: golett-api
    spec:
      containers:
      - name: golett-api
        image: golett/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_CONNECTION
          value: "postgresql://golett:$(POSTGRES_PASSWORD)@postgres:5432/golett"
        - name: QDRANT_URL
          value: "http://qdrant:6333"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: golett-secrets
              key: OPENAI_API_KEY
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: golett-secrets
              key: POSTGRES_PASSWORD
        envFrom:
        - configMapRef:
            name: golett-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"

---
apiVersion: v1
kind: Service
metadata:
  name: golett-api
  namespace: golett
spec:
  selector:
    app: golett-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### 6. Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: golett-ingress
  namespace: golett
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.golett.ai
    secretName: golett-tls
  rules:
  - host: api.golett.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: golett-api
            port:
              number: 80
```

### 7. Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: golett-api-hpa
  namespace: golett
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: golett-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 8. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgres.yaml
kubectl apply -f qdrant.yaml
kubectl apply -f golett-api.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# Check deployment status
kubectl get pods -n golett
kubectl get services -n golett
kubectl get ingress -n golett

# View logs
kubectl logs -f deployment/golett-api -n golett

# Scale deployment
kubectl scale deployment golett-api --replicas=5 -n golett
```

---

## Cloud Deployment

### AWS Deployment

#### 1. EKS Cluster Setup

```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create EKS cluster
eksctl create cluster \
  --name golett-cluster \
  --region us-west-2 \
  --nodegroup-name golett-nodes \
  --node-type m5.large \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10 \
  --managed
```

#### 2. RDS PostgreSQL Setup

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier golett-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username golett \
  --master-user-password your-secure-password \
  --allocated-storage 100 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name golett-subnet-group \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted
```

#### 3. ElastiCache Redis Setup

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id golett-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-group-name golett-cache-subnet-group
```

### Google Cloud Platform

#### 1. GKE Cluster Setup

```bash
# Create GKE cluster
gcloud container clusters create golett-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade
```

#### 2. Cloud SQL PostgreSQL

```bash
# Create Cloud SQL instance
gcloud sql instances create golett-postgres \
  --database-version POSTGRES_15 \
  --tier db-n1-standard-2 \
  --region us-central1 \
  --storage-size 100GB \
  --storage-type SSD \
  --backup-start-time 03:00 \
  --enable-bin-log \
  --maintenance-window-day SUN \
  --maintenance-window-hour 04
```

### Azure Deployment

#### 1. AKS Cluster Setup

```bash
# Create resource group
az group create --name golett-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group golett-rg \
  --name golett-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10 \
  --generate-ssh-keys
```

#### 2. Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group golett-rg \
  --name golett-postgres \
  --location eastus \
  --admin-user golett \
  --admin-password your-secure-password \
  --sku-name GP_Gen5_2 \
  --storage-size 102400 \
  --version 15
```

---

## Configuration Management

### Environment Variables

```bash
# Core Configuration
POSTGRES_CONNECTION=postgresql://user:pass@host:port/db
QDRANT_URL=http://host:port
OPENAI_API_KEY=your_api_key

# Memory Configuration
POSTGRES_BASE_TABLE=golett_memories
QDRANT_BASE_COLLECTION=golett_vectors
EMBEDDING_MODEL=text-embedding-3-small
ENABLE_NORMALIZED_LAYERS=true

# Layer Retention (days)
LONG_TERM_RETENTION_DAYS=365
SHORT_TERM_RETENTION_DAYS=30
IN_SESSION_RETENTION_DAYS=1

# Performance Configuration
MAX_CONNECTIONS=100
CONNECTION_POOL_SIZE=20
QUERY_TIMEOUT=30
EMBEDDING_BATCH_SIZE=100

# Security Configuration
API_KEY_REQUIRED=true
SESSION_TIMEOUT=3600
RATE_LIMIT_PER_MINUTE=100
CORS_ORIGINS=https://yourdomain.com

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/golett/app.log
ENABLE_METRICS=true
METRICS_PORT=9090
```

### Configuration Files

#### `config/production.yaml`

```yaml
database:
  postgres:
    connection: ${POSTGRES_CONNECTION}
    pool_size: 20
    max_overflow: 30
    pool_timeout: 30
  qdrant:
    url: ${QDRANT_URL}
    timeout: 30
    retry_attempts: 3

memory:
  layers:
    long_term:
      retention_days: 365
      importance_threshold: 0.7
      cleanup_frequency: "weekly"
    short_term:
      retention_days: 30
      importance_threshold: 0.5
      cleanup_frequency: "daily"
    in_session:
      retention_days: 1
      importance_threshold: 0.3
      cleanup_frequency: "hourly"

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 300
  rate_limit:
    requests_per_minute: 100
    burst_size: 20

security:
  api_key_required: true
  session_timeout: 3600
  cors_origins:
    - "https://yourdomain.com"
  ssl:
    enabled: true
    cert_file: "/etc/ssl/certs/golett.crt"
    key_file: "/etc/ssl/private/golett.key"

logging:
  level: "INFO"
  format: "json"
  handlers:
    - type: "file"
      filename: "/var/log/golett/app.log"
      max_size: "100MB"
      backup_count: 5
    - type: "console"
      stream: "stdout"

monitoring:
  metrics:
    enabled: true
    port: 9090
    path: "/metrics"
  health_check:
    enabled: true
    path: "/health"
    timeout: 10
```

---

## Monitoring and Logging

### Prometheus Metrics

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'golett-api'
    static_configs:
      - targets: ['golett-api:9090']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'qdrant'
    static_configs:
      - targets: ['qdrant:6333']
    metrics_path: /metrics
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Golett AI Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(golett_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Memory Layer Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "golett_memory_layer_size_bytes",
            "legendFormat": "{{layer}}"
          }
        ]
      },
      {
        "title": "Knowledge Retrieval Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, golett_knowledge_retrieval_duration_seconds_bucket)",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Log Aggregation (ELK Stack)

```yaml
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "golett-api" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    mutate {
      add_field => { "service" => "golett-api" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "golett-logs-%{+YYYY.MM.dd}"
  }
}
```

---

## Security Considerations

### Network Security

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: golett-network-policy
  namespace: golett
spec:
  podSelector:
    matchLabels:
      app: golett-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: qdrant
    ports:
    - protocol: TCP
      port: 6333
```

### Security Scanning

```bash
# Container security scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image golett/api:latest

# Kubernetes security scanning
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
```

### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.golett.ai;
    
    ssl_certificate /etc/ssl/certs/golett.crt;
    ssl_certificate_key /etc/ssl/private/golett.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://golett-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Performance Tuning

### Database Optimization

```sql
-- PostgreSQL optimization
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

-- Create indexes for common queries
CREATE INDEX CONCURRENTLY idx_memories_session_timestamp 
ON golett_memories_long_term(session_id, created_at);

CREATE INDEX CONCURRENTLY idx_memories_context_type 
ON golett_memories_long_term(context_type);

CREATE INDEX CONCURRENTLY idx_memories_importance 
ON golett_memories_long_term(importance) WHERE importance > 0.7;
```

### Qdrant Optimization

```yaml
# qdrant_config.yaml
storage:
  storage_path: "/qdrant/storage"
  snapshots_path: "/qdrant/snapshots"
  
service:
  http_port: 6333
  grpc_port: 6334
  max_request_size_mb: 32
  max_workers: 4
  
cluster:
  enabled: false
  
log_level: INFO

telemetry_disabled: true
```

### Application Optimization

```python
# Performance configuration
MEMORY_POOL_SIZE = 20
EMBEDDING_BATCH_SIZE = 100
QUERY_CACHE_TTL = 300
CONNECTION_POOL_SIZE = 20
MAX_CONCURRENT_REQUESTS = 100

# Async configuration
ASYNC_WORKERS = 4
ASYNC_QUEUE_SIZE = 1000
ASYNC_TIMEOUT = 30
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check PostgreSQL connectivity
psql -h localhost -U golett -d golett_db -c "SELECT 1;"

# Check Qdrant connectivity
curl http://localhost:6333/health

# Verify environment variables
env | grep -E "(POSTGRES|QDRANT|OPENAI)"
```

#### 2. Memory Layer Issues

```python
# Debug memory layer configuration
from golett.memory import MemoryManager

memory_manager = MemoryManager(...)
stats = memory_manager.get_layer_statistics()
print(json.dumps(stats, indent=2))

# Check layer-specific collections
collections = memory_manager.qdrant_storage.list_collections()
print("Available collections:", collections)
```

#### 3. Knowledge Retrieval Issues

```python
# Debug knowledge retrieval
from golett.chat import GolettKnowledgeAdapter

adapter = GolettKnowledgeAdapter(...)
results = adapter.retrieve_knowledge("test query", limit=5)
print(f"Retrieved {len(results)} results")

# Check knowledge sources
collections = adapter.list_collections()
print("Knowledge collections:", collections)
```

### Diagnostic Commands

```bash
# Check service health
curl http://localhost:8000/health

# View application logs
docker-compose logs -f golett-api

# Check resource usage
docker stats

# Database diagnostics
docker exec -it postgres psql -U golett -d golett_db -c "
SELECT 
  schemaname,
  tablename,
  n_tup_ins as inserts,
  n_tup_upd as updates,
  n_tup_del as deletes
FROM pg_stat_user_tables 
WHERE schemaname = 'public';
"

# Qdrant diagnostics
curl http://localhost:6333/collections
```

### Performance Debugging

```bash
# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health

# Database query analysis
docker exec -it postgres psql -U golett -d golett_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"

# Memory usage analysis
docker exec -it golett-api python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
print(f'CPU usage: {psutil.cpu_percent()}%')
"
```

---

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U golett golett_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h postgres -U golett golett_db | gzip > $BACKUP_DIR/golett_backup_$DATE.sql.gz

# Qdrant backup
curl -X POST "http://localhost:6333/collections/golett_vectors_long_term/snapshots"
```

### Disaster Recovery

```bash
# PostgreSQL restore
psql -h localhost -U golett golett_db < backup_20240101_120000.sql

# Qdrant restore
curl -X PUT "http://localhost:6333/collections/golett_vectors_long_term/snapshots/upload" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @snapshot.tar
```

---

*This deployment guide provides comprehensive instructions for deploying Golett AI in various environments. For specific cloud provider configurations and advanced deployment scenarios, refer to the respective cloud provider documentation.* 