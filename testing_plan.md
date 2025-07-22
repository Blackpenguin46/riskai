# RiskAI Docker Deployment Testing Plan

This document outlines the testing plan for the RiskAI Docker deployment across different platforms.

## 1. Linux Environment Testing

### Test Environment Setup

- **Distributions to test:**
  - Ubuntu 22.04 LTS
  - Debian 11
  - CentOS/RHEL 8
  - Alpine Linux (for container-optimized environments)

- **Prerequisites:**
  - Docker Engine 20.10+
  - Docker Compose 2.0+
  - Bash 4.0+
  - curl

### Test Cases

#### 1.1 Basic Deployment Test

**Steps:**
1. Clone the repository
2. Run `./start_riskai.sh`
3. Wait for services to start
4. Access frontend at http://localhost:3000
5. Access backend at http://localhost:8000

**Expected Results:**
- Script runs without errors
- Both services start successfully
- Frontend loads and connects to backend
- Backend health check returns success

#### 1.2 Custom Port Configuration Test

**Steps:**
1. Set environment variables: `export FRONTEND_PORT=3001 BACKEND_PORT=8001`
2. Run `./start_riskai.sh`
3. Access frontend at http://localhost:3001
4. Access backend at http://localhost:8001

**Expected Results:**
- Services start on the specified ports
- Frontend correctly connects to backend on port 8001
- No port conflicts occur

#### 1.3 Data Persistence Test

**Steps:**
1. Run `./start_riskai.sh`
2. Create a test profile in the application
3. Stop containers with `docker-compose down`
4. Start containers again with `./start_riskai.sh`
5. Check if the test profile still exists

**Expected Results:**
- Data persists across container restarts
- Test profile is still available after restart

#### 1.4 PDF Processing Test

**Steps:**
1. Run `./start_riskai.sh`
2. Add PDF files to the `data` directory
3. Trigger document reload with `curl -X POST http://localhost:8000/reload-documents`
4. Check if documents are processed

**Expected Results:**
- Documents are successfully loaded
- Vector embeddings are created
- Documents are available for RAG queries

#### 1.5 Error Handling Test

**Steps:**
1. Deliberately create error conditions:
   - Occupy ports 3000 and 8000 before running the script
   - Remove required directories
   - Use invalid configuration
2. Run `./start_riskai.sh`

**Expected Results:**
- Script detects errors and provides helpful messages
- Port conflict resolution works as expected
- Missing directories are created automatically
- Invalid configurations are reported with clear error messages

### Linux-Specific Considerations

- **SELinux/AppArmor:** Test with security modules enabled
- **File Permissions:** Test with different user permissions
- **Resource Constraints:** Test with limited CPU/memory resources
- **Network Configurations:** Test with different network setups (bridge, host, etc.)

## 2. macOS Environment Testing

### Test Environment Setup

- **macOS versions to test:**
  - macOS Monterey (12.x)
  - macOS Ventura (13.x)
  - macOS Sonoma (14.x)

- **Prerequisites:**
  - Docker Desktop for Mac 4.0+
  - Bash 3.2+ (default on macOS)
  - curl

### Test Cases

#### 2.1 Basic Deployment Test

**Steps:**
1. Clone the repository
2. Run `./start_riskai.sh`
3. Wait for services to start
4. Access frontend at http://localhost:3000
5. Access backend at http://localhost:8000

**Expected Results:**
- Script runs without errors
- Both services start successfully
- Frontend loads and connects to backend
- Backend health check returns success

#### 2.2 Custom Port Configuration Test

**Steps:**
1. Set environment variables: `export FRONTEND_PORT=3001 BACKEND_PORT=8001`
2. Run `./start_riskai.sh`
3. Access frontend at http://localhost:3001
4. Access backend at http://localhost:8001

**Expected Results:**
- Services start on the specified ports
- Frontend correctly connects to backend on port 8001
- No port conflicts occur

#### 2.3 Docker Desktop Resource Allocation Test

**Steps:**
1. Configure Docker Desktop with different resource allocations:
   - Minimal resources (1 CPU, 2GB RAM)
   - Medium resources (2 CPU, 4GB RAM)
   - High resources (4 CPU, 8GB RAM)
