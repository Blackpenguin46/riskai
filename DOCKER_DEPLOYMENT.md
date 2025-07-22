# RiskAI Docker Deployment Guide

This guide provides step-by-step instructions for deploying the RiskAI application using Docker.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop on Windows and macOS)

## Quick Start

The RiskAI application can be deployed with a single command:

```bash
./start_riskai.sh
```

This script will:
1. Check for Docker and Docker Compose
2. Detect and resolve port conflicts
3. Create necessary directories
4. Build and start the containers
5. Wait for services to be ready
6. Display access URLs

## Step-by-Step Deployment

If you prefer to deploy manually or need more control over the process, follow these steps:

### 1. Prepare the Environment

Create the necessary directories for data persistence:

```bash
mkdir -p data
mkdir -p vectordb
mkdir -p backend/database_data
```

### 2. Add PDF Documents

Add your PDF documents to the `data` directory. These will be processed by the RAG system:

```bash
cp your-documents/*.pdf data/
```

### 3. Start the Services

Start the RiskAI services using Docker Compose:

```bash
docker-compose up -d
```

### 4. Check Service Status

Check if the services are running:

```bash
docker-compose ps
```

### 5. Access the Application

Once the services are running, you can access:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Port Configuration Guide

RiskAI uses two main ports for its services:

- **Frontend**: Default port 3000
- **Backend**: Default port 8000

### Default Port Configuration

By default, the services are configured to use these ports:

```yaml
# In docker-compose.yml
services:
  backend:
    ports:
      - "${BACKEND_PORT:-8000}:8000"
  
  frontend:
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
```

### Using Custom Ports

If you need to use custom ports, you have several options:

#### Option 1: Environment Variables with the Deployment Script

Set environment variables before running the script:

```bash
export FRONTEND_PORT=3001
export BACKEND_PORT=8001
./start_riskai.sh
```

#### Option 2: Environment Variables with Docker Compose

Set environment variables when using Docker Compose directly:

```bash
FRONTEND_PORT=3001 BACKEND_PORT=8001 docker-compose up -d
```

#### Option 3: Create a Docker Compose Override File

Create a `docker-compose.override.yml` file:

```yaml
version: '3'
services:
  frontend:
    ports:
      - "3001:3000"
  backend:
    ports:
      - "8001:8000"
```

Then run Docker Compose as usual:

```bash
docker-compose up -d
```

### Port Configuration Examples

#### Example 1: Standard Development Setup

```bash
# Default ports
./start_riskai.sh
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

#### Example 2: Avoiding Conflicts with Other Services

```bash
# Custom ports to avoid conflicts
FRONTEND_PORT=3001 BACKEND_PORT=8001 ./start_riskai.sh
```

- Frontend: http://localhost:3001
- Backend: http://localhost:8001

#### Example 3: Running Multiple Instances

For first instance:
```bash
FRONTEND_PORT=3000 BACKEND_PORT=8000 docker-compose -p riskai-1 up -d
```

For second instance:
```bash
FRONTEND_PORT=3001 BACKEND_PORT=8001 docker-compose -p riskai-2 up -d
```

### Verifying Port Configuration

To verify that the services are running on the expected ports:

```bash
# Check listening ports
netstat -tuln | grep -E '3000|3001|8000|8001'

