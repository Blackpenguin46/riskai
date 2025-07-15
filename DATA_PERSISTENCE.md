# RiskAI Data Persistence Guide

## Overview

RiskAI now includes comprehensive data persistence functionality that automatically saves all assessment results, company data, and system state. This means your data will be preserved even when you close and restart the Docker containers.

## What Gets Saved Automatically

### ✅ Assessment Data
- **Complete assessment results** - All question responses, section scores, and overall scores
- **Assessment progress** - Partial assessments are saved so you can resume where you left off
- **Assessment history** - Multiple assessments are stored with timestamps
- **Scoring details** - NIST CSF 2.0 maturity levels, risk assessments, and recommendations

### ✅ Company Information
- **Company profile** - Name, industry, size, country
- **Contact information** - Primary contact, email, phone
- **Compliance settings** - Required frameworks and assessment frequency
- **Risk tolerance** - Configured risk management preferences

### ✅ System State
- **Configuration settings** - System preferences and customizations
- **Application state** - Various system settings and user preferences

## How Data Persistence Works

### Automatic Saving
- **Assessment progress** is automatically saved after completing each section
- **Company data** is saved when you fill out the company setup form
- **Final results** are saved when you complete an assessment

### Database Storage
- All data is stored in a **SQLite database** (`riskai.db`)
- The database file is located in `backend/database_data/riskai.db`
- This file is **persistent** and survives Docker restarts

### Volume Mounting
The Docker configuration includes persistent volume mounts:
```yaml
volumes:
  - ./backend/database_data:/app/database_data  # Database persistence
  - ./backend/data:/app/data                    # PDF documents
  - ./backend/vectordb:/app/vectordb            # Vector embeddings
```

## Using the Persistence Features

### 1. Resuming Assessments
- Start an assessment and answer some questions
- Close Docker containers: `docker-compose down`
- Restart containers: `docker-compose up -d`
- Go back to `/assessment` - **your progress is automatically restored**

### 2. Company Setup
- Navigate to `/company-setup` (or access via dashboard)
- Fill out your company information
- Click "Save Company Data"
- Data is permanently stored and will be available after restarts

### 3. Assessment History
The system maintains a complete history of all assessments:
- Multiple assessments can be stored
- Each assessment has a unique ID and timestamp
- Previous assessments can be loaded and reviewed

## API Endpoints for Data Management

### Assessment Management
```http
# Save assessment (automatic)
POST /assessment/save

# Load specific assessment
GET /assessment/load/{assessment_id}

# Get latest assessment
GET /assessment/latest

# List all assessments
GET /assessments/list
```

### Company Data
```http
# Save company data
POST /company/save

# Get company data
GET /company/{company_id}
```

### Data Backup & Restore
```http
# Create full backup
GET /data/backup

# Restore from backup
POST /data/restore
```

## Data Backup and Recovery

### Creating Backups
1. **Automatic file backup**: The SQLite database file is automatically backed up as part of the persistent volume
2. **API backup**: Use `GET /data/backup` to create a JSON export of all data
3. **Manual backup**: Copy the `backend/database_data/` folder

### Example: Create API Backup
```bash
# Create a backup via API
curl http://localhost:8000/data/backup > riskai_backup.json

# Restore from backup (if needed)
curl -X POST http://localhost:8000/data/restore \
  -H "Content-Type: application/json" \
  -d @riskai_backup.json
```

### Recovery Process
If you need to recover data:

1. **From file backup**: Restore the `backend/database_data/riskai.db` file
2. **From API backup**: Use the `/data/restore` endpoint with your JSON backup
3. **Migration**: The system will automatically create the database if it doesn't exist

## Data Location and File Structure

```
riskai/
├── backend/
│   ├── database_data/           # 🔄 PERSISTENT
│   │   └── riskai.db           # Main SQLite database
│   ├── data/                   # 🔄 PERSISTENT  
│   │   └── *.pdf              # Uploaded documents
│   └── vectordb/              # 🔄 PERSISTENT
│       └── chroma.sqlite3     # Vector embeddings
├── frontend/
└── docker-compose.yml
```

## Important Notes

### ✅ What Persists
- **All assessment data** and results
- **Company information** and settings
- **Uploaded documents** (PDFs)
- **Vector embeddings** for AI functionality
- **System configuration**

### ❌ What Doesn't Persist
- **Runtime logs** (these are ephemeral)
- **Temporary files** and caches
- **Session data** (you'll need to re-authenticate if applicable)

### 🔒 Data Security
- Database is stored locally on your machine
- No data is sent to external servers
- All data remains within your Docker environment
- Standard SQLite security practices apply

## Troubleshooting

### Database Issues
```bash
# Check if database exists
ls -la backend/database_data/

# Check database tables
sqlite3 backend/database_data/riskai.db ".tables"

# View assessment count
sqlite3 backend/database_data/riskai.db "SELECT COUNT(*) FROM assessments;"
```

### Container Issues
```bash
# Restart with fresh containers (data persists)
docker-compose down
docker-compose up -d

# Rebuild containers (data persists)
docker-compose down
docker-compose build
docker-compose up -d
```

### Data Recovery
```bash
# Backup current data
cp -r backend/database_data backup_$(date +%Y%m%d)

# Check available assessments via API
curl http://localhost:8000/assessments/list
```

## Best Practices

1. **Regular Backups**: Periodically backup the `database_data` folder
2. **Assessment Naming**: Use descriptive names for assessments
3. **Company Setup**: Complete company setup before running assessments
4. **Version Control**: Keep the `database_data` folder in `.gitignore` for security
5. **Monitor Storage**: The database will grow over time with multiple assessments

## Getting Started

1. **First Time Setup**:
   - Run `docker-compose up -d`
   - Navigate to `/company-setup` and configure your company
   - Start your first assessment at `/assessment`

2. **Daily Usage**:
   - Assessments automatically save progress
   - Docker can be stopped/started without data loss
   - Access assessment history via API or future UI features

3. **Data Management**:
   - Use API endpoints for programmatic access
   - Create regular backups for important assessments
   - Monitor the `database_data` folder for growth

Your data is now safe and persistent across Docker restarts! 🎉