2. Run `./start_riskai.sh` with each configuration
3. Monitor performance and startup time

**Expected Results:**
- Application starts successfully with all resource configurations
- Performance scales appropriately with resources
- Minimum resource requirements are documented

#### 2.4 File System Performance Test

**Steps:**
1. Run `./start_riskai.sh`
2. Add large PDF files to the `data` directory
3. Trigger document reload
4. Monitor file system performance

**Expected Results:**
- Files are processed correctly
- Performance is acceptable even with large files
- No file system permission issues occur

#### 2.5 macOS Sleep/Resume Test

**Steps:**
1. Run `./start_riskai.sh`
2. Put macOS to sleep
3. Resume from sleep
4. Check if services are still running and accessible

**Expected Results:**
- Services recover properly after sleep/resume
- No connection issues occur
- Data remains intact

### macOS-Specific Considerations

- **File System:** Test with both APFS and HFS+ file systems
- **Docker Desktop Settings:** Test with different virtualization settings
- **Network:** Test with different network configurations (Wi-Fi, Ethernet, VPN)
- **Resource Monitoring:** Monitor CPU, memory, and disk usage during operation

## 3. Windows Environment Testing

### Test Environment Setup

- **Windows versions to test:**
  - Windows 10 Pro/Enterprise (latest build)
  - Windows 11 Pro/Enterprise (latest build)
  - Windows Server 2019/2022

- **Prerequisites:**
  - Docker Desktop for Windows 4.0+
  - Windows Subsystem for Linux 2 (WSL2)
  - Git Bash or WSL Bash
  - curl

### Test Cases

#### 3.1 WSL2 Basic Deployment Test

**Steps:**
1. Clone the repository in WSL2
2. Run `./start_riskai.sh` from WSL2 bash
3. Wait for services to start
4. Access frontend at http://localhost:3000
5. Access backend at http://localhost:8000

**Expected Results:**
- Script runs without errors
- Both services start successfully
- Frontend loads and connects to backend
- Backend health check returns success

#### 3.2 Git Bash Deployment Test

**Steps:**
1. Clone the repository
2. Run `./start_riskai.sh` from Git Bash
3. Wait for services to start
4. Access frontend and backend

**Expected Results:**
- Script runs without errors in Git Bash environment
- Services start successfully
- All functionality works as expected

#### 3.3 Path Handling Test

**Steps:**
1. Clone the repository to a path with spaces and special characters
2. Run `./start_riskai.sh`
3. Check if services start correctly

**Expected Results:**
- Script handles Windows paths correctly
- Volume mounts work with spaces and special characters
- No path-related errors occur

#### 3.4 Docker Desktop Integration Test

**Steps:**
1. Test integration with Docker Desktop features:
   - Resource allocation
   - Network configuration
   - Volume management
2. Run `./start_riskai.sh` with different configurations

**Expected Results:**
- Application integrates well with Docker Desktop
- Resource controls work as expected
- Network and volume configurations are applied correctly

#### 3.5 Windows Firewall Test

**Steps:**
1. Enable Windows Firewall with different settings
2. Run `./start_riskai.sh`
3. Check if services are accessible

**Expected Results:**
- Docker handles firewall permissions correctly
- Services are accessible through the firewall
- No unexpected connection issues occur

### Windows-Specific Considerations

- **WSL2 Integration:** Test with different WSL2 distributions
- **File System Performance:** Test with files on both Windows and WSL file systems
- **Line Endings:** Ensure scripts handle Windows line endings correctly
- **Path Length Limitations:** Test with deeply nested directories
- **Anti-Virus Software:** Test with different anti-virus solutions enabled

## 4. Data Persistence Validation

### Test Environment Setup

- **Test across all platforms:**
  - Linux
  - macOS
  - Windows with WSL2

- **Prerequisites:**
  - Docker and Docker Compose
  - Test data files
  - Database inspection tools

### Test Cases

#### 4.1 Container Restart Persistence Test

**Steps:**
1. Start RiskAI with `./start_riskai.sh`
2. Create test data:
   - Upload PDF documents
   - Create user profiles
   - Perform assessments
3. Restart containers with `docker-compose restart`
4. Check if all data is preserved

**Expected Results:**
- All user data persists after container restart
- PDF documents remain processed
- Assessment data is preserved

