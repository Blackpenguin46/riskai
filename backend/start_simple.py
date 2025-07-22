#!/usr/bin/env python3
"""
Simple FastAPI server for RiskAI scoring system
Uses minimal dependencies and older, stable versions
"""

import sys
import os
from typing import Dict, Any, Optional

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError as e:
    print(f"Missing dependencies. Please run:")
    print("pip install -r requirements-fixed.txt")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(title="RiskAI Scoring System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "RiskAI Scoring System", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "scoring_system": "active"}

@app.get("/scoring/formula")
def get_scoring_formula():
    """Get scoring formulas and methodology"""
    return {
        "methodology": {
            "name": "RiskAI Mathematical Scoring System",
            "version": "1.0",
            "description": "Comprehensive risk assessment scoring using weighted mathematical formulas"
        },
        "formulas": {
            "question_score": "Question Score = Normalized Answer Value × Question Weight",
            "section_score": "Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100",
            "overall_score": "Overall Score = Σ(Section Score × Section Weight)"
        },
        "section_weights": {
            "governance": 20,
            "asset_management": 8,
            "data_protection": 12,
            "access_control": 12,
            "security_monitoring": 10,
            "incident_response": 10,
            "business_continuity": 8,
            "security_awareness": 6,
            "compliance": 4,
            "emerging_tech": 4,
            "third_party": 4,
            "risk_management": 2
        },
        "risk_levels": {
            "critical": {"min": 0, "max": 40, "label": "Critical Risk", "color": "#dc2626"},
            "high": {"min": 41, "max": 60, "label": "High Risk", "color": "#ea580c"},
            "medium": {"min": 61, "max": 80, "label": "Medium Risk", "color": "#ca8a04"},
            "low": {"min": 81, "max": 100, "label": "Low Risk", "color": "#16a34a"}
        }
    }

@app.post("/scoring/question")
def score_question(question_data: Dict[str, Any]):
    """Score an individual question"""
    try:
        question_id = question_data.get("question_id", "unknown")
        question_type = question_data.get("question_type", "text")
        answer = question_data.get("answer")
        weight = question_data.get("weight", 10)
        
        # Simple scoring logic
        if question_type == "boolean":
            raw_score = weight if answer else 0
        elif question_type == "scale":
            min_val = question_data.get("min_value", 1)
            max_val = question_data.get("max_value", 5)
            normalized = (float(answer) - min_val) / (max_val - min_val)
            raw_score = normalized * weight
        elif question_type == "select":
            options = question_data.get("question_options", [])
            if answer in options:
                option_index = options.index(answer)
                option_score = option_index / (len(options) - 1) if len(options) > 1 else 1.0
                raw_score = option_score * weight
            else:
                raw_score = 0
        else:
            raw_score = weight if str(answer).strip() else 0
        
        percentage = (raw_score / weight) * 100 if weight > 0 else 0
        
        return {
            "question_id": question_id,
            "raw_score": raw_score,
            "max_score": weight,
            "percentage": round(percentage, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scoring question: {str(e)}")

@app.post("/scoring/section")
def score_section(section_data: Dict[str, Any]):
    """Score a complete section"""
    try:
        section_id = section_data.get("section_id", "unknown")
        responses = section_data.get("responses", {})
        
        total_score = 0
        max_score = 0
        questions_answered = 0
        
        for question_id, answer in responses.items():
            if answer is not None and answer != "":
                questions_answered += 1
                # Simple scoring - each question worth 10 points
                if isinstance(answer, bool):
                    score = 10 if answer else 0
                elif isinstance(answer, (int, float)):
                    score = min(answer * 2, 10)  # Scale to 10
                else:
                    score = 5  # Default for text answers
                
                total_score += score
            max_score += 10
        
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Determine risk level
        if percentage >= 81:
            risk_level = "Low Risk"
        elif percentage >= 61:
            risk_level = "Medium Risk"
        elif percentage >= 41:
            risk_level = "High Risk"
        else:
            risk_level = "Critical Risk"
        
        return {
            "section_id": section_id,
            "section_name": section_id.replace("_", " ").title(),
            "raw_score": total_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "risk_level": risk_level,
            "questions_answered": questions_answered,
            "total_questions": len(responses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scoring section: {str(e)}")

@app.get("/scoring/test")
def test_scoring():
    """Test endpoint to verify scoring is working"""
    # Test question scoring
    test_question = {
        "question_id": "test_001",
        "question_type": "boolean",
        "answer": True,
        "weight": 10
    }
    
    question_result = score_question(test_question)
    
    # Test section scoring
    test_section = {
        "section_id": "governance",
        "responses": {
            "gov_001": True,
            "gov_002": 4,
            "gov_003": "Good"
        }
    }
    
    section_result = score_section(test_section)
    
    return {
        "message": "Scoring system test completed",
        "question_test": question_result,
        "section_test": section_result,
        "status": "working"
    }

def main():
    """Start the server"""
    print("=" * 60)
    print("STARTING RISKAI SCORING SYSTEM")
    print("=" * 60)
    print(f"Current directory: {current_dir}")
    print("Server will start on: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Test endpoint: http://localhost:8000/scoring/test")
    print("=" * 60)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False  # Disable reload to avoid issues
        )
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()