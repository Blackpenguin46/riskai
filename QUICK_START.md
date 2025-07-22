# 🚀 RiskAI Enhanced Platform - Quick Start

## One-Command Deployment (Recommended)

### Prerequisites
- Docker Desktop installed ([Download here](https://docs.docker.com/get-docker/))
- 4GB RAM available
- Ports 3000 and 8000 free

### Start Platform

**Linux/Mac:**
```bash
./start-riskai.sh
```

**Windows:**
```bash
start-riskai.bat
```

**Manual Docker Compose:**
```bash
docker-compose up --build -d
```

### Access Research Demo
- **Research Demo**: http://localhost:3000/research-demo
- **Main Platform**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Stop Platform
```bash
docker-compose down
```

## 🎯 Research Demo Components

### 1. Mathematical Scoring
- Transparent formulas with step-by-step calculations
- Statistical confidence intervals
- Interactive score visualizations
- Real-time updates

### 2. AI Bias Detection
- Multi-dimensional bias analysis (7 categories)
- Fairness metrics (demographic parity, equalized odds)
- Mitigation strategies
- Continuous monitoring

### 3. Framework Source Attribution
- Links to 8+ authoritative frameworks
- Confidence scoring for attributions
- Intelligent pattern matching
- Validation systems

### 4. Real-time Analysis
- Live scoring updates
- Projected outcomes
- Progress tracking
- Quality metrics

## 🐛 Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Docker not running**: Start Docker Desktop
3. **Build failures**: Run `docker system prune -a` and retry
4. **Memory issues**: Increase Docker memory allocation

### Check Status
```bash
# View logs
docker-compose logs -f

# Check containers
docker-compose ps

# Restart services
docker-compose restart
```

## 📊 Demo Script (2 minutes)

1. Open: http://localhost:3000/research-demo
2. **Mathematical Scoring**: Show transparent formulas and confidence intervals
3. **AI Feedback**: Demonstrate framework attribution and bias analysis
4. **Real-time**: Show live scoring updates and projections
5. **Highlight**: Research contributions and validation metrics

## 🎓 Research Paper Ready!

The platform demonstrates:
- ✅ Novel mathematical framework with transparency
- ✅ Comprehensive bias detection across 7 dimensions
- ✅ Automated source attribution to authoritative frameworks
- ✅ Industry-specific adaptations for emerging technologies
- ✅ Real-time analysis with confidence quantification

**Perfect for academic evaluation and research demonstration!**