# RiskAI Deployment Guide

## 🚀 **Quick Start (Development)**

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- Docker & Docker Compose

### 1. **Docker Development Setup** (Recommended)

```bash
# Clone and navigate to project
git clone <repository-url>
cd riskai

# Start with Docker Compose
docker-compose up -d

# Access the application
Frontend: http://localhost:3000
Backend API: http://localhost:8000
```

### 2. **Manual Development Setup**

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## 🏢 **Enterprise Distribution Options**

### **Option 1: Standalone Executable (Recommended for Non-Technical Users)**

```bash
# Install build dependencies
python build_standalone.py --install-deps

# Build standalone package
python build_standalone.py

# This creates:
# - Windows: riskai-2.0.0-windows-x64.zip
# - Linux: riskai-2.0.0-linux-x64.tar.gz
# - macOS: riskai-2.0.0-darwin-x64.tar.gz
```

**Distribution Contents:**
- `RiskAI.bat` (Windows) or `riskai.sh` (Linux/macOS) - Main launcher
- `backend/` - Compiled backend executable
- `frontend/` - Built React application
- `README.md` - Installation and usage instructions
- `data/` - Local data storage directory

**End-User Installation:**
1. Extract the archive to desired location
2. Double-click launcher script
3. Application opens in browser automatically

### **Option 2: Docker Enterprise Deployment**

```bash
# Production Docker setup
docker-compose -f docker-compose.prod.yml up -d

# Scale for enterprise
docker-compose -f docker-compose.prod.yml up --scale backend=3 -d
```

**Docker Compose Production:**
```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/riskai
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=riskai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

### **Option 3: Kubernetes Deployment**

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: riskai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: riskai-backend
  template:
    metadata:
      labels:
        app: riskai-backend
    spec:
      containers:
      - name: backend
        image: riskai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: riskai-secrets
              key: database-url
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
---
apiVersion: v1
kind: Service
metadata:
  name: riskai-backend-service
spec:
  selector:
    app: riskai-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## 🏭 **Enterprise Architecture Patterns**

### **1. Single-Tenant Deployment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   Frontend      │────│   Backend       │
│   (Nginx/HAProxy)│    │   (React SPA)   │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   Database      │
                                              │   (PostgreSQL)  │
                                              └─────────────────┘
```

### **2. Multi-Tenant SaaS Deployment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│   Frontend      │────│   Backend       │
│   (Kong/Traefik)│    │   (Multi-tenant)│    │   (Multi-tenant)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   Database      │
                                              │   (Per-tenant)  │
                                              └─────────────────┘
```

## 📋 **Enterprise Installation Guide**

### **For IT Administrators**

#### **Pre-Installation Checklist**

```bash
# System Requirements Check
python --version    # 3.9+
node --version     # 18+
docker --version   # 20.10+

# Network Requirements
# Ports: 3000 (frontend), 8000 (backend)
# Optional: 5432 (PostgreSQL), 6379 (Redis)

# Storage Requirements
# Minimum: 2GB free space
# Recommended: 10GB+ for enterprise data
```

#### **Installation Steps**

1. **Download Distribution Package**
   ```bash
   # Download from releases page
   wget https://releases.riskai.com/v2.0.0/riskai-enterprise-2.0.0.tar.gz
   
   # Extract
   tar -xzf riskai-enterprise-2.0.0.tar.gz
   cd riskai-enterprise-2.0.0
   ```

2. **Configuration**
   ```bash
   # Copy configuration template
   cp config.example.yaml config.yaml
   
   # Edit configuration
   nano config.yaml
   ```

3. **Database Setup**
   ```bash
   # PostgreSQL (recommended for enterprise)
   docker run -d \
     --name riskai-postgres \
     -e POSTGRES_DB=riskai \
     -e POSTGRES_USER=riskai \
     -e POSTGRES_PASSWORD=secure_password \
     -p 5432:5432 \
     postgres:15
   
   # Initialize database
   python manage.py migrate
   ```

4. **Start Services**
   ```bash
   # Production deployment
   docker-compose -f docker-compose.prod.yml up -d
   
   # Verify services
   docker-compose ps
   curl http://localhost:8000/health
   ```

### **For End Users**

#### **Desktop Installation (Windows)**
1. Download `RiskAI-Windows-Installer.zip`
2. Extract to `C:\RiskAI\`
3. Double-click `RiskAI.bat`
4. Application opens in browser

#### **Desktop Installation (macOS/Linux)**
1. Download `RiskAI-Unix-Installer.tar.gz`
2. Extract to `~/RiskAI/`
3. Run `./riskai.sh`
4. Application opens in browser

## 🔐 **Enterprise Security Configuration**

### **Authentication Setup**

```python
# config.yaml
authentication:
  method: "sso"  # sso, ldap, oauth
  sso_provider: "azure"  # azure, google, okta
  ldap_server: "ldap://company.com"
  oauth_client_id: "your-client-id"
  