# Or using lsof
lsof -i :3000
lsof -i :8000
```

### Updating Frontend Configuration

When changing the backend port, ensure the frontend is configured to use the correct backend URL:

```bash
# The script and docker-compose.yml handle this automatically
# The frontend will use the NEXT_PUBLIC_API_URL environment variable
```

## Viewing Logs

To view the logs from the running containers:

```bash
docker-compose logs -f
```

To view logs for a specific service:

```bash
docker-compose logs -f frontend
docker-compose logs -f backend
```

## Stopping the Services

To stop the RiskAI services:

```bash
docker-compose down
```

## Reloading Documents

If you add new PDF documents to the `data` directory while the services are running, you can trigger a reload without restarting the containers:

```bash
curl -X POST http://localhost:8000/reload-documents
```

## Troubleshooting

### Port Conflicts

If you see an error about ports being in use, you can either:

1. Stop the services using those ports:
   ```bash
   # Find processes using the ports
   lsof -i :3000
   lsof -i :8000
   
   # Kill the processes
   kill -9 <PID>
   ```

2. Use alternative ports as described in the "Using Custom Ports" section

### Container Startup Issues

If containers fail to start, check the logs:

```bash
docker-compose logs
```

Common issues and solutions:

1. **Backend fails to start**:
   - Check if required Python packages are available
   - Ensure the database directories have correct permissions
   - Look for specific error messages in the logs

2. **Frontend fails to start**:
   - Check if Node.js dependencies are installed correctly
   - Ensure the build process completes successfully
   - Verify the backend URL configuration

3. **Services start but are not healthy**:
   - Check the health check endpoints
   - Ensure the services are responding to requests
   - Look for timeout or connection errors in the logs

### Data Persistence Issues

If you're experiencing issues with data persistence, try the following:

1. Ensure the volume directories have the correct permissions:
   ```bash
   chmod -R 777 data vectordb backend/database_data
   ```

2. Check if Docker has access to the mounted directories:
   ```bash
   # On macOS/Windows, ensure the directories are in a location accessible to Docker
   # On Linux, check SELinux or AppArmor settings if applicable
   ```

3. Verify that the volumes are correctly mounted:
   ```bash
   docker-compose exec backend ls -la /app/data
   docker-compose exec backend ls -la /app/vectordb
   docker-compose exec backend ls -la /app/database_data
   ```

### Connection Issues

If the frontend cannot connect to the backend, ensure:

1. Both services are running:
   ```bash
   docker-compose ps
   ```

2. The backend is accessible at the expected URL:
   ```bash
   curl http://localhost:8000/health
   ```

3. The frontend is configured with the correct backend URL:
   ```bash
   # Check the environment variables in the docker-compose.yml file
   # Verify the NEXT_PUBLIC_API_URL setting
   ```

4. Network connectivity between containers:
   ```bash
   # Check if containers are on the same network
   docker network ls
   docker network inspect riskai_network
   ```

### PDF Processing Issues

If the RAG system is not processing PDF documents correctly:

1. Verify that PDF files are in the correct directory:
   ```bash
   ls -la data/*.pdf
   ```

2. Check if the files are accessible to the container:
   ```bash
   docker-compose exec backend ls -la /app/data
   ```

3. Trigger a manual reload of the documents:
   ```bash
   curl -X POST http://localhost:8000/reload-documents
   ```

4. Check the logs for processing errors:
   ```bash
   docker-compose logs backend | grep -i "pdf\|document\|error"
   ```

### Docker Environment Issues

If you're experiencing issues with the Docker environment:

1. Check Docker status:
   ```bash
   docker info
   ```

2. Verify Docker Compose version:
   ```bash
   docker-compose version
   ```

3. Restart Docker:
   ```bash
   # On macOS/Windows: Restart Docker Desktop
   # On Linux:
   sudo systemctl restart docker
   ```

4. Clean up Docker resources:
   ```bash
   # Stop and remove containers
   docker-compose down
   
   # Remove unused images
   docker image prune -a
   
   # Remove unused volumes
   docker volume prune
   ```

## Data Persistence and Volume Management

RiskAI uses Docker volumes to persist data across container restarts. Understanding how these volumes work is important for proper data management.

### Volume Structure

The RiskAI application uses three main volumes:

1. **data**: Contains PDF documents used by the RAG system
   - Path: `./data:/app/data`
   - Purpose: Stores source documents for knowledge extraction
   - Content: PDF files, documents, and other text sources

2. **vectordb**: Stores vector embeddings for the RAG system
   - Path: `./vectordb:/app/vectordb`
   - Purpose: Persists document embeddings to avoid reprocessing
   - Content: Vector database files, indexes, and metadata

3. **database_data**: Contains the application database
   - Path: `./backend/database_data:/app/database_data`
   - Purpose: Stores user data, assessments, and application state
   - Content: SQLite database files

### Managing PDF Documents

To add new PDF documents to the system:

1. Place the PDF files in the `data` directory
2. If the system is already running, trigger a reload:
   ```bash
   curl -X POST http://localhost:8000/reload-documents
   ```

To remove documents:

1. Delete the PDF files from the `data` directory
2. Trigger a reload as described above

### Backup and Restore

To backup your RiskAI data:

1. Stop the containers:
   ```bash
   docker-compose down
   ```

2. Create a backup of the volume directories:
   ```bash
   tar -czf riskai-backup-$(date +%Y%m%d).tar.gz data vectordb backend/database_data
   ```

To restore from a backup:

1. Ensure the containers are stopped:
   ```bash
   docker-compose down
   ```

2. Extract the backup:
   ```bash
   tar -xzf riskai-backup-YYYYMMDD.tar.gz
   ```

3. Start the containers:
   ```bash
   docker-compose up -d
   ```

### Volume Maintenance

Occasionally, you may need to perform maintenance on the volumes:

1. **Clearing vector database**: If you want to rebuild the vector database from scratch:
   ```bash
   docker-compose down
   rm -rf vectordb/*
   docker-compose up -d
   ```

2. **Resetting the application database**: If you want to reset all user data:
   ```bash
   docker-compose down
   rm -rf backend/database_data/*
   docker-compose up -d
   ```

3. **Checking volume usage**:
   ```bash
   du -sh data vectordb backend/database_data
   ```

### Volume Permissions

If you encounter permission issues with volumes:

1. Ensure the directories have appropriate permissions:
   ```bash
   chmod -R 777 data vectordb backend/database_data
   ```

2. Check ownership:
   ```bash
   ls -la data vectordb backend/database_data
   ```

3. If using SELinux (on some Linux distributions):
   ```bash
   chcon -Rt svirt_sandbox_file_t data vectordb backend/database_data
   ```

## Usage Examples

Here are some common usage scenarios for the RiskAI Docker deployment:

### Example 1: Basic Deployment

Deploy RiskAI with default settings:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/your-org/riskai.git
cd riskai

# Start RiskAI with a single command
./start_riskai.sh
```

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Example 2: Deployment with Custom Ports

Deploy RiskAI with custom ports to avoid conflicts with other services:

```bash
# Set custom ports
export FRONTEND_PORT=3001
export BACKEND_PORT=8001

# Start RiskAI
./start_riskai.sh
```

Access the application at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001

### Example 3: Adding Documents After Deployment

Add new documents to an already running RiskAI instance:

```bash
# Copy new documents to the data directory
cp /path/to/your/documents/*.pdf data/

# Trigger a document reload
curl -X POST http://localhost:8000/reload-documents
```

### Example 4: Monitoring and Maintenance

Monitor the running services:

```bash
# View logs from all services
docker-compose logs -f

# Check container status
docker-compose ps

# Restart services
docker-compose restart

# Stop services
docker-compose down
```

### Example 5: Production Deployment

For a production deployment with enhanced security:

```bash
# Create a .env file with production settings
cat > .env << EOF
FRONTEND_PORT=3000
BACKEND_PORT=8000
NODE_ENV=production
EOF

# Start RiskAI with production settings
docker-compose up -d
```

Additional production considerations:
- Set up a reverse proxy (like Nginx) for SSL termination
- Configure proper authentication
- Set up regular backups of the data volumes
- Monitor container health and resource usage

### Example 6: Development Environment

For a development environment with live logs:

```bash
# Start services in foreground mode
docker-compose up

# In another terminal, make changes to your code
# The services will automatically reload (if configured)
```

## Next Steps

After deploying RiskAI, you can:

1. Set up your company profile
2. Upload relevant documents
3. Start using the risk assessment features
4. Explore the benchmarking and validation capabilities