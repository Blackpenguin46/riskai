# RiskAI Enterprise Quick Start Guide

## 🚀 One-Command Startup

Get RiskAI running with frontend and backend in **one command**:

### Option 1: Shell Script (Recommended)
```bash
# Linux/Mac
./start-riskai-dev.sh

# Windows  
start-riskai-dev.bat
```

### Option 2: Python Script (Cross-platform)
```bash
python start-riskai-simple.py
```

### What This Does:
✅ Starts backend API server (port 8000)  
✅ Starts frontend web interface (port 3000)  
✅ Initializes RAG pipeline with AI knowledge base  
✅ Loads dynamic scoring engine with industry benchmarks  
✅ Health checks both services  
✅ Shows you all the important URLs  

## 📊 Access Points After Startup

| Service | URL | Description |
|---------|-----|-------------|
| **Web Interface** | http://localhost:3000 | Main dashboard with Assessment + Demo Data tabs |
| **Real Assessment** | http://localhost:3000/real-assessment | Complete enterprise assessment interface |
| **Backend API** | http://localhost:8000 | REST API for assessments |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Service status monitoring |

## 🏢 Enterprise Assessment Flow

### 1. Get Assessment Questions
```bash
curl http://localhost:8000/api/assessment/enterprise/questions
```

### 2. Submit Assessment (Example)
```bash
curl -X POST http://localhost:8000/api/assessment/enterprise/submit \
  -H "Content-Type: application/json" \
  -d '{
    "company_profile": {
      "name": "Acme Corp",
      "industry": "healthcare", 
      "size": "medium",
      "compliance_requirements": ["HIPAA"]
    },
    "answers": [
      {"question_id": "gov_001", "answer": "basic", "section_id": "governance"},
      {"question_id": "access_001", "answer": 75, "section_id": "access_control"}
    ]
  }'
```

### 3. View Dynamic Scoring Results
- **Overall Score**: 0-100 with industry benchmarking
- **Section Breakdown**: Governance, Access Control, Data Protection, etc.
- **Confidence Metrics**: Statistical confidence in assessment results
- **AI Recommendations**: RAG-powered suggestions from knowledge base

## 🎯 Key Features Available

### ✅ Dynamic Scoring
- Scores change based on actual answers (not static demo data)
- Industry benchmarks: Healthcare MFA 85%, Finance 94%, Tech 91%
- Company size adjustments: Small companies get governance leniency

### ✅ Question Types
- **Scale**: Rate 1-10 (e.g., "Rate your cybersecurity budget adequacy")
- **Multiple Choice**: Predefined options with scores (e.g., "How often do you test incident response?")
- **Boolean**: Yes/No questions (e.g., "Do you have a CISO?")
- **Percentage**: Quantitative metrics (e.g., "What % of users have MFA?")
- **Text**: Qualitative analysis (e.g., "Describe your risk assessment process")

### ✅ Industry Intelligence
- **Healthcare**: Stricter data protection requirements, HIPAA focus
- **Finance**: Enhanced access controls, PCI DSS compliance
- **Technology**: Innovation bonuses, advanced monitoring expectations
- **Government**: FedRAMP alignment, continuous monitoring

### ✅ AI-Powered Features
- **RAG Pipeline**: Recommendations from 100+ cybersecurity documents
- **Source Attribution**: Links to NIST CSF, ISO 27001, CIS Controls
- **Bias Detection**: Multi-dimensional fairness analysis
- **Confidence Scoring**: Statistical confidence intervals

## 🔧 Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker info

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart clean
docker-compose down
docker-compose up --build -d
```

### Port Conflicts
If ports 3000 or 8000 are in use:
```bash
# Stop other services using these ports
lsof -ti:3000 | xargs kill -9  # Mac/Linux
lsof -ti:8000 | xargs kill -9  # Mac/Linux

# Or edit docker-compose.yml to use different ports
```

### Performance Issues
- Minimum 4GB RAM required
- Allow 30-60 seconds for full startup
- RAG pipeline initialization takes extra time on first run

## 📋 Sample Assessment Scenarios

### Low Maturity Organization
```json
{
  "gov_001": "none",      // No governance = 10/100
  "access_001": 25,       // 25% MFA = 30/100  
  "data_001": 40,         // 40% encryption = 44/100
  "monitor_001": 2        // Basic monitoring = 20/100
}
```
**Result**: ~26/100 - Critical Risk

### Medium Maturity Organization  
```json
{
  "gov_001": "basic",     // Basic governance = 30/100
  "access_001": 75,       // 75% MFA = 75/100
  "data_001": 85,         // 85% encryption = 85/100  
  "monitor_001": 6        // Managed monitoring = 60/100
}
```
**Result**: ~68/100 - Medium Risk

### High Maturity Organization
```json
{
  "gov_001": "optimized", // Optimized governance = 100/100
  "access_001": 95,       // 95% MFA = 100/100
  "data_001": 98,         // 98% encryption = 100/100
  "monitor_001": 9        // Advanced monitoring = 90/100
}
```
**Result**: ~92/100 - Low Risk

## 🛡️ Ready for Enterprise Use

The platform now provides:
- **Real dynamic scoring** based on actual answers
- **Industry-specific benchmarks** with quantitative validation
- **Statistical confidence intervals** for assessment reliability
- **AI-powered recommendations** from cybersecurity knowledge base
- **Framework alignment** with NIST, ISO 27001, CIS Controls

Start your enterprise cybersecurity assessment in **one command**! 🚀