#### 4.2 Full System Restart Test

**Steps:**
1. Start RiskAI and create test data
2. Stop containers with `docker-compose down`
3. Restart the host system
4. Start RiskAI again with `./start_riskai.sh`
5. Check if all data is preserved

**Expected Results:**
- All data persists after full system restart
- Application state is correctly restored
- No data corruption occurs

#### 4.3 Volume Backup and Restore Test

**Steps:**
1. Start RiskAI and create test data
2. Stop containers
3. Backup volume directories
4. Delete volume directories
5. Restore from backup
6. Start RiskAI again
7. Check if all data is preserved

**Expected Results:**
- Backup process works correctly
- Restore process recovers all data
- Application functions normally with restored data

#### 4.4 Database Integrity Test

**Steps:**
1. Start RiskAI and create test data
2. Stop containers
3. Inspect database files directly
4. Verify database integrity
5. Start RiskAI again

**Expected Results:**
- Database files are properly structured
- No corruption occurs during normal operation
- Database can be inspected and verified

#### 4.5 Concurrent Access Test

**Steps:**
1. Start RiskAI
2. Simulate multiple users accessing the system concurrently
3. Check for data consistency issues
4. Stop and restart containers
5. Verify data integrity

**Expected Results:**
- Data remains consistent with concurrent access
- No race conditions or corruption occurs
- All data persists correctly after restart

### Data Persistence Considerations

- **Volume Permissions:** Test with different user/group permissions
- **Storage Types:** Test with different storage backends (local disk, NFS, etc.)
- **Disk Space:** Test behavior when disk space is limited
- **Database Backups:** Verify automated and manual backup procedures
- **Data Migration:** Test upgrading between different versions

## 5. Error Recovery Testing

### Test Environment Setup

- **Test across all platforms:**
  - Linux
  - macOS
  - Windows with WSL2

- **Prerequisites:**
  - Docker and Docker Compose
  - Network tools (netstat, curl, etc.)
  - Process management tools

### Test Cases

#### 5.1 Port Conflict Resolution Test

**Steps:**
1. Deliberately occupy ports 3000 and 8000 with other services
2. Run `./start_riskai.sh`
3. Test both automatic and manual port conflict resolution

**Expected Results:**
- Script detects port conflicts
- User is presented with clear options
- Alternative ports work correctly when selected
- Frontend correctly connects to backend on alternative port

#### 5.2 Missing Directory Recovery Test

**Steps:**
1. Delete required directories (data, vectordb, database_data)
2. Run `./start_riskai.sh`
3. Check if directories are recreated

**Expected Results:**
- Script detects missing directories
- Directories are created automatically
- Application starts normally
- User is informed about the actions taken

#### 5.3 Container Failure Recovery Test

**Steps:**
1. Start RiskAI with `./start_riskai.sh`
2. Manually kill one of the containers
3. Check if health checks detect the failure
4. Restart the services

**Expected Results:**
- Health checks correctly identify container failures
- Clear error messages are provided
- Recovery instructions are accurate
- Services can be restarted successfully

#### 5.4 Network Interruption Test

**Steps:**
1. Start RiskAI
2. Simulate network interruptions:
   - Disconnect network temporarily
   - Block specific ports
   - Introduce network latency
3. Check how the application handles the interruptions

**Expected Results:**
- Application handles network interruptions gracefully
- Connections are re-established when possible
- Clear error messages are provided to the user
- No data corruption occurs

#### 5.5 Resource Exhaustion Test

**Steps:**
1. Start RiskAI
2. Simulate resource exhaustion:
   - Limit available memory
   - Limit available CPU
   - Fill disk space
3. Check how the application handles resource constraints

**Expected Results:**
- Application degrades gracefully under resource constraints
- Clear error messages are provided
- No data corruption occurs
- Application recovers when resources are available again

### Error Recovery Considerations

- **Logging:** Verify that error conditions are properly logged
- **User Guidance:** Check that error messages provide clear next steps
- **Automatic Recovery:** Test automatic recovery mechanisms where applicable
- **Manual Recovery:** Verify that manual recovery procedures work as documented
- **Data Integrity:** Ensure that error conditions don't lead to data corruption