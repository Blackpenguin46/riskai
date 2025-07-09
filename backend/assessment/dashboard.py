"""
Assessment Dashboard

Provides a unified dashboard interface for navigating between assessment sections
with clickable cards, progress tracking, and completion status indicators.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from .structured_assessment import structured_assessment

logger = logging.getLogger(__name__)

@dataclass
class SectionCard:
    """Assessment section card for dashboard"""
    id: str
    title: str
    description: str
    icon: str
    estimated_time: str
    questions_count: int
    completion_status: str  # 'not_started', 'in_progress', 'completed'
    completion_percentage: float
    framework_coverage: List[str]
    priority: str  # 'high', 'medium', 'low'
    order: int

@dataclass
class DashboardProgress:
    """Overall assessment progress"""
    total_sections: int
    completed_sections: int
    in_progress_sections: int
    overall_completion: float
    estimated_time_remaining: str
    last_updated: datetime

class AssessmentDashboard:
    """Dashboard for assessment navigation and progress tracking"""
    
    def __init__(self):
        self.section_progress: Dict[str, Dict[str, Any]] = {}
        self.section_cards = self._initialize_section_cards()
        
    def _initialize_section_cards(self) -> List[SectionCard]:
        """Initialize section cards with metadata"""
        
        cards = [
            SectionCard(
                id="company_profile",
                title="Company Profile & Context",
                description="Basic company information, industry context, and regulatory requirements",
                icon="🏢",
                estimated_time="5-10 minutes",
                questions_count=6,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF", "ISO 27001", "CIS Controls"],
                priority="high",
                order=1
            ),
            SectionCard(
                id="governance",
                title="Governance & Risk Management",
                description="Board oversight, cybersecurity policies, and risk assessment processes",
                icon="⚖️",
                estimated_time="10-15 minutes",
                questions_count=8,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF ID.GV", "ISO 27001 A.5", "CIS Controls 1"],
                priority="high",
                order=2
            ),
            SectionCard(
                id="asset_management",
                title="Asset Management",
                description="Hardware/software inventory, asset classification, and lifecycle management",
                icon="💾",
                estimated_time="8-12 minutes",
                questions_count=5,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF ID.AM", "ISO 27001 A.8", "CIS Controls 1,2"],
                priority="high",
                order=3
            ),
            SectionCard(
                id="data_protection",
                title="Data Protection",
                description="Data encryption, backup systems, and data loss prevention measures",
                icon="🔒",
                estimated_time="10-15 minutes",
                questions_count=7,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF PR.DS", "ISO 27001 A.10", "CIS Controls 3,13"],
                priority="high",
                order=4
            ),
            SectionCard(
                id="access_control",
                title="Access Control",
                description="Multi-factor authentication, privileged access, and access reviews",
                icon="🔑",
                estimated_time="12-18 minutes",
                questions_count=8,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF PR.AC", "ISO 27001 A.9", "CIS Controls 5,6"],
                priority="high",
                order=5
            ),
            SectionCard(
                id="security_monitoring",
                title="Security Monitoring",
                description="Logging, SIEM systems, and threat detection capabilities",
                icon="👁️",
                estimated_time="10-15 minutes",
                questions_count=6,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF DE.AE", "ISO 27001 A.12", "CIS Controls 6,8"],
                priority="medium",
                order=6
            ),
            SectionCard(
                id="incident_response",
                title="Incident Response",
                description="Incident response plans, teams, and testing procedures",
                icon="🚨",
                estimated_time="8-12 minutes",
                questions_count=5,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF RS.RP", "ISO 27001 A.16", "CIS Controls 17,19"],
                priority="medium",
                order=7
            ),
            SectionCard(
                id="business_continuity",
                title="Business Continuity",
                description="Disaster recovery plans, backup testing, and continuity procedures",
                icon="🔄",
                estimated_time="8-12 minutes",
                questions_count=4,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF RC.RP", "ISO 27001 A.17", "CIS Controls 11"],
                priority="medium",
                order=8
            ),
            SectionCard(
                id="security_awareness",
                title="Security Awareness",
                description="Training programs, phishing simulations, and security culture",
                icon="🎓",
                estimated_time="6-10 minutes",
                questions_count=4,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST CSF PR.AT", "ISO 27001 A.7", "CIS Controls 14"],
                priority="medium",
                order=9
            ),
            SectionCard(
                id="emerging_technology",
                title="Emerging Technology",
                description="AI governance, cloud security, and IoT device management",
                icon="🚀",
                estimated_time="8-12 minutes",
                questions_count=5,
                completion_status="not_started",
                completion_percentage=0.0,
                framework_coverage=["NIST AI RMF", "ISO 27001 A.14", "CIS Controls 12,15"],
                priority="low",
                order=10
            )
        ]
        
        return sorted(cards, key=lambda x: x.order)
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get complete dashboard overview with all sections"""
        
        # Calculate overall progress
        progress = self._calculate_overall_progress()
        
        return {
            "dashboard_info": {
                "title": "Cybersecurity Risk Assessment",
                "subtitle": "Complete structured assessment based on industry frameworks",
                "total_sections": len(self.section_cards),
                "estimated_total_time": "70-130 minutes",
                "frameworks_covered": ["NIST CSF", "ISO 27001", "CIS Controls", "NIST AI RMF"]
            },
            "progress": asdict(progress),
            "section_cards": [asdict(card) for card in self.section_cards],
            "quick_actions": [
                {
                    "id": "continue_assessment",
                    "title": "Continue Assessment",
                    "description": "Resume from where you left off",
                    "icon": "▶️",
                    "enabled": progress.in_progress_sections > 0
                },
                {
                    "id": "start_new_assessment",
                    "title": "Start New Assessment",
                    "description": "Begin a fresh assessment",
                    "icon": "🆕",
                    "enabled": True
                },
                {
                    "id": "view_results",
                    "title": "View Results",
                    "description": "Review completed assessment results",
                    "icon": "📊",
                    "enabled": progress.completed_sections > 0
                },
                {
                    "id": "export_report",
                    "title": "Export Report",
                    "description": "Download assessment report",
                    "icon": "📄",
                    "enabled": progress.overall_completion >= 100
                }
            ],
            "priority_sections": [
                card for card in self.section_cards 
                if card.priority == "high" and card.completion_status != "completed"
            ][:3]  # Top 3 high priority incomplete sections
        }
    
    def get_section_details(self, section_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific section"""
        
        # Find the section card
        section_card = None
        for card in self.section_cards:
            if card.id == section_id:
                section_card = card
                break
        
        if not section_card:
            return {"error": "Section not found"}
        
        # Get section questions from structured assessment
        section_questions = structured_assessment.get_section_questions(section_id)
        
        return {
            "section_info": asdict(section_card),
            "questions": section_questions,
            "navigation": {
                "previous_section": self._get_previous_section(section_id),
                "next_section": self._get_next_section(section_id),
                "section_index": section_card.order,
                "total_sections": len(self.section_cards)
            },
            "framework_details": self._get_framework_details(section_card.framework_coverage),
            "completion_guide": {
                "required_questions": len([q for q in section_questions if q.get("required", False)]),
                "total_questions": len(section_questions),
                "estimated_time": section_card.estimated_time,
                "tips": [
                    "Answer all required questions marked with *",
                    "Use the help text if you need clarification",
                    "You can save progress and return later",
                    "Consider your current maturity level when answering"
                ]
            }
        }
    
    def update_section_progress(self, section_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Update progress for a specific section"""
        
        # Find the section card
        section_card = None
        card_index = None
        for i, card in enumerate(self.section_cards):
            if card.id == section_id:
                section_card = card
                card_index = i
                break
        
        if not section_card:
            return {"error": "Section not found"}
        
        # Get section questions to calculate completion
        section_questions = structured_assessment.get_section_questions(section_id)
        
        # Calculate completion percentage
        total_questions = len(section_questions)
        answered_questions = len([q for q in section_questions if q.get("id") in answers])
        required_questions = len([q for q in section_questions if q.get("required", False)])
        answered_required = len([q for q in section_questions if q.get("required", False) and q.get("id") in answers])
        
        completion_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        # Determine completion status
        if completion_percentage == 100 and answered_required == required_questions:
            completion_status = "completed"
        elif answered_questions > 0:
            completion_status = "in_progress"
        else:
            completion_status = "not_started"
        
        # Update section card
        self.section_cards[card_index].completion_status = completion_status
        self.section_cards[card_index].completion_percentage = completion_percentage
        
        # Store progress data
        self.section_progress[section_id] = {
            "answers": answers,
            "completion_percentage": completion_percentage,
            "completion_status": completion_status,
            "last_updated": datetime.now().isoformat(),
            "answered_questions": answered_questions,
            "total_questions": total_questions,
            "answered_required": answered_required,
            "required_questions": required_questions
        }
        
        return {
            "section_id": section_id,
            "completion_percentage": completion_percentage,
            "completion_status": completion_status,
            "answered_questions": answered_questions,
            "total_questions": total_questions,
            "next_action": self._get_next_action(completion_status, section_id)
        }
    
    def _calculate_overall_progress(self) -> DashboardProgress:
        """Calculate overall assessment progress"""
        
        total_sections = len(self.section_cards)
        completed_sections = len([card for card in self.section_cards if card.completion_status == "completed"])
        in_progress_sections = len([card for card in self.section_cards if card.completion_status == "in_progress"])
        
        overall_completion = (completed_sections / total_sections) * 100 if total_sections > 0 else 0
        
        # Calculate estimated time remaining
        remaining_sections = [card for card in self.section_cards if card.completion_status != "completed"]
        estimated_minutes = sum([self._parse_time_estimate(card.estimated_time) for card in remaining_sections])
        
        if estimated_minutes < 60:
            estimated_time_remaining = f"{estimated_minutes} minutes"
        else:
            hours = estimated_minutes // 60
            minutes = estimated_minutes % 60
            estimated_time_remaining = f"{hours}h {minutes}m"
        
        return DashboardProgress(
            total_sections=total_sections,
            completed_sections=completed_sections,
            in_progress_sections=in_progress_sections,
            overall_completion=overall_completion,
            estimated_time_remaining=estimated_time_remaining,
            last_updated=datetime.now()
        )
    
    def _get_previous_section(self, section_id: str) -> Optional[str]:
        """Get previous section ID"""
        
        current_order = None
        for card in self.section_cards:
            if card.id == section_id:
                current_order = card.order
                break
        
        if current_order and current_order > 1:
            for card in self.section_cards:
                if card.order == current_order - 1:
                    return card.id
        
        return None
    
    def _get_next_section(self, section_id: str) -> Optional[str]:
        """Get next section ID"""
        
        current_order = None
        for card in self.section_cards:
            if card.id == section_id:
                current_order = card.order
                break
        
        if current_order and current_order < len(self.section_cards):
            for card in self.section_cards:
                if card.order == current_order + 1:
                    return card.id
        
        return None
    
    def _get_framework_details(self, framework_coverage: List[str]) -> List[Dict[str, Any]]:
        """Get detailed framework information"""
        
        framework_details = {
            "NIST CSF": {
                "name": "NIST Cybersecurity Framework",
                "description": "Risk-based approach to cybersecurity",
                "url": "https://www.nist.gov/cyberframework"
            },
            "ISO 27001": {
                "name": "ISO/IEC 27001",
                "description": "Information security management standard",
                "url": "https://www.iso.org/isoiec-27001-information-security.html"
            },
            "CIS Controls": {
                "name": "CIS Critical Security Controls",
                "description": "Prioritized set of actions for cybersecurity",
                "url": "https://www.cisecurity.org/controls"
            },
            "NIST AI RMF": {
                "name": "NIST AI Risk Management Framework",
                "description": "Framework for managing AI risks",
                "url": "https://www.nist.gov/itl/ai-risk-management-framework"
            }
        }
        
        return [
            {
                "id": framework,
                **framework_details.get(framework, {"name": framework, "description": "", "url": ""})
            }
            for framework in framework_coverage
        ]
    
    def _parse_time_estimate(self, time_estimate: str) -> int:
        """Parse time estimate string to minutes"""
        
        import re
        
        # Extract numbers from time estimate (e.g., "5-10 minutes" -> 7.5)
        numbers = re.findall(r'\d+', time_estimate)
        if len(numbers) >= 2:
            return int((int(numbers[0]) + int(numbers[1])) / 2)
        elif len(numbers) == 1:
            return int(numbers[0])
        else:
            return 10  # Default estimate
    
    def _get_next_action(self, completion_status: str, section_id: str) -> Dict[str, Any]:
        """Get suggested next action based on completion status"""
        
        if completion_status == "completed":
            next_section = self._get_next_section(section_id)
            if next_section:
                return {
                    "action": "next_section",
                    "message": "Section completed! Continue to next section.",
                    "section_id": next_section
                }
            else:
                return {
                    "action": "view_results",
                    "message": "Assessment completed! View your results.",
                    "section_id": None
                }
        
        elif completion_status == "in_progress":
            return {
                "action": "complete_section",
                "message": "Continue answering questions in this section.",
                "section_id": section_id
            }
        
        else:
            return {
                "action": "start_section",
                "message": "Start this section by answering the first question.",
                "section_id": section_id
            }
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get assessment summary with all section results"""
        
        summary = {
            "assessment_id": f"assessment_{int(datetime.now().timestamp())}",
            "completed_at": datetime.now().isoformat(),
            "overall_progress": asdict(self._calculate_overall_progress()),
            "section_results": [],
            "recommendations": [],
            "next_steps": []
        }
        
        for card in self.section_cards:
            section_progress = self.section_progress.get(card.id, {})
            
            section_result = {
                "section_id": card.id,
                "section_title": card.title,
                "completion_status": card.completion_status,
                "completion_percentage": card.completion_percentage,
                "framework_coverage": card.framework_coverage,
                "priority": card.priority,
                "answered_questions": section_progress.get("answered_questions", 0),
                "total_questions": card.questions_count
            }
            
            summary["section_results"].append(section_result)
        
        return summary

# Global instance
assessment_dashboard = AssessmentDashboard()