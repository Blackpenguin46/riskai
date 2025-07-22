# RiskAI Scoring System

## Overview

The RiskAI Scoring System provides comprehensive mathematical scoring for cybersecurity risk assessments. It implements precise formulas, statistical analysis, and industry benchmarking to deliver accurate risk evaluations.

## Architecture

### Core Components

1. **ScoringEngine** (`scoring_engine.py`)
   - Mathematical scoring algorithms
   - Question, section, and overall score calculations
   - Risk level categorization

2. **RiskCategorizationEngine** (`../assessment/risk_categorization.py`)
   - Advanced risk level assignment
   - Statistical confidence intervals
   - Industry benchmarking and trend analysis

3. **Scoring API** (`../assessment/scoring_api.py`)
   - REST API endpoints for all scoring functionality
   - Weight management and methodology documentation
   - Audit logging and export capabilities

4. **Database Models** (`../database/models.py`)
   - ScoringWeights, ScoringMethodology, AssessmentResult
   - IndustryBenchmarks, ScoringAuditLog
   - Enhanced data persistence

5. **Benchmark Data Loader** (`benchmark_data_loader.py`)
   - Sample industry benchmark data
   - Database population utilities
   - Benchmark management functions

## Mathematical Formulas

### Question Scoring
```
Question Score = Normalized Answer Value × Question Weight
```

### Section Scoring
```
Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100
```

### Overall Scoring
```
Overall Score = Σ(Section Score × Section Weight)

Where Section Weights:
- Governance: 20%
- Technical Controls: 40% (Asset Mgmt + Data Protection + Access Control + Monitoring)
- Operational: 25% (Incident Response + Business Continuity + Awareness)
- Compliance: 15% (Compliance + Emerging Tech + Third Party + Risk Mgmt)
```

### Risk Level Categories
- **Critical Risk**: 0-40 (Immediate action required)
- **High Risk**: 41-60 (Priority improvements needed)
- **Medium Risk**: 61-80 (Moderate improvements recommended)
- **Low Risk**: 81-100 (Maintain current practices)

### Confidence Intervals
```
CI = Score ± √(Completion Margin² + Statistical Margin²)

Where:
- Completion Margin = (1 - Completion Rate) × 15%
- Statistical Margin = Z-score × (Industry StdDev / √Sample Size)
```

## API Endpoints

### Core Scoring
- `POST /scoring/calculate` - Calculate comprehensive assessment score
- `POST /scoring/question` - Score individual question
- `POST /scoring/section` - Score complete section
- `POST /scoring/export` - Generate detailed scoring report

### Configuration
- `GET /scoring/formula` - Get scoring methodology and formulas
- `GET /scoring/weights` - Get current question and section weights
- `POST /scoring/weights` - Update scoring weights
- `GET /scoring/benchmarks/{industry}` - Get industry benchmarks

### Methodology Management
- `POST /scoring/methodology` - Create/update scoring methodology
- `GET /scoring/methodology/{name}` - Get specific methodology
- `GET /scoring/audit/{assessment_id}` - Get scoring audit log

## Database Schema

