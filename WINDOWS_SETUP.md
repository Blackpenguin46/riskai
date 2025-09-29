# 🪟 Windows Setup Guide for RiskAI

## Quick Fix for Docker Issues

If you're getting "failed to read dockerfile" errors, try these solutions:

### Option 1: Use Batch Script (Easiest)
```cmd
start-riskai-dev.bat
```

### Option 2: Use Python Script
```cmd
python start-riskai-simple.py
```

### Option 3: Manual Docker Fix

1. **Check Docker Desktop is running**
   - Make sure Docker Desktop is started and running
   - You should see the Docker whale icon in your system tray

2. **Try rebuilding individually**
   ```cmd
   docker build -f Dockerfile.backend -t riskai-backend .
   docker build -f Dockerfile.frontend -t riskai-frontend .
   docker-compose up -d
   ```

3. **Alternative: Use different context**
   ```cmd
   docker-compose down
   docker system prune -f
   docker-compose up --build --force-recreate
   ```

### Option 4: Manual Installation (If Docker fails)

1. **Install Python 3.9+**
   - Download from https://python.org
   - Check "Add to PATH" during installation

2. **Install Node.js 18+**
   - Download from https://nodejs.org

3. **Setup Backend**
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main_api.py
   ```

4. **Setup Frontend** (in new terminal)
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```

### Common Windows Issues & Fixes

**Issue: "No such file or directory"**
```cmd
# Try with quotes around paths
docker build -f "Dockerfile.frontend" -t riskai-frontend .
```

**Issue: Permission denied**
```cmd
# Run as administrator or check Docker Desktop permissions
# Right-click Command Prompt -> "Run as administrator"
```

**Issue: Port already in use**
```cmd
# Kill processes on ports 3000 and 8000
netstat -ano | findstr :3000
netstat -ano | findstr :8000
# Kill the process ID shown
taskkill /PID <process_id> /F
```

## Verification

Once running, check these URLs:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Alternative: Use WSL2

If Docker continues to fail on Windows:

1. Install WSL2 (Windows Subsystem for Linux)
2. Install Docker inside WSL2
3. Run the Linux installation commands

This often resolves Windows-specific Docker issues.