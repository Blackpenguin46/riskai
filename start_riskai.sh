#!/bin/bash

# RiskAI Single Command Deployment Script
# This script provides a simple way to deploy the RiskAI application with Docker

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default configuration
FRONTEND_PORT=3000
BACKEND_PORT=8000
COMPOSE_FILE="docker-compose.yml"

# Display banner
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}       RiskAI Deployment Tool           ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if running on Windows with WSL
if [ -n "$WINDIR" ] || [ -n "$windir" ]; then
    echo -e "${YELLOW}Windows environment detected${NC}"
    echo -e "${YELLOW}Ensuring Docker is accessible through WSL...${NC}"
    # Additional Windows-specific checks could be added here
fi

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
    echo -e "${YELLOW}docker-compose not found as standalone command${NC}"
    echo -e "${YELLOW}Will try to use 'docker compose' instead${NC}"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Verify docker compose command works
if ! $COMPOSE_CMD version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not available${NC}"
    echo "Please install Docker Compose and try again"
    exit 1
fi

# Function to check if a port is in use (platform-independent)
check_port() {
    local port=$1
    
    # Try different methods based on available commands
    if command -v nc &> /dev/null; then
        nc -z localhost $port &> /dev/null
        return $?
    elif command -v lsof &> /dev/null; then
        lsof -i :$port &> /dev/null
        return $?
    elif command -v netstat &> /dev/null; then
        netstat -an | grep "LISTEN" | grep -q ":$port "
        return $?
    else
        # If no tools are available, assume port is free
        # This is not ideal but allows the script to continue
        echo -e "${YELLOW}Warning: Cannot check if port $port is in use${NC}"
        echo -e "${YELLOW}Assuming port is available${NC}"
        return 1
    fi
}

# Function to handle port conflicts
handle_port_conflicts() {
    local frontend_in_use=false
    local backend_in_use=false
    
    echo -e "${BLUE}Checking for port conflicts...${NC}"
    
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
                
                echo -e "${GREEN}Using alternative ports: Frontend=$FRONTEND_PORT, Backend=$BACKEND_PORT${NC}"
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
    else
        echo -e "${GREEN}No port conflicts detected${NC}"
    fi
}

# Function to create required directories
create_directories() {
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
}

# Function to display progress spinner
show_spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    
    echo -n "Starting services "
    
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    
    printf "    \b\b\b\b"
}

# Function to wait for services to be healthy
wait_for_services() {
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    
    # Wait for backend to be healthy
    echo -n "Waiting for backend service "
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$BACKEND_PORT/health &> /dev/null; then
            echo -e "\n${GREEN}Backend service is ready!${NC}"
            break
        fi
        
        attempt=$((attempt+1))
        echo -n "."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo -e "\n${RED}Backend service did not become ready in time${NC}"
        echo "Check the logs for more information:"
        echo "$COMPOSE_CMD logs backend"
    fi
    
    # Wait for frontend to be healthy
    echo -n "Waiting for frontend service "
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$FRONTEND_PORT/api/health &> /dev/null; then
            echo -e "\n${GREEN}Frontend service is ready!${NC}"
            break
        fi
        
        attempt=$((attempt+1))
        echo -n "."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo -e "\n${RED}Frontend service did not become ready in time${NC}"
        echo "Check the logs for more information:"
        echo "$COMPOSE_CMD logs frontend"
    fi
}

# Main deployment function
deploy_riskai() {
    # Check for port conflicts
    handle_port_conflicts
    
    # Create required directories
    create_directories
    
    # Set environment variables
    export FRONTEND_PORT
    export BACKEND_PORT
    
    # Stop any existing containers
    echo -e "${BLUE}Stopping any existing RiskAI containers...${NC}"
    $COMPOSE_CMD down
    
    # Start services
    echo -e "${BLUE}Starting RiskAI with Docker...${NC}"
    echo -e "${BLUE}This may take a few minutes on first run${NC}"
    
    $COMPOSE_CMD up --build -d
    
    # Check if containers started successfully
    if [ $? -eq 0 ]; then
        # Wait for services to be healthy
        wait_for_services
        
        echo -e "${GREEN}RiskAI has been deployed successfully!${NC}"
        echo -e "${GREEN}Frontend: http://localhost:$FRONTEND_PORT${NC}"
        echo -e "${GREEN}Backend API: http://localhost:$BACKEND_PORT${NC}"
        echo ""
        echo -e "${BLUE}To view logs:${NC}"
        echo "$COMPOSE_CMD logs -f"
        echo ""
        echo -e "${BLUE}To stop the services:${NC}"
        echo "$COMPOSE_CMD down"
    else
        echo -e "${RED}Failed to start RiskAI containers${NC}"
        echo "Check the error messages above for more information"
        exit 1
    fi
}

# Execute deployment
deploy_riskai