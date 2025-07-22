# 🛡️ RiskAI - Professional Cybersecurity Risk Assessment Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15.3+-black.svg)](https://nextjs.org/)

## 🎯 Overview

RiskAI is a comprehensive, AI-powered cybersecurity risk assessment platform designed for real business use. The platform provides organizations with professional-grade security evaluations, personalized recommendations, and detailed compliance reporting across 12 critical security domains.

### 🌟 Key Features

- **📊 Comprehensive Assessment**: 120+ questions across 12 security domains
- **🤖 AI-Powered Recommendations**: Personalized insights with framework attribution
- **📈 Real-time Scoring**: Live mathematical calculations with confidence intervals
- **📋 Professional Reporting**: Executive dashboards and detailed compliance reports
- **🏢 Industry-Specific**: Tailored assessments for healthcare, finance, and technology sectors
- **⚖️ Bias Detection**: Multi-dimensional fairness analysis and mitigation
- **📚 Framework Integration**: NIST CSF, ISO 27001, CIS Controls, and more

## 🚀 Quick Start (One-Command Deployment)

### Prerequisites
- **Docker Desktop** ([Download here](https://docs.docker.com/get-docker/))
- **4GB RAM** available
- **Ports 3000 and 8000** available

### 🐳 Start Platform (Choose Your Method)

#### Option 1: Shell Script (Recommended)
```bash
# Linux/macOS
./start-riskai-dev.sh

# Windows
start-riskai-dev.bat
```

#### Option 2: Python Script (Cross-platform)
```bash
python start-riskai-simple.py
```

#### Option 3: Docker Compose (Manual)
```bash
docker-compose up --build -d
```

### 🌐 Access Your Platform

Once started, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:3000 | Complete assessment interface |
| **Research Demo** | http://localhost:3000/research-demo | Interactive research demonstration |
| **API Documentation** | http://localhost:8000/docs | Complete API reference |
| **Health Check** | http://localhost:8000/health | System status |

### 🛑 Stop Platform
```bash
docker-compose down
```

## 📋 Assessment Domains

RiskAI evaluates organizations across 12 critical security domains:

| Domain | Weight | Questions | Focus Area |
|--------|--------|-----------|------------|
| **Governance & Risk Management** | 20% | 10 | Strategic foundation and policy framework |
| **Data Protection** | 12% | 10 | Privacy controls and data security |
| **Access Control** | 12% | 10 | Identity and authorization management |
| **Security Monitoring** | 10% | 10 | Detection and response capabilities |
| **Incident Response** | 10% | 10 | Crisis management and recovery |
| **Asset Management** | 8% | 10 | Technical visibility and inventory |
| **Business Continuity** | 8% | 10 | Operational resilience |
| **Security Awareness** | 6% | 10 | Human factor considerations |
| **Compliance** | 4% | 10 | Regulatory alignment |
| **Emerging Technologies** | 4% | 10 | AI, IoT, cloud risk management |
| **Third Party Risk** | 4% | 10 | Supply chain security |
| **Risk Management Process** | 2% | 10 | Continuous improvement |

## 🏗️ Architecture

### Backend Components
```
backend/
├── main_api.py                          # Unified API endpoint
├── assessment/
│   ├── assessment_api.py                # Core assessment engine
│   ├── scoring_api.py                   # Mathematical scoring system
│   ├── question_api.py                  # Question bank management
│   ├── comprehensive_feedback_api.py    # AI recommendation engine
│   ├── source_attribution_api.py        # Framework attribution
│   ├── bias_detection_api.py            # Fairness analysis
│   └── dashboard_api.py                 # Analytics dashboard
├── scoring/
│   └── scoring_engine.py                # Core mathematical formulas
└── database/
    └── models.py                        # Data persistence layer
```

### Frontend Components
```
frontend/
├── pages/
│   ├── index.tsx                        # Main dashboard
│   ├── assessment-simple.tsx            # Assessment interface
│   ├── research-demo.tsx                # Research demonstration
│   ├── reports.tsx                      # Reporting dashboard
│   └── scoring.tsx                      # Scoring visualization
├── components/
│   ├── ScoringVisualization.tsx         # Interactive score displays
│   ├── FeedbackVisualization.tsx        # AI recommendation interface
│   └── RealTimeScoringDisplay.tsx       # Live scoring updates
└── lib/
    ├── assessment-api.ts                # Assessment API client
    ├── dashboard-api.ts                 # Dashboard API client
    └── validation-api.ts                # Validation utilities
```

## 🔬 Research & Academic Features

### Mathematical Scoring Transparency
- **Defined Formulas**: `Section Score = Σ(Question Score × Weight) / Σ(Weights) × 100`
- **Confidence Intervals**: `CI = Score ± (1 - Completion Rate) × 10%`
- **Weighted Scoring**: `Overall = Σ(Section Score × Domain Weight)`
- **Statistical Analysis**: Real-time confidence and margin of error calculations

### AI Bias Detection & Mitigation
- **Multi-dimensional Analysis**: 7 bias categories with severity classification
- **Fairness Metrics**: Demographic parity, equalized odds, calibration
- **Mitigation Strategies**: Specific recommendations for bias reduction
- **Continuous Monitoring**: Ongoing bias tracking and alerting

### Framework Source Attribution
- **Authoritative Linking**: NIST CSF, ISO 27001, CIS Controls, COBIT
- **Confidence Scoring**: Reliability assessment for each attribution
- **Intelligent Matching**: Pattern recognition for framework alignment
- **Validation System**: Quality checks for attribution accuracy

## 📊 Key API Endpoints

### Assessment APIs
```bash
# Start new assessment
POST /api/assessment/start

# Get assessment questions
GET /api/assessment/questions/{section}

# Submit responses
POST /api/assessment/responses

# Get real-time scores
GET /api/scoring/realtime/{assessment_id}
```

### Analytics APIs
```bash
# Dashboard data
GET /api/dashboard/data

# Comprehensive feedback
POST /api/feedback/comprehensive

# Bias analysis
POST /api/bias/analyze

# Framework attribution
POST /api/attribution/analyze
```

### Reporting APIs
```bash
# Generate reports
GET /api/reports/{assessment_id}

# Export functionality
GET /api/reports/{assessment_id}/export/{format}
```

## 🛠️ Development Setup

### Local Development (Without Docker)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main_api.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `.env` files as needed:

**Backend (.env)**
```env
ENVIRONMENT=development
PYTHONPATH=/app
DATABASE_URL=sqlite:///./riskai.db
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## 📈 Performance & Scalability

### System Requirements
- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 4GB RAM, 4 CPU cores
- **Storage**: 1GB available space

### Performance Metrics
- **Assessment Completion**: <5 minutes average
- **Real-time Scoring**: <100ms response time
- **Report Generation**: <30 seconds for comprehensive reports
- **Concurrent Users**: Supports 50+ simultaneous assessments

## 🔒 Security & Compliance

### Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **Privacy**: GDPR and CCPA compliant data handling
- **Authentication**: Secure user authentication and authorization
- **Audit Logging**: Comprehensive activity tracking

### Compliance Frameworks
- **NIST Cybersecurity Framework 2.0**
- **ISO/IEC 27001:2022**
- **CIS Controls v8**
- **COBIT 2019**
- **GDPR, HIPAA, PCI DSS** (industry-specific)

## 🧪 Testing & Quality Assurance

### Automated Testing
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Quality Metrics
- **Code Coverage**: >85% test coverage
- **Performance**: <2s page load times
- **Accessibility**: WCAG 2.1 AA compliant
- **Security**: Regular vulnerability scanning

## 📚 Documentation

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Postman Collection**: Available in `/docs` folder

### User Guides
- **Assessment Guide**: Complete walkthrough of the assessment process
- **Reporting Guide**: How to interpret and use assessment reports
- **Admin Guide**: Platform configuration and management

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Docker Issues**
```bash
# Reset Docker environment
docker-compose down -v
docker system prune -f
docker-compose up --build -d
```

**Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
```

**Memory Issues**
- Ensure Docker has at least 4GB RAM allocated
- Close other applications to free memory


---



---


*Empowering organizations to build stronger security postures through intelligent risk assessment.*