security:
  ssl_enabled: true
  ssl_cert_path: "/path/to/cert.pem"
  ssl_key_path: "/path/to/key.pem"
  session_timeout: 28800  # 8 hours
```

### **Role-Based Access Control**

```yaml
# rbac.yaml
roles:
  admin:
    permissions:
      - read_all_assessments
      - manage_companies
      - view_analytics
      - manage_users
      
  analyst:
    permissions:
      - read_assessments
      - create_assessments
      - view_analytics
      
  viewer:
    permissions:
      - read_assessments
      - view_reports
```

## 📊 **Monitoring & Maintenance**

### **Health Check Endpoints**

```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/database

# Dependencies health
curl http://localhost:8000/health/dependencies
```

### **Logging Configuration**

```python
# logging.yaml
version: 1
handlers:
  file:
    class: logging.FileHandler
    filename: /app/logs/riskai.log
    formatter: json
    level: INFO
    
  syslog:
    class: logging.handlers.SysLogHandler
    address: ['syslog-server', 514]
    facility: local0
    
loggers:
  riskai:
    level: INFO
    handlers: [file, syslog]
```

### **Backup Strategy**

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/riskai"

# Database backup
pg_dump riskai > "$BACKUP_DIR/db_$DATE.sql"

# Data directory backup
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /app/data/

# Upload to cloud storage
aws s3 cp "$BACKUP_DIR/" s3://riskai-backups/ --recursive
```

## 🚀 **Performance Optimization**

### **Production Tuning**

```python
# production.yaml
performance:
  worker_processes: 4
  worker_connections: 1000
  max_request_size: 100MB
  timeout: 30
  
caching:
  enabled: true
  backend: redis
  timeout: 3600
  
database:
  pool_size: 20
  max_overflow: 0
  pool_timeout: 30
```

### **Scaling Guidelines**

| Users | Backend Instances | Database | RAM | Storage |
|-------|------------------|----------|-----|---------|
| 1-50  | 1                | SQLite   | 4GB | 10GB    |
| 51-200| 2                | PostgreSQL| 8GB | 50GB    |
| 201-500| 3               | PostgreSQL| 16GB| 100GB   |
| 500+  | 4+               | PostgreSQL| 32GB| 200GB+  |

## 📞 **Support & Maintenance**

### **Enterprise Support Channels**

- **Technical Support**: support@riskai.com
- **Documentation**: https://docs.riskai.com
- **Status Page**: https://status.riskai.com
- **Community Forum**: https://community.riskai.com

### **Maintenance Windows**

- **Updates**: Monthly, first Saturday 2-4 AM UTC
- **Patches**: As needed, during business hours
- **Emergency**: 24/7 on-call support available

### **SLA Commitments**

- **Uptime**: 99.9%
- **Response Time**: < 2 hours for critical issues
- **Resolution Time**: < 24 hours for critical issues
- **Data Backup**: Daily with 30-day retention

## 🔄 **Update Process**

### **Automated Updates**

```bash
# Check for updates
python manage.py check-updates

# Download and apply updates
python manage.py update --version=2.1.0

# Rollback if needed
python manage.py rollback --version=2.0.0
```

### **Manual Updates**

1. **Backup current installation**
2. **Download new version**
3. **Stop services**
4. **Update files**
5. **Migrate database**
6. **Start services**
7. **Verify functionality**

This comprehensive deployment guide covers all aspects of running RiskAI in enterprise environments, from simple desktop installations to complex multi-tenant cloud deployments.