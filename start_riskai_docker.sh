#!/bin/bash

# RiskAI Docker Startup Script
# This script provides a simple way to start the RiskAI application with Docker

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default ports
FRONTEND_PORT=3000
BACKEND_PORT=8000

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}       RiskAI Docker Startup Tool       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    echo "Please install Docker and try again"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Warning: docker-compose not found as standalone command${NC}"
    echo "Will try to use 'docker compose' instead"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if command -v nc &> /dev/null; then
        nc -z localhost $port &> /dev/null
        return $?
    elif command -v lsof &> /dev/null; then
        lsof -i :$port &> /dev/null
        return $?
    else
        # If neither nc nor lsof is available, assume port is free
        return 1
    fi
}

# Check if ports are in use and offer alternatives
check_ports() {
    local frontend_in_use=false
    local backend_in_use=false
    
    if check_port $FRONTEND_PORT; then
        echo -e "${YELLOW}Warning: Port $FRONTEND_PORT is already in use${NC}"
        frontend_in_use=true
    fi
    
    if check_port $BACKEND_PORT; then
        echo -e "${YELLOW}Warning: Port $BACKEND_PORT is already in use${NC}"
        backend_in_use=true
    fi
    
    if $frontend_in_use || $backend_in_use; then
        echo -e "${YELLOW}Would you like to:${NC}"
        echo "1. Stop the services using these ports"
        echo "2. Use alternative ports"
        echo "3. Exit"
        read -p "Enter your choice (1-3): " choice
        
        case $choice in
            1)
                echo -e "${BLUE}Stopping services using ports $FRONTEND_PORT and $BACKEND_PORT...${NC}"
                if $frontend_in_use; then
                    if command -v lsof &> /dev/null; then
                        pid=$(lsof -t -i:$FRONTEND_PORT)
                        if [ ! -z "$pid" ]; then
                            echo "Stopping process using port $FRONTEND_PORT (PID: $pid)"
                            kill -9 $pid
                        fi
                    else
                        echo -e "${RED}Cannot automatically stop services. Please stop them manually.${NC}"
                        exit 1
                    fi
                fi
                
                if $backend_in_use; then
                    if command -v lsof &> /dev/null; then
                        pid=$(lsof -t -i:$BACKEND_PORT)
                        if [ ! -z "$pid" ]; then
                            echo "Stopping process using port $BACKEND_PORT (PID: $pid)"
                            kill -9 $pid
                        fi
                    else
                        echo -e "${RED}Cannot automatically stop services. Please stop them manually.${NC}"
                        exit 1
                    fi
                fi
                ;;
            2)
                if $frontend_in_use; then
                    read -p "Enter alternative port for frontend (default: 3001): " new_frontend_port
                    FRONTEND_PORT=${new_frontend_port:-3001}
                fi
                
                if $backend_in_use; then
                    read -p "Enter alternative port for backend (default: 8001): " new_backend_port
                    BACKEND_PORT=${new_backend_port:-8001}
                fi
                
                # Create a temporary docker-compose override file
                cat > docker-compose.override.yml << EOF
version: '3'
services:
  frontend:
    ports:
      - "${FRONTEND_PORT}:3000"
  backend:
    ports:
      - "${BACKEND_PORT}:8000"
    environment:
      - PORT=8000
EOF
                echo -e "${GREEN}Created docker-compose.override.yml with alternative ports${NC}"
                ;;
            3)
                echo -e "${YELLOW}Exiting...${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice. Exiting...${NC}"
                exit 1
                ;;
        esac
    fi
}

# Create necessary directories if they don't exist
echo -e "${BLUE}Checking required directories...${NC}"

if [ ! -d "data" ]; then
    echo -e "${YELLOW}Creating data directory for PDF documents${NC}"
    mkdir -p data
    echo -e "${YELLOW}Note: You should add your PDF documents to the 'data' directory${NC}"
fi

if [ ! -d "vectordb" ]; then
    echo -e "${YELLOW}Creating vectordb directory for vector database${NC}"
    mkdir -p vectordb
fi

if [ ! -d "backend/database_data" ]; then
    echo -e "${YELLOW}Creating database_data directory for SQLite database${NC}"
    mkdir -p backend/database_data
fi

# Check if any PDF files exist in the data directory
if [ -d "data" ] && [ -z "$(ls -A data/*.pdf 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: No PDF files found in the data directory${NC}"
    echo -e "${YELLOW}The RAG system needs PDF documents to function properly${NC}"
    echo -e "${YELLOW}Please add PDF files to the 'data' directory before or after starting${NC}"
fi

# Check if ports are in use
check_ports

# Stop any existing containers
echo -e "${BLUE}Stopping any existing RiskAI containers...${NC}"
$COMPOSE_CMD down

# Build and start the containers
echo -e "${BLUE}Starting RiskAI with Docker...${NC}"
echo -e "${BLUE}This may take a few minutes on first run${NC}"

# Use the appropriate docker-compose command
$COMPOSE_CMD up --build -d

# Check if containers started successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}RiskAI is starting up!${NC}"
    echo -e "${GREEN}Frontend will be available at: http://localhost:${FRONTEND_PORT}${NC}"
    echo -e "${GREEN}Backend API will be available at: http://localhost:${BACKEND_PORT}${NC}"
    echo ""
    echo -e "${BLUE}Container logs:${NC}"
    $COMPOSE_CMD logs -f
else
    echo -e "${RED}Failed to start RiskAI containers${NC}"
    echo "Check the error messages above for more information"
    exit 1
fi