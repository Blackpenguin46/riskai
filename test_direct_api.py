#!/usr/bin/env python3
"""
Test the assessment API directly without HTTP server
"""

import sys
sys.path.append('backend')

def test_assessment_direct():
    """Test assessment submission directly"""
    
    print("🧪 Testing Assessment Submission Directly")
    print("=" * 50)
    
    # Import required modules
    from assessment.enterprise_assessment_api import submit_enterprise_assessment, AssessmentSubmission, CompanyProfile, AssessmentAnswer
    
    # Create test data
    company_profile = CompanyProfile(
        name="Test Healthcare Corp",
        industry="healthcare",
        size="medium",
        country="US",
        compliance_requirements=["HIPAA"],
        technology_adoption="medium",
        data_types=["health_records"],
        risk_tolerance="medium"
    )
    
    answers = [
        AssessmentAnswer(question_id="gov_001", answer="basic", section_id="governance"),
        AssessmentAnswer(question_id="gov_002", answer=5, section_id="governance"),
        AssessmentAnswer(question_id="gov_003", answer="quarterly", section_id="governance"),
        AssessmentAnswer(question_id="gov_004", answer=True, section_id="governance"),
        AssessmentAnswer(question_id="access_001", answer=60, section_id="access_control"),
        AssessmentAnswer(question_id="access_002", answer="quarterly", section_id="access_control"),
        AssessmentAnswer(question_id="access_003", answer=5, section_id="access_control"),
        AssessmentAnswer(question_id="data_001", answer=70, section_id="data_protection"),
        AssessmentAnswer(question_id="data_002", answer=True, section_id="data_protection"),
        AssessmentAnswer(question_id="data_005", answer=75, section_id="data_protection"),
        AssessmentAnswer(question_id="monitor_001", answer=5, section_id="security_monitoring"),
        AssessmentAnswer(question_id="monitor_002", answer="hours", section_id="security_monitoring"),
        AssessmentAnswer(question_id="monitor_003", answer=False, section_id="security_monitoring"),
        AssessmentAnswer(question_id="ir_001", answer=4, section_id="incident_response"),
        AssessmentAnswer(question_id="ir_002", answer="quarterly", section_id="incident_response"),
        AssessmentAnswer(question_id="ir_003", answer="hours", section_id="incident_response"),
        AssessmentAnswer(question_id="bc_001", answer=True, section_id="business_continuity"),
        AssessmentAnswer(question_id="bc_002", answer="hours", section_id="business_continuity"),
        AssessmentAnswer(question_id="asset_001", answer=80, section_id="asset_management"),
        AssessmentAnswer(question_id="asset_002", answer="quarterly", section_id="asset_management"),
        AssessmentAnswer(question_id="aware_001", answer="quarterly", section_id="security_awareness"),
        AssessmentAnswer(question_id="aware_002", answer=True, section_id="security_awareness"),
    ]
    
    submission = AssessmentSubmission(
        company_profile=company_profile,
        answers=answers
    )
    
    try:
        print("🔄 Submitting assessment...")
        result = submit_enterprise_assessment(submission)
        
        print("✅ Assessment Submitted Successfully!")
        print(f"   Overall Score: {result.get('overall_score', 'N/A')}%")
        print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"   Questions Answered: {result.get('questions_answered', 'N/A')}")
        print(f"   Section Breakdown: {len(result.get('section_breakdown', []))} sections")
        
        # Check AI feedback
        ai_feedback = result.get('ai_feedback', {})
        if ai_feedback and ai_feedback.get('overall_assessment') != "AI feedback temporarily unavailable":
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
                print(f"\n✅ Found {len(recommendations)} total AI recommendations!")
            else:
                print("\n❌ No AI recommendations found")
        else:
            print(f"\n❌ AI feedback not available: {ai_feedback.get('overall_assessment', 'Unknown')}")
        
        # Check section breakdown
        sections = result.get('section_breakdown', [])
        if sections:
            print(f"\n📊 Section Scores:")
            for section in sections:
                print(f"   {section.get('section_name', 'Unknown')}: {section.get('score', 0)}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_assessment_direct()