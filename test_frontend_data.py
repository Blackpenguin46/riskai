#!/usr/bin/env python3
"""
Test what data the frontend receives from the assessment API
"""

import sys
sys.path.append('backend')
import json

def test_frontend_data():
    """Test the exact data format the frontend will receive"""
    
    print("🧪 Testing Frontend Data Format")
    print("=" * 50)
    
    # Import required modules
    from assessment.enterprise_assessment_api import submit_enterprise_assessment, AssessmentSubmission, CompanyProfile, AssessmentAnswer
    
    # Create test data similar to what frontend would send
    company_profile = CompanyProfile(
        name="Test Corp",
        industry="healthcare",
        size="medium",
        country="US",
        compliance_requirements=["HIPAA"],
        technology_adoption="medium",
        data_types=["health_records"],
        risk_tolerance="medium"
    )
    
    # Minimal answers to trigger AI recommendations
    answers = [
        AssessmentAnswer(question_id="gov_001", answer="none", section_id="governance"),
        AssessmentAnswer(question_id="gov_002", answer=2, section_id="governance"),
        AssessmentAnswer(question_id="access_001", answer=20, section_id="access_control"),
        AssessmentAnswer(question_id="access_002", answer="never", section_id="access_control"),
        AssessmentAnswer(question_id="data_001", answer=30, section_id="data_protection"),
        AssessmentAnswer(question_id="data_002", answer=False, section_id="data_protection"),
        AssessmentAnswer(question_id="monitor_001", answer=2, section_id="security_monitoring"),
        AssessmentAnswer(question_id="ir_001", answer=1, section_id="incident_response"),
        AssessmentAnswer(question_id="bc_001", answer=False, section_id="business_continuity"),
        AssessmentAnswer(question_id="asset_001", answer=40, section_id="asset_management"),
        AssessmentAnswer(question_id="aware_001", answer="never", section_id="security_awareness"),
        AssessmentAnswer(question_id="aware_002", answer=False, section_id="security_awareness"),
    ]
    
    submission = AssessmentSubmission(
        company_profile=company_profile,
        answers=answers
    )
    
    try:
        result = submit_enterprise_assessment(submission)
        
        print("📊 Assessment Results Summary:")
        print(f"   Overall Score: {result.get('overall_score', 'N/A')}%")
        print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"   Has ai_feedback key: {'ai_feedback' in result}")
        
        # Check AI feedback structure
        ai_feedback = result.get('ai_feedback')
        if ai_feedback:
            print(f"\n🤖 AI Feedback Structure:")
            print(f"   Type: {type(ai_feedback)}")
            print(f"   Keys: {list(ai_feedback.keys()) if isinstance(ai_feedback, dict) else 'Not a dict'}")
            
            if isinstance(ai_feedback, dict):
                print(f"   overall_assessment: '{ai_feedback.get('overall_assessment', 'N/A')[:100]}...'")
                print(f"   key_strengths: {len(ai_feedback.get('key_strengths', []))} items")
                print(f"   critical_gaps: {len(ai_feedback.get('critical_gaps', []))} items")
                print(f"   ai_recommendations: {len(ai_feedback.get('ai_recommendations', []))} items")
                print(f"   industry_comparison: '{ai_feedback.get('industry_comparison', 'N/A')[:100]}...'")
                
                # Check if ai_feedback is truthy for frontend conditionals
                print(f"   ai_feedback is truthy: {bool(ai_feedback)}")
                print(f"   overall_assessment != 'AI feedback temporarily unavailable': {ai_feedback.get('overall_assessment') != 'AI feedback temporarily unavailable'}")
                
                # Show first recommendation
                recommendations = ai_feedback.get('ai_recommendations', [])
                if recommendations:
                    print(f"\n📋 First AI Recommendation:")
                    rec = recommendations[0]
                    print(f"   Title: {rec.get('title', 'N/A')}")
                    print(f"   Priority: {rec.get('priority', 'N/A')}")
                    print(f"   Description: {rec.get('description', 'N/A')[:100]}...")
        else:
            print(f"\n❌ No ai_feedback found in result")
        
        # Save the complete result for frontend debugging
        with open('/Users/samoakes/Desktop/RiskAI/riskai/frontend_test_data.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Complete result saved to frontend_test_data.json for debugging")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_frontend_data()