### ScoringWeights
```sql
CREATE TABLE scoring_weights (
    id INTEGER PRIMARY KEY,
    weight_type VARCHAR(50) NOT NULL,  -- section, question, category
    identifier VARCHAR(100) NOT NULL,  -- section_id, question_id, etc.
    weight_value FLOAT NOT NULL,
    max_score FLOAT NOT NULL,
    description TEXT,
    formula TEXT,
    version VARCHAR(20) DEFAULT '1.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### IndustryBenchmarks
```sql
CREATE TABLE industry_benchmarks (
    id INTEGER PRIMARY KEY,
    industry VARCHAR(100) NOT NULL,
    company_size VARCHAR(50) NOT NULL,
    average_score FLOAT NOT NULL,
    standard_deviation FLOAT NOT NULL,
    sample_size INTEGER NOT NULL,
    percentile_10 FLOAT,
    percentile_25 FLOAT,
    percentile_50 FLOAT,
    percentile_75 FLOAT,
    percentile_90 FLOAT,
    data_source VARCHAR(200),
    collection_method VARCHAR(200),
    data_quality_score FLOAT,
    data_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### ScoringAuditLog
```sql
CREATE TABLE scoring_audit_log (
    id INTEGER PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,  -- calculate, update, validate
    assessment_id INTEGER,
    input_data JSON,
    methodology_used VARCHAR(100),
    output_data JSON,
    execution_time_ms INTEGER,
    status VARCHAR(20) NOT NULL,  -- success, error, warning
    error_message TEXT,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Examples

### Calculate Assessment Score
```python
import requests

response = requests.post("http://localhost:8000/scoring/calculate", json={
    "assessment_id": 123,
    "methodology": "default",
    "include_confidence": True,
    "include_benchmarking": True,
    "industry": "financial_services",
    "company_size": "large"
})

result = response.json()
print(f"Overall Score: {result['overall_score']}%")
print(f"Risk Level: {result['risk_level']}")
```

### Score Individual Question
```python
response = requests.post("http://localhost:8000/scoring/question", json={
    "question_id": "gov_001",
    "question_type": "boolean",
    "answer": True
})

result = response.json()
print(f"Question Score: {result['percentage']}%")
```

### Get Industry Benchmarks
```python
response = requests.get("http://localhost:8000/scoring/benchmarks/technology")
benchmarks = response.json()

for benchmark in benchmarks['benchmarks']:
    print(f"Average Score: {benchmark['average_score']}")
    print(f"Sample Size: {benchmark['sample_size']}")
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
python test_scoring_api.py
```

The test suite covers:
- Formula and weight endpoints
- Individual question scoring
- Section scoring
- Assessment scoring
- Methodology management
- Industry benchmarks
- Export functionality

## Configuration

### Section Weights
Default section weights are defined in `scoring_engine.py`:

```python
SECTION_WEIGHTS = {
    'governance': 20,           # Strategic foundation
    'asset_management': 8,      # Technical visibility
    'data_protection': 12,      # Technical security
    'access_control': 12,       # Technical security
    'security_monitoring': 10,  # Technical detection
    'incident_response': 10,    # Operational resilience
    'business_continuity': 8,   # Operational resilience
    'security_awareness': 6,    # Operational culture
    'compliance': 4,            # Regulatory alignment
    'emerging_tech': 4,         # Innovation risk
    'third_party': 4,           # Extended ecosystem
    'risk_management': 2        # Process maturity
}
```

### Question Types
Supported question types and scoring:

- **Boolean**: True = full points, False = 0 points
- **Scale**: Normalized to question weight (1-5 scale)
- **Select**: Score based on option position (higher = better)
- **Multiselect**: Score based on valid selections ratio
- **Text**: Full points if answered, 0 if empty

## Industry Benchmarks

The system includes benchmark data for:
- Financial Services
- Healthcare
- Technology
- Manufacturing
- Government

Each benchmark includes:
- Average scores and standard deviations
- Percentile distributions (10th, 25th, 50th, 75th, 90th)
- Sample sizes and data quality scores
- Data sources and collection methods

## Error Handling

The scoring system implements comprehensive error handling:

1. **Input Validation**: All inputs are validated before processing
2. **Database Errors**: Proper rollback and error logging
3. **Calculation Errors**: Graceful handling of mathematical edge cases
4. **API Errors**: Structured error responses with details
5. **Audit Logging**: All operations are logged for debugging

## Performance Considerations

- Database queries are optimized with proper indexing
- Scoring calculations are cached where appropriate
- Audit logs are rotated to prevent database bloat
- API responses include execution time metrics

## Security

- All database operations use parameterized queries
- Input sanitization prevents injection attacks
- Audit trails track all scoring operations
- Access controls protect sensitive benchmark data

## Future Enhancements

Planned improvements include:
- Machine learning-based scoring adjustments
- Real-time benchmark updates
- Advanced statistical analysis
- Custom scoring methodologies
- Integration with external risk frameworks