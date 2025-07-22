# 🚀 RiskAI Installation Guide

This comprehensive guide will help you install and set up RiskAI on your system. Choose the installation method that best fits your needs.

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation (Docker)](#quick-installation-docker)
3. [Manual Installation](#manual-installation)
4. [Development Setup](#development-setup)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Verification](#verification)

## 🖥️ System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB available
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

### Recommended Requirements
- **RAM**: 8GB or more
- **CPU**: 4 cores or more
- **Storage**: 5GB free space (for development)
- **Network**: Stable broadband connection

### Required Software
- **Docker Desktop** (for Docker installation)
- **Python 3.9+** (for manual installation)
- **Node.js 18+** (for manual installation)
- **Git** (for cloning repository)

## 🐳 Quick Installation (Docker) - Recommended

This is the fastest and most reliable way to get RiskAI running.

### Step 1: Install Docker Desktop

#### Windows
1. Download Docker Desktop from [docker.com](https://docs.docker.com/desktop/install/windows-install/)
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Launch Docker Desktop and complete the initial setup

#### macOS
1. Download Docker Desktop from [docker.com](https://docs.docker.com/desktop/install/mac-install/)
2. Drag Docker.app to your Applications folder
3. Launch Docker Desktop and complete the initial setup

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/Blackpenguin46/riskai.git
cd riskai
```

### Step 3: Start RiskAI

Choose one of these methods:

#### Method A: Shell Script (Linux/macOS)
```bash
chmod +x start-riskai-dev.sh
./start-riskai-dev.sh
```

#### Method B: Batch Script (Windows)
```cmd
start-riskai-dev.bat
```

#### Method C: Python Script (Cross-platform)
```bash
python start-riskai-simple.py
```

#### Method D: Docker Compose (Manual)
```bash
docker-compose up --build -d
```

### Step 4: Verify Installation
Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Manual Installation

For development or when Docker is not available.

### Step 1: Install Prerequisites

#### Python 3.9+
**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer, check "Add Python to PATH"
3. Verify: `python --version`

**macOS:**
```bash
# Using Homebrew
brew install python@3.9

# Or download from python.org
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv python3.9-dev
```

#### Node.js 18+
**Windows/macOS:**
1. Download from [nodejs.org](https://nodejs.org/)
2. Run installer and follow setup wizard
3. Verify: `node --version` and `npm --version`

**Linux:**
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 2: Clone Repository
```bash
git clone https://github.com/Blackpenguin46/riskai.git
cd riskai
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p data vectordb uploads

# Start backend server
python main_api.py
```

The backend will start on http://localhost:8000

### Step 4: Frontend Setup
Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on http://localhost:3000

### Step 5: Verify Installation
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Development Setup

For contributors and developers who want to modify RiskAI.

### Step 1: Fork and Clone
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/riskai.git
cd riskai
```

### Step 2: Set Up Development Environment

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\\Scripts\\activate  # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Install development tools
npm install -D @types/node @types/react @types/react-dom
```

### Step 3: Environment Configuration

#### Backend Environment (.env)
```bash
cd backend
cat > .env << EOF
ENVIRONMENT=development
PYTHONPATH=/app
DATABASE_URL=sqlite:///./riskai.db
LOG_LEVEL=DEBUG
EOF
```

#### Frontend Environment (.env.local)
```bash
cd frontend
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
NEXT_TELEMETRY_DISABLED=1
EOF
```

### Step 4: Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## ⚙️ Configuration

### Environment Variables

#### Backend Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Runtime environment | `production` |
| `DATABASE_URL` | Database connection string | `sqlite:///./riskai.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PYTHONPATH` | Python path | `/app` |

#### Frontend Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NODE_ENV` | Node environment | `production` |
| `NEXT_TELEMETRY_DISABLED` | Disable Next.js telemetry | `1` |

### Database Configuration

RiskAI uses SQLite by default. For production, consider PostgreSQL:

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost:5432/riskai
```

### Customization Options

#### Assessment Configuration
Edit `backend/assessment/question_bank.py` to customize:
- Question sets
- Scoring weights
- Domain definitions

#### UI Customization
Edit `frontend/styles/main.css` and Tailwind configuration:
- Color schemes
- Typography
- Layout preferences

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Docker Issues

**Issue**: "Docker daemon not running"
```bash
# Solution: Start Docker Desktop
# Windows/macOS: Launch Docker Desktop application
# Linux: sudo systemctl start docker
```

**Issue**: "Port already in use"
```bash
# Find process using port
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Kill process (replace PID)
kill -9 PID

# Or use different ports
docker-compose down
# Edit docker-compose.yml to change ports
docker-compose up -d
```

**Issue**: "Out of memory"
```bash
# Increase Docker memory allocation
# Docker Desktop > Settings > Resources > Memory > 4GB+
```

#### Python Issues

**Issue**: "Module not found"
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue**: "Permission denied"
```bash
# Linux/macOS: Fix permissions
chmod +x start-riskai-dev.sh
sudo chown -R $USER:$USER .
```

#### Node.js Issues

**Issue**: "npm install fails"
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: "Build fails"
```bash
# Check Node.js version
node --version  # Should be 18+

# Update Node.js if needed
# Use nvm (Node Version Manager) for easy switching
```

#### Network Issues

**Issue**: "Cannot connect to backend"
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check firewall settings
# Windows: Windows Defender Firewall
# macOS: System Preferences > Security & Privacy > Firewall
# Linux: sudo ufw status
```

### Performance Issues

**Slow startup:**
- Ensure sufficient RAM (4GB+)
- Close unnecessary applications
- Use SSD storage if available

**Slow assessment loading:**
- Check network connection
- Clear browser cache
- Restart services

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```bash
   # Docker logs
   docker-compose logs backend
   docker-compose logs frontend
   
   # Manual installation logs
   # Check terminal output for error messages
   ```

2. **Search existing issues:**
   - [GitHub Issues](https://github.com/Blackpenguin46/riskai/issues)

3. **Create a new issue:**
   - Include system information
   - Provide error messages
   - Describe steps to reproduce

## ✅ Verification

### Health Checks

After installation, verify everything is working:

#### 1. Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

#### 2. Frontend Access
Open http://localhost:3000 in your browser
- Should see RiskAI dashboard
- No console errors in browser developer tools

#### 3. API Documentation
Visit http://localhost:8000/docs
- Should see interactive API documentation
- All endpoints should be listed

#### 4. Assessment Flow
1. Navigate to http://localhost:3000
2. Click "Risk Assessment"
3. Complete company profile
4. Start assessment
5. Verify real-time scoring works

#### 5. Report Generation
1. Complete an assessment
2. Navigate to Reports
3. Generate and export a report
4. Verify PDF/Excel export works

### Performance Verification

#### Response Times
```bash
# Backend API response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Create curl-format.txt:
echo "time_total: %{time_total}s" > curl-format.txt
```

#### Memory Usage
```bash
# Docker container memory usage
docker stats --no-stream

# System memory usage
# Linux: free -h
# macOS: vm_stat
# Windows: Task Manager
```

### Security Verification

#### SSL/TLS (Production)
```bash
# Check SSL certificate (if using HTTPS)
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

#### Port Security
```bash
# Verify only required ports are open
nmap -p 3000,8000 localhost
```

## 🎉 Success!

If all verification steps pass, RiskAI is successfully installed and ready to use!

### Next Steps
1. **Explore the Platform**: Take a sample assessment
2. **Read the Documentation**: Check out the user guides
3. **Customize Settings**: Adjust configuration as needed
4. **Invite Users**: Share access with your team
5. **Schedule Regular Assessments**: Set up ongoing security evaluations

### Support Resources
- **Documentation**: [User Guide](USER_GUIDE.md)
- **API Reference**: http://localhost:8000/docs
- **Community**: [GitHub Discussions](https://github.com/Blackpenguin46/riskai/discussions)
- **Issues**: [GitHub Issues](https://github.com/Blackpenguin46/riskai/issues)

---

**Welcome to RiskAI! 🛡️**

*Your journey to better cybersecurity starts here.*