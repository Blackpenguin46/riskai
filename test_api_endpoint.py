#!/usr/bin/env python3
"""
Test the assessment API endpoint to verify it returns proper results
"""

import requests
import json

def test_assessment_api():
    """Test the full assessment API endpoint"""
    
    print("🧪 Testing Assessment API Endpoint")
    print("=" * 50)
    
    # Sample assessment data
    assessment_data = {
        "company_profile": {
            "name": "Test Healthcare Corp",
            "industry": "healthcare", 
            "size": "medium",
            "country": "US",
            "compliance_requirements": ["HIPAA"],
            "technology_adoption": "medium",
            "data_types": ["health_records"],
            "risk_tolerance": "medium"
        },
        "answers": [
            {"question_id": "gov_001", "answer": "basic", "section_id": "governance"},
            {"question_id": "gov_002", "answer": 5, "section_id": "governance"},
            {"question_id": "gov_003", "answer": "quarterly", "section_id": "governance"},
            {"question_id": "gov_004", "answer": True, "section_id": "governance"},
            {"question_id": "access_001", "answer": 60, "section_id": "access_control"},
            {"question_id": "access_002", "answer": "quarterly", "section_id": "access_control"},
            {"question_id": "access_003", "answer": 5, "section_id": "access_control"},
            {"question_id": "data_001", "answer": 70, "section_id": "data_protection"},
            {"question_id": "data_002", "answer": True, "section_id": "data_protection"},
            {"question_id": "data_005", "answer": 75, "section_id": "data_protection"},
            {"question_id": "monitor_001", "answer": 5, "section_id": "security_monitoring"},
            {"question_id": "monitor_002", "answer": "hours", "section_id": "security_monitoring"},
            {"question_id": "monitor_003", "answer": False, "section_id": "security_monitoring"},
            {"question_id": "ir_001", "answer": 4, "section_id": "incident_response"},
            {"question_id": "ir_002", "answer": "quarterly", "section_id": "incident_response"},
            {"question_id": "ir_003", "answer": "hours", "section_id": "incident_response"},
            {"question_id": "bc_001", "answer": True, "section_id": "business_continuity"},
            {"question_id": "bc_002", "answer": "hours", "section_id": "business_continuity"},
            {"question_id": "asset_001", "answer": 80, "section_id": "asset_management"},
            {"question_id": "asset_002", "answer": "quarterly", "section_id": "asset_management"},
            {"question_id": "aware_001", "answer": "quarterly", "section_id": "security_awareness"},
            {"question_id": "aware_002", "answer": True, "section_id": "security_awareness"}
        ]
    }
    
    try:
        # Make API request
        response = requests.post(
            'http://localhost:8000/api/assessment/enterprise/submit',
            json=assessment_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Request Successful!")
            print(f"   Overall Score: {result.get('overall_score', 'N/A')}%")
            print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"   Questions Answered: {result.get('questions_answered', 'N/A')}")
            print(f"   Section Breakdown: {len(result.get('section_breakdown', []))} sections")
            
            # Check AI feedback
            ai_feedback = result.get('ai_feedback', {})
            if ai_feedback:
                print("\n🤖 AI Feedback Analysis:")
                print(f"   Overall Assessment: {len(ai_feedback.get('overall_assessment', ''))} characters")
                print(f"   Key Strengths: {len(ai_feedback.get('key_strengths', []))} items")
                print(f"   Critical Gaps: {len(ai_feedback.get('critical_gaps', []))} items")
                print(f"   AI Recommendations: {len(ai_feedback.get('ai_recommendations', []))} items")
                print(f"   Industry Comparison: {len(ai_feedback.get('industry_comparison', ''))} characters")
                
                # Show sample recommendations
                recommendations = ai_feedback.get('ai_recommendations', [])
                if recommendations:
                    print("\n📋 Sample AI Recommendations:")
                    for i, rec in enumerate(recommendations[:3]):
                        print(f"   {i+1}. {rec.get('title', 'N/A')} ({rec.get('priority', 'N/A')} priority)")
                else:
                    print("\n❌ No AI recommendations found")
            else:
                print("\n❌ No AI feedback found in response")
            
            # Save full response for debugging
            with open('/Users/samoakes/Desktop/RiskAI/riskai/api_test_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full response saved to api_test_response.json")
            
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - make sure the backend is running on port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_assessment_api()