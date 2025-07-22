# 🚀 RiskAI Production Deployment Guide

This guide covers deploying RiskAI in production environments with security, scalability, and reliability considerations.

## 📋 Table of Contents

1. [Production Architecture](#production-architecture)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Security Configuration](#security-configuration)
4. [Database Setup](#database-setup)
5. [Load Balancing](#load-balancing)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [CI/CD Pipeline](#cicd-pipeline)

## 🏗️ Production Architecture

### Recommended Architecture
```
Internet
    ↓
Load Balancer (nginx/AWS ALB)
    ↓
Frontend Servers (3+ instances)
    ↓
API Gateway/Load Balancer
    ↓
Backend Servers (3+ instances)
    ↓
Database Cluster (PostgreSQL)
    ↓
File Storage (S3/MinIO)
```

### Component Specifications

#### Frontend Tier
- **Technology**: Next.js with static generation
- **Instances**: 3+ for high availability
- **Resources**: 2 CPU, 4GB RAM per instance
- **CDN**: CloudFront/CloudFlare for static assets

#### Backend Tier
- **Technology**: FastAPI with Gunicorn
- **Instances**: 3+ for high availability
- **Resources**: 4 CPU, 8GB RAM per instance
- **Auto-scaling**: Based on CPU/memory usage

#### Database Tier
- **Primary**: PostgreSQL 14+ with read replicas
- **Resources**: 8 CPU, 32GB RAM, SSD storage
- **Backup**: Automated daily backups with point-in-time recovery

## 🖥️ Infrastructure Requirements

### Minimum Production Setup
- **CPU**: 16 cores total
- **RAM**: 64GB total
- **Storage**: 500GB SSD
- **Network**: 1Gbps bandwidth
- **Availability**: 99.9% uptime SLA

### Recommended Production Setup
- **CPU**: 32+ cores total
- **RAM**: 128GB+ total
- **Storage**: 1TB+ SSD with RAID
- **Network**: 10Gbps bandwidth
- **Availability**: 99.99% uptime SLA

### Cloud Provider Recommendations

#### AWS
```yaml
# Frontend: EC2 t3.medium (2 vCPU, 4GB RAM)
# Backend: EC2 c5.xlarge (4 vCPU, 8GB RAM)
# Database: RDS db.r5.2xlarge (8 vCPU, 64GB RAM)
# Load Balancer: Application Load Balancer
# CDN: CloudFront
# Storage: S3
```

#### Google Cloud Platform
```yaml
# Frontend: e2-standard-2 (2 vCPU, 8GB RAM)
# Backend: c2-standard-4 (4 vCPU, 16GB RAM)
# Database: Cloud SQL db-standard-8 (8 vCPU, 30GB RAM)
# Load Balancer: Cloud Load Balancing
# CDN: Cloud CDN
# Storage: Cloud Storage
```

#### Azure
```yaml
# Frontend: Standard_B2s (2 vCPU, 4GB RAM)
# Backend: Standard_F4s_v2 (4 vCPU, 8GB RAM)
# Database: Standard_D8s_v3 (8 vCPU, 32GB RAM)
# Load Balancer: Application Gateway
# CDN: Azure CDN
# Storage: Blob Storage
```

## 🔒 Security Configuration

### SSL/TLS Configuration

#### nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    location / {
        proxy_pass http://frontend-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Variables (Production)
```bash
# Backend
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@db-cluster:5432/riskai
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-domain.com
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn

# Frontend
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirect to HTTPS)
ufw allow 443/tcp   # HTTPS
ufw deny 3000/tcp   # Block direct frontend access
ufw deny 8000/tcp   # Block direct backend access
ufw enable
```

## 🗄️ Database Setup

### PostgreSQL Production Configuration

#### Installation
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-14 postgresql-contrib

# Configure PostgreSQL
sudo -u postgres createuser --interactive riskai
sudo -u postgres createdb riskai_production
```

#### Configuration (postgresql.conf)
```ini
# Memory settings
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 256MB
maintenance_work_mem = 2GB

# Connection settings
max_connections = 200
listen_addresses = '*'

# Performance settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Logging
log_statement = 'mod'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

#### Backup Configuration
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="riskai_production"

# Create backup
pg_dump -h localhost -U riskai -d $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/postgresql/
```

### Database Migration
```bash
# Create migration script
cat > migrate_to_production.py << EOF
import os
import psycopg2
from sqlalchemy import create_engine

# Source (SQLite) and target (PostgreSQL) connections
sqlite_url = "sqlite:///./riskai.db"
postgres_url = os.getenv("DATABASE_URL")

# Migration logic here
# (Implementation depends on your specific schema)
EOF

python migrate_to_production.py
```

## ⚖️ Load Balancing

### nginx Load Balancer Configuration
```nginx
upstream frontend-backend {
    least_conn;
    server frontend1:3000 max_fails=3 fail_timeout=30s;
    server frontend2:3000 max_fails=3 fail_timeout=30s;
    server frontend3:3000 max_fails=3 fail_timeout=30s;
}

upstream api-backend {
    least_conn;
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration (see Security section)
    
    location / {
        proxy_pass http://frontend-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    location /api/ {
        proxy_pass http://api-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API-specific settings
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### Docker Compose Production
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend1
      - frontend2
      - backend1
      - backend2
    restart: unless-stopped

  frontend1:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://api.your-domain.com
      - NODE_ENV=production
    restart: unless-stopped

  frontend2:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://api.your-domain.com
      - NODE_ENV=production
    restart: unless-stopped

  backend1:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/riskai
      - ENVIRONMENT=production
    depends_on:
      - postgres
    restart: unless-stopped

  backend2:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/riskai
      - ENVIRONMENT=production
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=riskai
      - POSTGRES_USER=riskai
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

volumes:
  postgres_data:
```

## 📊 Monitoring & Logging

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'riskai-backend'
    static_configs:
      - targets: ['backend1:8000', 'backend2:8000']
    metrics_path: '/metrics'

  - job_name: 'riskai-frontend'
    static_configs:
      - targets: ['frontend1:3000', 'frontend2:3000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "RiskAI Production Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(active_sessions)"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      }
    ]
  }
}
```

### Application Logging
```python
# backend/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### Log Aggregation (ELK Stack)
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

## 💾 Backup & Recovery

### Automated Backup Strategy
```bash
#!/bin/bash
# backup.sh - Comprehensive backup script

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h postgres -U riskai riskai_production | gzip > $BACKUP_DIR/database.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/application.tar.gz /app/uploads /app/config

# Upload to cloud storage
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/$(date +%Y%m%d)/

# Cleanup old backups (keep 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### Disaster Recovery Plan
```bash
#!/bin/bash
# disaster_recovery.sh - Recovery procedures

# 1. Restore database
gunzip -c database.sql.gz | psql -h postgres -U riskai riskai_production

# 2. Restore application files
tar -xzf application.tar.gz -C /

# 3. Restart services
docker-compose restart

# 4. Verify system health
curl -f http://localhost:8000/health
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/
          
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Build frontend
        run: |
          cd frontend
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          # Build and push Docker images
          docker build -t riskai-backend:latest -f Dockerfile.backend .
          docker build -t riskai-frontend:latest -f Dockerfile.frontend .
          
          # Push to registry
          docker tag riskai-backend:latest ${{ secrets.DOCKER_REGISTRY }}/riskai-backend:latest
          docker tag riskai-frontend:latest ${{ secrets.DOCKER_REGISTRY }}/riskai-frontend:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/riskai-backend:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/riskai-frontend:latest
          
          # Deploy to production servers
          ssh ${{ secrets.PRODUCTION_SERVER }} "
            docker-compose pull
            docker-compose up -d --no-deps backend frontend
          "
```

### Blue-Green Deployment
```bash
#!/bin/bash
# blue_green_deploy.sh

CURRENT_ENV=$(docker-compose ps | grep "Up" | head -1 | awk '{print $1}' | cut -d'_' -1)

if [ "$CURRENT_ENV" = "blue" ]; then
    NEW_ENV="green"
else
    NEW_ENV="blue"
fi

echo "Deploying to $NEW_ENV environment..."

# Start new environment
docker-compose -f docker-compose.$NEW_ENV.yml up -d

# Health check
sleep 30
if curl -f http://localhost:8080/health; then
    echo "Health check passed. Switching traffic..."
    
    # Update load balancer to point to new environment
    # (Implementation depends on your load balancer)
    
    # Stop old environment
    docker-compose -f docker-compose.$CURRENT_ENV.yml down
    
    echo "Deployment successful!"
else
    echo "Health check failed. Rolling back..."
    docker-compose -f docker-compose.$NEW_ENV.yml down
    exit 1
fi
```

## 📈 Performance Optimization

### Backend Optimization
```python
# backend/main_api.py - Production optimizations
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Adjust based on CPU cores
        access_log=False,  # Disable for performance
        server_header=False,  # Security
    )
```

### Frontend Optimization
```javascript
// next.config.js - Production optimizations
module.exports = {
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  
  // Image optimization
  images: {
    domains: ['your-domain.com'],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Bundle analysis
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback.fs = false;
    }
    return config;
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          }
        ]
      }
    ];
  }
};
```

## 🎯 Production Checklist

### Pre-Deployment
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL certificates installed
- [ ] Environment variables configured
- [ ] Database optimized
- [ ] Load balancer configured

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Backup verification completed
- [ ] Performance metrics baseline established
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team training completed

### Ongoing Maintenance
- [ ] Regular security updates
- [ ] Performance monitoring
- [ ] Backup verification
- [ ] Capacity planning
- [ ] Incident response procedures
- [ ] Regular disaster recovery testing

---

**Production deployment requires careful planning and testing. Always test in a staging environment first!**

*For additional support with production deployments, consult with your DevOps team or cloud provider.*