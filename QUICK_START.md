# 🚀 RiskAI Quick Start Guide

## **Immediate Setup (5 Minutes)**

### **Option 1: One-Click Start (Recommended)**

```bash
# Navigate to the RiskAI directory
cd riskai

# Run the quick start script
python start_riskai.py
```

This will:
- ✅ Check all requirements
- ✅ Set up virtual environment
- ✅ Install dependencies
- ✅ Start both backend and frontend
- ✅ Open your browser automatically

### **Option 2: Docker Setup**

```bash
# Start with Docker (requires Docker installed)
docker-compose up -d

# Access the application
open http://localhost:3000
```

### **Option 3: Manual Setup**

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## **🌐 Access Points**

Once running, access these URLs:

- **🖥️ Main Application**: http://localhost:3000
- **⚙️ Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔍 Health Check**: http://localhost:8000/health

## **📱 Using RiskAI**

### **1. First Run**
- Navigate to http://localhost:3000
- The system will initialize with default settings
- No initial configuration required

### **2. Basic Assessment**
1. Click "Start Assessment" on the dashboard
2. Answer questions about your security posture
3. Get real-time scoring and recommendations
4. View detailed analytics and benchmarks

### **3. Advanced Features**
- **📊 Analytics Dashboard**: Track improvement over time
- **🏢 Industry Benchmarks**: Compare against peers
- **🔄 Trend Analysis**: Predictive insights
- **💡 Improvement Tracking**: Monitor initiatives

## **🛠️ Development & Testing**

### **Backend Only**
```bash
python start_riskai.py --backend-only
```

### **Frontend Only**
```bash
python start_riskai.py --frontend-only
```

### **Without Browser**
```bash
python start_riskai.py --no-browser
```

## **🏢 Enterprise Quick Setup**

### **For IT Administrators**

1. **Download Enterprise Package**
   ```bash
   # Build standalone package
   python build_standalone.py
   
   # This creates platform-specific installers
   ```

2. **Deploy to Network**
   ```bash
   # Extract on server
   tar -xzf riskai-enterprise-2.0.0.tar.gz
   
   # Configure for network access
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **User Access**
   - Users navigate to: http://your-server:3000
   - No local installation required
   - All data stored centrally

### **For End Users**

1. **Desktop Installation**
   - Download appropriate installer for your OS
   - Extract and run launcher script
   - Application opens in browser automatically

2. **No Installation (Web Access)**
   - Navigate to company RiskAI server
   - Login with corporate credentials
   - Start using immediately

## **🔐 Security & Data**

### **Data Storage**
- All data stored locally in `backend/database_data/`
- No cloud dependencies required
- Full data control and privacy

### **Network Security**
- Only local ports used (3000, 8000)
- No external API calls required
- Enterprise-ready security model

## **🚨 Troubleshooting**

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :3000
   lsof -i :8000
   
   # Kill processes if needed
   kill -9 <PID>
   ```

2. **Python Version**
   ```bash
   # Check Python version (needs 3.9+)
   python --version
   
   # Use specific Python version
   python3.9 start_riskai.py
   ```

3. **Node.js Issues**
   ```bash
   # Check Node.js version (needs 18+)
   node --version
   
   # Clear npm cache
   npm cache clean --force
   ```

4. **Permission Errors**
   ```bash
   # Make script executable
   chmod +x start_riskai.py
   
   # Run with proper permissions
   sudo python start_riskai.py
   ```

### **Reset Everything**
```bash
# Clean all data and start fresh
rm -rf backend/venv
rm -rf backend/database_data
rm -rf frontend/node_modules
rm -rf frontend/.next

# Restart
python start_riskai.py
```

## **📞 Support**

### **Self-Service**
- **Logs**: Check `backend/logs/` for error details
- **Health Check**: Visit http://localhost:8000/health
- **API Status**: Visit http://localhost:8000/docs

### **Documentation**
- **Full Guide**: `DEPLOYMENT_GUIDE.md`
- **API Reference**: http://localhost:8000/docs (when running)
- **Database Schema**: `backend/database/models.py`

### **Community**
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share experiences and get help
- **Wiki**: Community-maintained documentation

## **🎯 Next Steps**

1. **Complete First Assessment** (10 minutes)
2. **Explore Analytics Dashboard** (5 minutes)
3. **Set Up Improvement Tracking** (10 minutes)
4. **Configure Industry Benchmarks** (5 minutes)
5. **Schedule Regular Assessments** (ongoing)

## **💡 Pro Tips**

- **Save Progress**: Sessions automatically save, resume anytime
- **Export Data**: Use API endpoints for data export
- **Customize**: Modify scoring criteria for your industry
- **Scale**: Use Docker for multi-user environments
- **Monitor**: Set up health checks for production use

---

**🎉 You're ready to start using RiskAI!**

The system will guide you through the rest. Begin with a simple assessment to see how it works, then explore the advanced features as needed.