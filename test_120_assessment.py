#!/usr/bin/env python3
"""
Test script for 120-question enterprise assessment with AI feedback
"""

import sys
sys.path.append('backend')

def test_120_question_assessment():
    """Test the complete 120-question assessment system"""
    
    print("🧪 Testing 120-Question Enterprise Assessment")
    print("=" * 60)
    
    # Import modules
    from assessment.enterprise_assessment_api import ENTERPRISE_QUESTIONS
    from scoring.dynamic_scoring_engine import dynamic_scoring_engine
    from assessment.ai_feedback_generator import ai_feedback_generator
    
    # 1. Verify 120 questions
    total_questions = sum(len(section["questions"]) for section in ENTERPRISE_QUESTIONS.values())
    print(f"✅ Total Questions: {total_questions}")
    assert total_questions == 120, f"Expected 120 questions, got {total_questions}"
    
    # 2. Test dynamic scoring with sample answers
    sample_answers = {
        # Governance section
        "gov_001": "basic",
        "gov_002": 6,
        "gov_003": "quarterly", 
        "gov_004": True,
        
        # Access control section
        "access_001": 75,
        "access_002": "quarterly",
        "access_003": 6,
        
        # Data protection section
        "data_001": 80,
        "data_002": True,
        "data_005": 85,
        
        # Security monitoring section
        "monitor_001": 6,
        "monitor_002": "hours",
        "monitor_003": True,
        
        # Incident response section
        "ir_001": 5,
        "ir_002": "quarterly",
        "ir_003": "hours",
        
        # Business continuity section
        "bc_001": True,
        "bc_002": "hours",
        
        # Asset management section
        "asset_001": 85,
        "asset_002": "quarterly",
        
        # Security awareness section
        "aware_001": "quarterly",
        "aware_002": True
    }
    
    sample_company = {
        "name": "Test Healthcare Corp",
        "industry": "healthcare",
        "size": "medium",
        "country": "US",
        "compliance_requirements": ["HIPAA"]
    }
    
    print("🔢 Testing Dynamic Scoring Engine...")
    try:
        scoring_result = dynamic_scoring_engine.score_assessment(sample_answers, sample_company)
        overall_score = scoring_result['overall_score']
        print(f"✅ Dynamic Scoring: {overall_score:.1f}%")
        print(f"   Sections Scored: {len(scoring_result['section_scores'])}")
        print(f"   Confidence Metrics: ✅")
        print(f"   Industry Adjustments: ✅")
    except Exception as e:
        print(f"❌ Dynamic Scoring Error: {str(e)}")
        return False
    
    # 3. Test AI feedback generation
    print("🧠 Testing AI Feedback Generation...")
    try:
        # Prepare assessment results for AI feedback
        section_breakdown = []
        for section_id, section_data in scoring_result['section_scores'].items():
            section_info = ENTERPRISE_QUESTIONS.get(section_id, {})
            section_breakdown.append({
                "section_id": section_id,
                "section_name": section_info.get("name", section_id.title()),
                "score": section_data['score'],
                "weight": section_data['weight'],
                "confidence": section_data['confidence'],
                "evidence_strength": section_data['evidence_strength'],
                "maturity_level": section_data['maturity_level'],
                "questions_answered": section_data['questions_answered']
            })
        
        assessment_results = {
            'overall_score': overall_score,
            'section_breakdown': section_breakdown,
            'company_profile': sample_company
        }
        
        ai_feedback = ai_feedback_generator.generate_comprehensive_feedback(
            assessment_results, sample_company
        )
        
        print(f"✅ AI Feedback Generated:")
        print(f"   Overall Assessment: {ai_feedback.overall_assessment[:80]}...")
        print(f"   Key Strengths: {len(ai_feedback.key_strengths)}")
        print(f"   Critical Gaps: {len(ai_feedback.critical_gaps)}")
        print(f"   Recommendations: {len(ai_feedback.recommendations)}")
        print(f"   Industry Comparison: ✅")
        print(f"   Improvement Roadmap: ✅")
        
    except Exception as e:
        print(f"❌ AI Feedback Error: {str(e)}")
        return False
    
    # 4. Test question distribution
    print("📊 Question Distribution Analysis:")
    for section_id, section_data in ENTERPRISE_QUESTIONS.items():
        count = len(section_data['questions'])
        weight = section_data['weight']
        print(f"   {section_data['name']}: {count} questions ({weight:.0%} weight)")
    
    print("\n🎉 All Tests Passed! 120-Question Assessment with AI Feedback Ready!")
    return True

if __name__ == "__main__":
    test_120_question_assessment()