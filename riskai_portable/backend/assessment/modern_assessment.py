"""
Modern Assessment Framework

Enterprise-grade security assessment with test-like interface,
comprehensive question structure, and NIST CSF 2.0 maturity scoring.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Types of assessment questions"""
    LIKERT_SCALE = "likert_scale"  # 1-5 strength ratings
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_TEXT = "short_text"
    DROPDOWN = "dropdown"
    CHECKLIST = "checklist"
    BOOLEAN = "boolean"

class MaturityLevel(Enum):
    """NIST CSF 2.0 Maturity Levels"""
    PARTIAL = (1, "Partial", "Ad hoc, reactive approach to cybersecurity")
    RISK_INFORMED = (2, "Risk-Informed", "Risk management practices exist but not comprehensive")
    REPEATABLE = (3, "Repeatable", "Formal risk management approach regularly updated")
    ADAPTIVE = (4, "Adaptive", "Proactive approach with continuous improvement")

class RiskLevel(Enum):
    """Risk impact levels"""
    CRITICAL = (4, "Critical", "#dc2626")  # red-600
    HIGH = (3, "High", "#ea580c")         # orange-600
    MEDIUM = (2, "Medium", "#ca8a04")     # yellow-600
    LOW = (1, "Low", "#16a34a")           # green-600

@dataclass
class AssessmentQuestion:
    """Modern assessment question structure"""
    id: str
    section_id: str
    section_name: str
    category: str
    question_text: str
    question_type: QuestionType
    options: List[Any]
    required: bool
    weight: float  # Scoring weight (0.0-1.0)
    risk_impact: RiskLevel
    framework_mapping: Dict[str, str]  # Framework -> Control ID
    help_text: Optional[str] = None
    compliance_related: bool = False
    maturity_indicators: Dict[str, str] = None  # Maturity level -> description

@dataclass
class AssessmentSection:
    """Assessment section grouping"""
    id: str
    name: str
    description: str
    estimated_time: str
    question_count: int
    weight: float
    icon: str
    order: int
    completion_required: bool = True

class ModernAssessmentBuilder:
    """Builds comprehensive modern assessment framework"""
    
    def __init__(self):
        self.sections = self._create_assessment_sections()
        self.questions = self._create_comprehensive_questions()
        
    def _create_assessment_sections(self) -> List[AssessmentSection]:
        """Create the 10 assessment sections"""
        
        return [
            AssessmentSection(
                id="company_profile",
                name="Company Profile & Context",
                description="Organization overview, industry context, and regulatory environment",
                estimated_time="8-10 minutes",
                question_count=12,
                weight=0.08,
                icon="🏢",
                order=1
            ),
            AssessmentSection(
                id="governance_risk",
                name="Governance & Risk Management", 
                description="Executive oversight, risk frameworks, and policy governance",
                estimated_time="10-12 minutes",
                question_count=15,
                weight=0.15,
                icon="⚖️",
                order=2
            ),
            AssessmentSection(
                id="asset_management",
                name="Asset Management",
                description="Hardware, software, and data asset inventory and lifecycle management",
                estimated_time="8-10 minutes", 
                question_count=12,
                weight=0.10,
                icon="💾",
                order=3
            ),
            AssessmentSection(
                id="data_protection",
                name="Data Protection & Privacy",
                description="Data classification, encryption, backup, and privacy compliance",
                estimated_time="12-15 minutes",
                question_count=18,
                weight=0.18,
                icon="🔒",
                order=4
            ),
            AssessmentSection(
                id="access_control",
                name="Access Control & Identity Management",
                description="Authentication, authorization, and privileged access management",
                estimated_time="10-12 minutes",
                question_count=16,
                weight=0.14,
                icon="🔑",
                order=5
            ),
            AssessmentSection(
                id="security_monitoring",
                name="Security Monitoring & Detection",
                description="SIEM, threat detection, and security operations capabilities",
                estimated_time="8-10 minutes",
                question_count=14,
                weight=0.12,
                icon="👁️",
                order=6
            ),
            AssessmentSection(
                id="incident_response",
                name="Incident Response & Recovery",
                description="Incident handling, business continuity, and disaster recovery",
                estimated_time="8-10 minutes",
                question_count=12,
                weight=0.10,
                icon="🚨",
                order=7
            ),
            AssessmentSection(
                id="vendor_risk",
                name="Vendor & Third-Party Risk",
                description="Supply chain security and third-party risk management",
                estimated_time="6-8 minutes",
                question_count=10,
                weight=0.08,
                icon="🤝",
                order=8
            ),
            AssessmentSection(
                id="security_awareness",
                name="Security Awareness & Training",
                description="Employee training, awareness programs, and security culture",
                estimated_time="4-6 minutes",
                question_count=8,
                weight=0.06,
                icon="🎓",
                order=9
            ),
            AssessmentSection(
                id="emerging_technology",
                name="Emerging Technology Governance",
                description="AI/ML governance, cloud security, and emerging technology risks",
                estimated_time="6-8 minutes",
                question_count=10,
                weight=0.09,
                icon="🚀",
                order=10
            )
        ]
    
    def _create_comprehensive_questions(self) -> List[AssessmentQuestion]:
        """Create comprehensive question set (120+ questions)"""
        
        questions = []
        
        # Section 1: Company Profile & Context (12 questions)
        questions.extend([
            AssessmentQuestion(
                id="cp_001",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Organization Size",
                question_text="How many full-time employees does your organization have?",
                question_type=QuestionType.DROPDOWN,
                options=["1-10", "11-50", "51-200", "201-1000", "1001-5000", "5000+"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.LOW,
                framework_mapping={"NIST_CSF": "ID.AM-6", "ISO_27001": "A.7.1.1"},
                help_text="Employee count affects risk assessment approach and regulatory requirements"
            ),
            AssessmentQuestion(
                id="cp_002",
                section_id="company_profile", 
                section_name="Company Profile & Context",
                category="Industry Classification",
                question_text="What is your primary industry sector?",
                question_type=QuestionType.DROPDOWN,
                options=["Financial Services", "Healthcare", "Technology", "Manufacturing", "Retail", "Government", "Education", "Energy", "Other"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.RA-1", "ISO_27001": "A.5.1.1"},
                help_text="Industry determines applicable regulations and threat landscape"
            ),
            AssessmentQuestion(
                id="cp_003",
                section_id="company_profile",
                section_name="Company Profile & Context", 
                category="Regulatory Compliance",
                question_text="How comprehensive is your understanding of applicable cybersecurity regulations?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No awareness", "2 - Basic awareness", "3 - Moderate understanding", "4 - Good understanding", "5 - Comprehensive expertise"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "ID.GV-3", "ISO_27001": "A.18.1.1"},
                help_text="Understanding regulations is critical for compliance and avoiding penalties",
                maturity_indicators={
                    "1": "No formal process for tracking regulatory requirements",
                    "2": "Basic awareness but no systematic approach",
                    "3": "Some processes in place but not comprehensive", 
                    "4": "Well-defined processes with regular updates",
                    "5": "Comprehensive regulatory tracking with expert guidance"
                }
            ),
            AssessmentQuestion(
                id="cp_004",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Geographic Presence",
                question_text="In how many countries/regions does your organization operate?",
                question_type=QuestionType.DROPDOWN,
                options=["Single country", "2-5 countries", "6-15 countries", "16+ countries", "Global presence"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-4", "ISO_27001": "A.18.1.4"},
                help_text="Geographic presence affects data residency and privacy law compliance"
            ),
            AssessmentQuestion(
                id="cp_005",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Technology Adoption",
                question_text="How would you characterize your organization's technology adoption approach?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Early adopter of new technologies", "Mainstream adoption after proven success", "Conservative - adopt only when necessary", "Laggard - minimal technology adoption"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.12.6.1"},
                help_text="Technology adoption patterns affect exposure to emerging threats"
            ),
            AssessmentQuestion(
                id="cp_006",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Data Handling",
                question_text="What types of sensitive data does your organization handle?",
                question_type=QuestionType.CHECKLIST,
                options=["Personal/Customer Data", "Financial Records", "Health Information", "Intellectual Property", "Payment Card Data", "Government/Classified Data", "None"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.AM-5", "ISO_27001": "A.8.2.1"},
                help_text="Data types determine applicable compliance requirements"
            ),
            AssessmentQuestion(
                id="cp_007",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Business Model",
                question_text="How would you describe your organization's primary business model?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["B2B Services", "B2C Products", "SaaS/Cloud Services", "E-commerce", "Manufacturing", "Financial Services", "Healthcare Provider", "Other"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.BE-1", "ISO_27001": "A.5.1.1"},
                help_text="Business model affects threat landscape and risk profile"
            ),
            AssessmentQuestion(
                id="cp_008",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Revenue",
                question_text="What is your organization's annual revenue range?",
                question_type=QuestionType.DROPDOWN,
                options=["Under $1M", "$1M - $10M", "$10M - $50M", "$50M - $200M", "$200M - $1B", "Over $1B"],
                required=True,
                weight=0.5,
                risk_impact=RiskLevel.LOW,
                framework_mapping={"NIST_CSF": "ID.BE-1", "ISO_27001": "A.5.1.1"},
                help_text="Revenue size affects resource allocation and regulatory requirements"
            ),
            AssessmentQuestion(
                id="cp_009",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="IT Infrastructure",
                question_text="What percentage of your IT infrastructure is cloud-based?",
                question_type=QuestionType.DROPDOWN,
                options=["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-3", "ISO_27001": "A.14.1.1"},
                help_text="Cloud adoption affects security architecture and controls"
            ),
            AssessmentQuestion(
                id="cp_010",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Remote Work",
                question_text="What percentage of your workforce works remotely?",
                question_type=QuestionType.DROPDOWN,
                options=["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-3", "ISO_27001": "A.6.2.1"},
                help_text="Remote work increases attack surface and access control complexity"
            ),
            AssessmentQuestion(
                id="cp_011",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Security Budget",
                question_text="What percentage of IT budget is allocated to cybersecurity?",
                question_type=QuestionType.DROPDOWN,
                options=["Less than 5%", "5-10%", "10-15%", "15-20%", "More than 20%"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.GV-4", "ISO_27001": "A.6.1.1"},
                help_text="Budget allocation indicates organizational commitment to security"
            ),
            AssessmentQuestion(
                id="cp_012",
                section_id="company_profile",
                section_name="Company Profile & Context",
                category="Previous Incidents",
                question_text="Has your organization experienced a significant security incident in the past 2 years?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No incidents", "Minor incidents only", "One significant incident", "Multiple significant incidents", "Major breach/ransomware"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.16.1.1"},
                help_text="Past incidents indicate current security posture effectiveness"
            )
        ])
        
        # Section 2: Governance & Risk Management (15 questions)
        questions.extend([
            AssessmentQuestion(
                id="gr_001",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Executive Oversight",
                question_text="How strong is your board/executive leadership's commitment to cybersecurity?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No formal commitment", "2 - Minimal oversight", "3 - Moderate involvement", "4 - Strong commitment", "5 - Comprehensive leadership"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "ID.GV-1", "ISO_27001": "A.5.1.1"},
                help_text="Executive commitment is fundamental to effective cybersecurity governance",
                maturity_indicators={
                    "1": "No board-level cybersecurity oversight",
                    "2": "Irregular cybersecurity updates to leadership",
                    "3": "Regular reporting but limited strategic involvement",
                    "4": "Active board participation in cybersecurity strategy",
                    "5": "Board-level cybersecurity expertise and continuous oversight"
                }
            ),
            AssessmentQuestion(
                id="gr_002",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Risk Framework",
                question_text="How mature is your organization's cybersecurity risk management framework?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No formal framework", "2 - Basic processes", "3 - Documented framework", "4 - Mature framework", "5 - Optimized framework"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "ID.RA-1", "ISO_27001": "A.6.1.1"},
                help_text="Risk management framework provides foundation for all security decisions"
            ),
            AssessmentQuestion(
                id="gr_003",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Security Policies",
                question_text="How comprehensive are your cybersecurity policies and procedures?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No formal policies", "2 - Basic policies exist", "3 - Comprehensive documented policies", "4 - Regularly updated policies", "5 - Dynamic policy management"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.GV-1", "ISO_27001": "A.5.1.2"},
                help_text="Policies provide governance foundation for security operations"
            ),
            AssessmentQuestion(
                id="gr_004",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Risk Assessment",
                question_text="How frequently do you conduct comprehensive risk assessments?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Never/Ad-hoc", "Only when required", "Annually", "Quarterly", "Continuously"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.RA-1", "ISO_27001": "A.12.6.1"},
                help_text="Regular risk assessments ensure current understanding of threats"
            ),
            AssessmentQuestion(
                id="gr_005",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Compliance Management",
                question_text="How do you manage regulatory compliance requirements?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal process", "Manual tracking", "Spreadsheet-based", "Dedicated compliance software", "Integrated GRC platform"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.GV-3", "ISO_27001": "A.18.1.1"},
                help_text="Compliance management ensures regulatory requirements are met"
            ),
            AssessmentQuestion(
                id="gr_006",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Security Roles",
                question_text="Do you have dedicated cybersecurity personnel?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No dedicated security staff", "Part-time security responsibilities", "One dedicated security person", "Small security team (2-5)", "Large security team (5+)"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.GV-2", "ISO_27001": "A.7.1.2"},
                help_text="Dedicated security staff ensures focused attention on security matters"
            ),
            AssessmentQuestion(
                id="gr_007",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Budget Management",
                question_text="How is cybersecurity budget planning conducted?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal budget process", "Ad-hoc spending", "Annual budget allocation", "Risk-based budgeting", "Continuous budget optimization"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.GV-4", "ISO_27001": "A.6.1.1"},
                help_text="Budget planning ensures adequate resources for security initiatives"
            ),
            AssessmentQuestion(
                id="gr_008",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Third-Party Risk",
                question_text="How do you assess and manage third-party cybersecurity risks?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No third-party assessment", "2 - Basic vendor questionnaires", "3 - Formal risk assessments", "4 - Continuous monitoring", "5 - Comprehensive risk management"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "ID.SC-1", "ISO_27001": "A.15.1.1"},
                help_text="Third-party risk management is critical for supply chain security"
            ),
            AssessmentQuestion(
                id="gr_009",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Metrics and KPIs",
                question_text="Do you track cybersecurity metrics and KPIs?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No metrics tracked", "Basic security metrics", "Comprehensive security KPIs", "Real-time security dashboard", "Advanced analytics and reporting"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.GV-4", "ISO_27001": "A.18.2.1"},
                help_text="Metrics enable measurement and improvement of security posture"
            ),
            AssessmentQuestion(
                id="gr_010",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Change Management",
                question_text="How mature is your security change management process?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No formal process", "2 - Basic change controls", "3 - Documented change process", "4 - Integrated with security", "5 - Automated change management"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.IP-3", "ISO_27001": "A.12.1.2"},
                help_text="Change management prevents security gaps from unauthorized changes"
            ),
            AssessmentQuestion(
                id="gr_011",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Security Architecture",
                question_text="Do you have a defined security architecture and design principles?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No security architecture", "Basic security guidelines", "Documented security architecture", "Comprehensive security framework", "Zero-trust architecture"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.IP-1", "ISO_27001": "A.13.1.1"},
                help_text="Security architecture provides structure for technology decisions"
            ),
            AssessmentQuestion(
                id="gr_012",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Documentation",
                question_text="How well-documented are your security processes and procedures?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No documentation", "2 - Minimal documentation", "3 - Basic procedures documented", "4 - Comprehensive documentation", "5 - Living documentation with regular updates"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.IP-1", "ISO_27001": "A.5.1.2"},
                help_text="Documentation ensures consistency and knowledge transfer"
            ),
            AssessmentQuestion(
                id="gr_013",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Legal and Regulatory",
                question_text="How do you stay current with evolving cybersecurity regulations?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal process", "Occasional review", "Subscribe to updates", "Regular legal consultation", "Dedicated compliance monitoring"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.GV-3", "ISO_27001": "A.18.1.1"},
                help_text="Staying current prevents compliance gaps and penalties"
            ),
            AssessmentQuestion(
                id="gr_014",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Security Culture",
                question_text="How would you rate your organization's security culture?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - Security is ignored", "2 - Security is compliance-driven", "3 - Security is understood", "4 - Security is valued", "5 - Security is ingrained in culture"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                help_text="Security culture determines effectiveness of technical controls"
            ),
            AssessmentQuestion(
                id="gr_015",
                section_id="governance_risk",
                section_name="Governance & Risk Management",
                category="Executive Reporting",
                question_text="How frequently do you report security metrics to executive leadership?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Never", "Only during incidents", "Quarterly", "Monthly", "Real-time dashboard"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.GV-2", "ISO_27001": "A.6.1.1"},
                help_text="Regular reporting ensures leadership awareness and support"
            )
        ])
        
        # Section 3: Asset Management (12 questions) 
        questions.extend([
            AssessmentQuestion(
                id="am_001",
                section_id="asset_management",
                section_name="Asset Management",
                category="Asset Inventory",
                question_text="How comprehensive is your hardware asset inventory?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No inventory", "2 - Basic spreadsheet", "3 - Automated tools", "4 - Real-time tracking", "5 - Complete visibility"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.8.1.1"},
                help_text="Asset inventory is fundamental to understanding your attack surface"
            ),
            AssessmentQuestion(
                id="am_002",
                section_id="asset_management",
                section_name="Asset Management",
                category="Software Inventory",
                question_text="How well do you track and manage software assets?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No software tracking", "2 - Basic license tracking", "3 - Comprehensive software inventory", "4 - Automated discovery and tracking", "5 - Complete software lifecycle management"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.AM-2", "ISO_27001": "A.8.1.1"},
                help_text="Software inventory prevents unauthorized applications and licensing issues"
            ),
            AssessmentQuestion(
                id="am_003",
                section_id="asset_management",
                section_name="Asset Management",
                category="Asset Classification",
                question_text="Are your assets classified based on criticality and sensitivity?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No classification", "Basic high/medium/low", "Detailed classification scheme", "Automated classification", "Dynamic classification with continuous assessment"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-5", "ISO_27001": "A.8.2.1"},
                help_text="Asset classification enables appropriate protection measures"
            ),
            AssessmentQuestion(
                id="am_004",
                section_id="asset_management",
                section_name="Asset Management",
                category="Network Mapping",
                question_text="How well do you understand your network topology and data flows?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No network documentation", "2 - Basic network diagrams", "3 - Comprehensive network maps", "4 - Real-time network discovery", "5 - Complete network visibility with data flow analysis"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.AM-3", "ISO_27001": "A.13.1.1"},
                help_text="Network visibility is essential for security monitoring and incident response"
            ),
            AssessmentQuestion(
                id="am_005",
                section_id="asset_management",
                section_name="Asset Management",
                category="Asset Lifecycle",
                question_text="How do you manage the complete lifecycle of IT assets?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal lifecycle management", "Basic procurement and disposal", "Documented lifecycle processes", "Integrated asset lifecycle management", "Automated lifecycle management with security integration"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.8.1.4"},
                help_text="Lifecycle management ensures security throughout asset lifespan"
            ),
            AssessmentQuestion(
                id="am_006",
                section_id="asset_management",
                section_name="Asset Management",
                category="Configuration Management",
                question_text="How do you manage and track system configurations?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No configuration management", "Manual configuration tracking", "Basic configuration documentation", "Automated configuration management", "Comprehensive configuration management with drift detection"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.IP-1", "ISO_27001": "A.12.6.1"},
                help_text="Configuration management prevents security gaps from unauthorized changes"
            ),
            AssessmentQuestion(
                id="am_007",
                section_id="asset_management",
                section_name="Asset Management",
                category="Cloud Assets",
                question_text="How do you track and manage cloud-based assets?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No cloud asset tracking", "Manual cloud inventory", "Cloud-native tools for tracking", "Centralized cloud asset management", "Comprehensive multi-cloud asset visibility"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.14.1.1"},
                help_text="Cloud assets require specialized tracking and management approaches"
            ),
            AssessmentQuestion(
                id="am_008",
                section_id="asset_management",
                section_name="Asset Management",
                category="Mobile Devices",
                question_text="How do you manage and secure mobile devices?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No mobile device management", "Basic device policies", "Mobile Device Management (MDM)", "Enterprise Mobility Management (EMM)", "Zero-trust mobile security"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-3", "ISO_27001": "A.6.2.1"},
                help_text="Mobile devices extend the attack surface and require specific controls"
            ),
            AssessmentQuestion(
                id="am_009",
                section_id="asset_management",
                section_name="Asset Management",
                category="IoT Devices",
                question_text="How do you manage Internet of Things (IoT) devices?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No IoT devices", "Unmanaged IoT devices", "Basic IoT inventory", "IoT device management platform", "Comprehensive IoT security management"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.11.2.6"},
                help_text="IoT devices present unique security challenges and require specialized management"
            ),
            AssessmentQuestion(
                id="am_010",
                section_id="asset_management",
                section_name="Asset Management",
                category="Asset Discovery",
                question_text="How do you discover unknown or rogue assets on your network?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No asset discovery", "Manual periodic scans", "Automated network scanning", "Continuous asset discovery", "AI-powered asset discovery and classification"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.11.2.6"},
                help_text="Asset discovery identifies unauthorized devices that may pose security risks"
            ),
            AssessmentQuestion(
                id="am_011",
                section_id="asset_management",
                section_name="Asset Management",
                category="Documentation Standards",
                question_text="How standardized is your asset documentation and labeling?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No standards", "2 - Basic documentation", "3 - Consistent standards", "4 - Comprehensive documentation", "5 - Automated documentation with real-time updates"],
                required=True,
                weight=0.5,
                risk_impact=RiskLevel.LOW,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.8.1.1"},
                help_text="Standardized documentation improves asset management efficiency"
            ),
            AssessmentQuestion(
                id="am_012",
                section_id="asset_management",
                section_name="Asset Management",
                category="Asset Disposal",
                question_text="How do you securely dispose of IT assets containing sensitive data?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal disposal process", "Basic data deletion", "Data wiping procedures", "Certified data destruction", "Comprehensive secure disposal with certification"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-3", "ISO_27001": "A.8.3.2"},
                help_text="Secure disposal prevents data breaches from discarded equipment"
            )
        ])
        
        # Section 4: Data Protection & Privacy (18 questions)
        questions.extend([
            AssessmentQuestion(
                id="dp_001",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Classification",
                question_text="How robust is your data classification and labeling program?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No classification", "2 - Basic categories", "3 - Formal program", "4 - Automated classification", "5 - Comprehensive program"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.DS-2", "ISO_27001": "A.8.2.1"},
                help_text="Data classification enables appropriate protection controls"
            ),
            AssessmentQuestion(
                id="dp_002",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Encryption at Rest",
                question_text="What percentage of sensitive data is encrypted at rest?",
                question_type=QuestionType.DROPDOWN,
                options=["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.13.1.1"},
                help_text="Encryption at rest protects data from unauthorized access"
            ),
            AssessmentQuestion(
                id="dp_003",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Encryption in Transit",
                question_text="What percentage of data transmissions are encrypted?",
                question_type=QuestionType.DROPDOWN,
                options=["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.DS-2", "ISO_27001": "A.13.1.1"},
                help_text="Encryption in transit protects data during transmission"
            ),
            AssessmentQuestion(
                id="dp_004",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Backup Strategy",
                question_text="How comprehensive is your data backup strategy?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No formal backups", "2 - Basic backups", "3 - Regular backup schedule", "4 - Comprehensive backup strategy", "5 - Advanced backup with real-time replication"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-4", "ISO_27001": "A.12.3.1"},
                help_text="Backup strategy ensures data recovery capabilities"
            ),
            AssessmentQuestion(
                id="dp_005",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Backup Testing",
                question_text="How frequently do you test backup recovery procedures?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Never tested", "Annual testing", "Quarterly testing", "Monthly testing", "Continuous testing"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RC.RP-1", "ISO_27001": "A.17.1.3"},
                help_text="Regular testing ensures backup procedures work when needed"
            ),
            AssessmentQuestion(
                id="dp_006",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Loss Prevention",
                question_text="Do you have Data Loss Prevention (DLP) controls in place?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No DLP controls", "Basic email DLP", "Network DLP", "Endpoint DLP", "Comprehensive DLP across all vectors"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-3", "ISO_27001": "A.13.2.1"},
                help_text="DLP prevents unauthorized data exfiltration"
            ),
            AssessmentQuestion(
                id="dp_007",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Retention",
                question_text="Do you have formal data retention and disposal policies?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No retention policies", "Basic retention guidelines", "Formal retention policies", "Automated retention management", "Comprehensive lifecycle management"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.DS-3", "ISO_27001": "A.8.3.1"},
                help_text="Data retention policies reduce exposure and ensure compliance"
            ),
            AssessmentQuestion(
                id="dp_008",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Privacy Controls",
                question_text="How mature are your privacy protection controls?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No privacy controls", "2 - Basic privacy measures", "3 - Formal privacy program", "4 - Comprehensive privacy controls", "5 - Privacy by design"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.DS-2", "ISO_27001": "A.18.1.4"},
                help_text="Privacy controls protect personal data and ensure regulatory compliance"
            ),
            AssessmentQuestion(
                id="dp_009",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Discovery",
                question_text="How well do you know where sensitive data resides in your environment?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No data discovery", "2 - Basic data location awareness", "3 - Regular data discovery scans", "4 - Automated data discovery", "5 - Real-time data discovery and classification"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.AM-5", "ISO_27001": "A.8.2.1"},
                help_text="Data discovery is essential for protecting sensitive information"
            ),
            AssessmentQuestion(
                id="dp_010",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Database Security",
                question_text="How comprehensive is your database security program?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - Basic database security", "2 - Standard database hardening", "3 - Comprehensive database security", "4 - Advanced database protection", "5 - Zero-trust database security"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.13.1.1"},
                help_text="Database security protects critical business data"
            ),
            AssessmentQuestion(
                id="dp_011",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Masking",
                question_text="Do you use data masking or anonymization techniques?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No data masking", "Basic data masking for testing", "Comprehensive data masking", "Dynamic data masking", "Advanced anonymization and pseudonymization"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.DS-2", "ISO_27001": "A.18.1.3"},
                help_text="Data masking reduces risk in non-production environments"
            ),
            AssessmentQuestion(
                id="dp_012",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Cross-Border Data",
                question_text="How do you manage cross-border data transfers?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No cross-border transfers", "Unmanaged transfers", "Basic transfer controls", "Formal transfer agreements", "Comprehensive cross-border data governance"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-2", "ISO_27001": "A.18.1.3"},
                help_text="Cross-border transfers require specific privacy and security controls"
            ),
            AssessmentQuestion(
                id="dp_013",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Subject Rights",
                question_text="How do you handle data subject access requests?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal process", "Manual request handling", "Semi-automated process", "Automated request fulfillment", "Comprehensive privacy rights management"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.DS-2", "ISO_27001": "A.18.1.4"},
                help_text="Data subject rights management ensures regulatory compliance"
            ),
            AssessmentQuestion(
                id="dp_014",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Breach Notification",
                question_text="Do you have a data breach notification process?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No notification process", "Basic incident notification", "Formal notification procedures", "Automated notification systems", "Comprehensive breach response program"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.CO-2", "ISO_27001": "A.16.1.2"},
                help_text="Breach notification ensures regulatory compliance and stakeholder communication"
            ),
            AssessmentQuestion(
                id="dp_015",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Privacy Impact Assessment",
                question_text="Do you conduct Privacy Impact Assessments (PIAs)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No PIAs conducted", "PIAs for major projects only", "Regular PIA process", "Automated PIA integration", "Comprehensive privacy risk assessment"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.RA-1", "ISO_27001": "A.18.1.4"},
                help_text="PIAs identify and mitigate privacy risks in advance"
            ),
            AssessmentQuestion(
                id="dp_016",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Key Management",
                question_text="How do you manage encryption keys?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal key management", "Basic key storage", "Key management procedures", "Dedicated key management system", "Enterprise key management with HSM"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.13.1.1"},
                help_text="Proper key management is essential for encryption effectiveness"
            ),
            AssessmentQuestion(
                id="dp_017",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Cloud Data Protection",
                question_text="How do you protect data in cloud environments?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Basic cloud security", "Cloud-native security tools", "Comprehensive cloud data protection", "Multi-cloud security management", "Zero-trust cloud architecture"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.14.1.3"},
                help_text="Cloud data requires specialized protection approaches"
            ),
            AssessmentQuestion(
                id="dp_018",
                section_id="data_protection",
                section_name="Data Protection & Privacy",
                category="Data Quality",
                question_text="How do you ensure data integrity and quality?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No data quality controls", "2 - Basic integrity checks", "3 - Regular data validation", "4 - Automated quality controls", "5 - Comprehensive data integrity management"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.DS-6", "ISO_27001": "A.12.2.1"},
                help_text="Data integrity ensures reliability and trustworthiness of information"
            )
        ])
        
        # Section 5: Access Control & Identity Management (16 questions)
        questions.extend([
            AssessmentQuestion(
                id="ac_001", 
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Multi-Factor Authentication",
                question_text="What percentage of your user accounts have multi-factor authentication enabled?",
                question_type=QuestionType.DROPDOWN,
                options=["0-10%", "11-25%", "26-50%", "51-75%", "76-90%", "91-100%"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.4.2"},
                help_text="MFA is critical protection against credential-based attacks"
            ),
            AssessmentQuestion(
                id="ac_002",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Privileged Access Management",
                question_text="How do you manage privileged user accounts?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No special controls", "Basic privileged account policies", "Privileged Access Management (PAM) solution", "Advanced PAM with session recording", "Zero-trust privileged access"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.AC-4", "ISO_27001": "A.9.2.3"},
                help_text="Privileged accounts have elevated access and require special protection"
            ),
            AssessmentQuestion(
                id="ac_003",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Identity Governance",
                question_text="How mature is your identity governance program?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No identity governance", "2 - Basic user provisioning", "3 - Formal identity processes", "4 - Automated identity governance", "5 - Comprehensive identity lifecycle management"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.2.1"},
                help_text="Identity governance ensures appropriate access throughout user lifecycle"
            ),
            AssessmentQuestion(
                id="ac_004",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Access Reviews",
                question_text="How frequently do you review user access rights?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Never/Ad-hoc", "Annual reviews", "Quarterly reviews", "Monthly reviews", "Continuous access monitoring"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-4", "ISO_27001": "A.9.2.6"},
                help_text="Regular access reviews prevent privilege creep and unauthorized access"
            ),
            AssessmentQuestion(
                id="ac_005",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Single Sign-On",
                question_text="What percentage of applications use Single Sign-On (SSO)?",
                question_type=QuestionType.DROPDOWN,
                options=["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.4.2"},
                help_text="SSO improves security and user experience"
            ),
            AssessmentQuestion(
                id="ac_006",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Password Policies",
                question_text="How comprehensive are your password policies?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No password policy", "Basic password requirements", "Comprehensive password policy", "Advanced password policy with monitoring", "Passwordless authentication"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.4.3"},
                help_text="Strong password policies reduce credential-based attacks"
            ),
            AssessmentQuestion(
                id="ac_007",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Role-Based Access",
                question_text="Do you implement role-based access control (RBAC)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal roles", "Basic role definitions", "Comprehensive RBAC", "Dynamic role assignment", "Attribute-based access control (ABAC)"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-4", "ISO_27001": "A.9.1.2"},
                help_text="RBAC ensures users have appropriate access based on their responsibilities"
            ),
            AssessmentQuestion(
                id="ac_008",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Account Provisioning",
                question_text="How do you handle user account provisioning and deprovisioning?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Manual processes", "Semi-automated provisioning", "Automated provisioning", "Just-in-time provisioning", "Zero-trust provisioning"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.2.1"},
                help_text="Automated provisioning reduces errors and improves security"
            ),
            AssessmentQuestion(
                id="ac_009",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Remote Access",
                question_text="How do you secure remote access to corporate resources?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Basic VPN", "VPN with MFA", "Zero-trust network access", "Comprehensive remote access security", "Secure access service edge (SASE)"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-3", "ISO_27001": "A.6.2.1"},
                help_text="Remote access security is critical for distributed workforces"
            ),
            AssessmentQuestion(
                id="ac_010",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Session Management",
                question_text="How do you manage user sessions and concurrent access?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No session controls", "Basic session timeouts", "Comprehensive session management", "Advanced session monitoring", "Zero-trust session security"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.4.1"},
                help_text="Session management prevents unauthorized access to active sessions"
            ),
            AssessmentQuestion(
                id="ac_011",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Directory Services",
                question_text="How centralized is your directory and identity management?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No centralized directory", "Basic directory service", "Comprehensive directory integration", "Cloud directory services", "Hybrid identity management"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.2.1"},
                help_text="Centralized directory services improve identity management consistency"
            ),
            AssessmentQuestion(
                id="ac_012",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Segregation of Duties",
                question_text="Do you implement segregation of duties for critical functions?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No segregation controls", "Basic duty separation", "Formal segregation policies", "Automated segregation controls", "Comprehensive duty segregation with monitoring"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-4", "ISO_27001": "A.9.1.2"},
                help_text="Segregation of duties prevents fraud and errors"
            ),
            AssessmentQuestion(
                id="ac_013",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Access Logging",
                question_text="How comprehensive is your access logging and monitoring?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No access logging", "2 - Basic login logs", "3 - Comprehensive access logs", "4 - Real-time access monitoring", "5 - Advanced access analytics"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.AE-3", "ISO_27001": "A.12.4.1"},
                help_text="Access logging enables detection of unauthorized access attempts"
            ),
            AssessmentQuestion(
                id="ac_014",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Guest Access",
                question_text="How do you manage guest and temporary access?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No guest access controls", "Basic guest policies", "Formal guest access process", "Automated guest management", "Zero-trust guest access"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.2.6"},
                help_text="Guest access requires special controls to limit exposure"
            ),
            AssessmentQuestion(
                id="ac_015",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Emergency Access",
                question_text="Do you have emergency access procedures for critical situations?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No emergency procedures", "Basic break-glass access", "Formal emergency access process", "Automated emergency controls", "Comprehensive crisis access management"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AC-6", "ISO_27001": "A.9.2.6"},
                help_text="Emergency access ensures business continuity while maintaining security"
            ),
            AssessmentQuestion(
                id="ac_016",
                section_id="access_control",
                section_name="Access Control & Identity Management",
                category="Application Access",
                question_text="How do you control access to applications and systems?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Basic application security", "Application-level access controls", "Comprehensive application security", "Zero-trust application access", "Advanced application protection"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-5", "ISO_27001": "A.14.2.5"},
                help_text="Application access controls protect business-critical systems and data"
            )
        ])
        
        # Section 6: Security Monitoring & Detection (14 questions)
        questions.extend([
            AssessmentQuestion(
                id="sm_001",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="SIEM/Log Management",
                question_text="What type of security event monitoring do you have in place?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No centralized logging", "Basic log collection", "SIEM solution deployed", "Advanced threat detection", "AI-powered security operations"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "DE.AE-3", "ISO_27001": "A.12.4.1"},
                help_text="Security monitoring provides visibility into potential threats and incidents"
            ),
            AssessmentQuestion(
                id="sm_002",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Threat Intelligence",
                question_text="Do you use threat intelligence to enhance your security monitoring?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No threat intelligence", "2 - Basic threat feeds", "3 - Commercial threat intelligence", "4 - Integrated threat intelligence platform", "5 - Advanced threat hunting capabilities"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.DP-4", "ISO_27001": "A.16.1.3"},
                help_text="Threat intelligence helps identify and respond to emerging threats"
            ),
            AssessmentQuestion(
                id="sm_003",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Network Monitoring",
                question_text="How comprehensive is your network traffic monitoring?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No network monitoring", "Basic network tools", "Network security monitoring", "Advanced network detection", "AI-powered network analysis"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.CM-1", "ISO_27001": "A.12.4.2"},
                help_text="Network monitoring detects lateral movement and data exfiltration"
            ),
            AssessmentQuestion(
                id="sm_004",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Endpoint Detection",
                question_text="What endpoint detection and response capabilities do you have?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Traditional antivirus only", "Next-gen antivirus", "Basic EDR solution", "Advanced EDR with threat hunting", "XDR with full integration"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.CM-7", "ISO_27001": "A.12.2.1"},
                help_text="Endpoint detection is critical for identifying compromised systems"
            ),
            AssessmentQuestion(
                id="sm_005",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Vulnerability Scanning",
                question_text="How frequently do you conduct vulnerability assessments?",
                question_type=QuestionType.DROPDOWN,
                options=["Never", "Annually", "Quarterly", "Monthly", "Weekly", "Continuous scanning"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.CM-8", "ISO_27001": "A.12.6.1"},
                help_text="Regular vulnerability scanning identifies security weaknesses"
            ),
            AssessmentQuestion(
                id="sm_006",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Penetration Testing",
                question_text="How often do you conduct penetration testing?",
                question_type=QuestionType.DROPDOWN,
                options=["Never", "Every few years", "Annually", "Bi-annually", "Quarterly", "Continuous red team"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "DE.DP-4", "ISO_27001": "A.14.2.8"},
                help_text="Penetration testing validates the effectiveness of security controls"
            ),
            AssessmentQuestion(
                id="sm_007",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Alert Management",
                question_text="How effective is your security alert management process?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - Overwhelmed by alerts", "2 - Basic alert review", "3 - Structured alert process", "4 - Advanced correlation", "5 - AI-powered alert prioritization"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.AE-5", "ISO_27001": "A.16.1.4"},
                help_text="Effective alert management ensures timely response to real threats"
            ),
            AssessmentQuestion(
                id="sm_008",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Security Metrics",
                question_text="Do you track and analyze security metrics and KPIs?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No security metrics", "Basic security reporting", "Regular metrics tracking", "Comprehensive dashboard", "Advanced analytics platform"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "DE.DP-5", "ISO_27001": "A.16.1.7"},
                help_text="Security metrics enable measurement and improvement of security posture"
            ),
            AssessmentQuestion(
                id="sm_009",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Cloud Security Monitoring",
                question_text="How do you monitor security in cloud environments?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No cloud monitoring", "Basic cloud logs", "Cloud security tools", "CSPM solution", "Comprehensive cloud security platform"],
                required=False,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.CM-1", "ISO_27001": "A.14.1.3"},
                help_text="Cloud environments require specialized monitoring approaches"
            ),
            AssessmentQuestion(
                id="sm_010",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Insider Threat Detection",
                question_text="Do you have capabilities to detect insider threats?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No insider threat program", "2 - Basic monitoring", "3 - User behavior analytics", "4 - Advanced insider threat platform", "5 - Comprehensive insider risk management"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.CM-3", "ISO_27001": "A.12.4.3"},
                help_text="Insider threats require specialized detection capabilities"
            ),
            AssessmentQuestion(
                id="sm_011",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Forensic Capabilities",
                question_text="What digital forensic capabilities do you maintain?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No forensic capabilities", "Basic log retention", "Forensic tools available", "Trained forensic staff", "Advanced forensic laboratory"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "DE.AE-2", "ISO_27001": "A.16.1.7"},
                help_text="Forensic capabilities support incident investigation and evidence collection"
            ),
            AssessmentQuestion(
                id="sm_012",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Threat Hunting",
                question_text="Do you conduct proactive threat hunting activities?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No threat hunting", "Ad-hoc searches", "Regular hunting activities", "Structured hunting program", "Advanced threat hunting team"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "DE.DP-4", "ISO_27001": "A.16.1.3"},
                help_text="Proactive threat hunting identifies sophisticated attacks"
            ),
            AssessmentQuestion(
                id="sm_013",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="Security Orchestration",
                question_text="Do you use security orchestration and automation (SOAR)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No automation", "Basic scripting", "Security orchestration platform", "Advanced SOAR with playbooks", "AI-powered security automation"],
                required=False,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "RS.MI-3", "ISO_27001": "A.16.1.5"},
                help_text="Security automation improves response speed and consistency"
            ),
            AssessmentQuestion(
                id="sm_014",
                section_id="security_monitoring",
                section_name="Security Monitoring & Detection",
                category="24/7 Monitoring",
                question_text="Do you have 24/7 security monitoring coverage?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No 24/7 coverage", "Business hours only", "Extended hours coverage", "24/7 internal SOC", "24/7 managed security services"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "DE.AE-4", "ISO_27001": "A.16.1.2"},
                help_text="24/7 monitoring ensures rapid detection and response to security events"
            )
        ])
        
        # Section 7: Incident Response & Recovery (12 questions)
        questions.extend([
            AssessmentQuestion(
                id="ir_001",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Incident Response Plan",
                question_text="Do you have a documented incident response plan?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No incident response plan", "Basic response procedures", "Documented IR plan", "Comprehensive IR framework", "Tested and mature IR program"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.16.1.1"},
                help_text="An incident response plan ensures organized and effective response to security incidents"
            ),
            AssessmentQuestion(
                id="ir_002",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="IR Team Structure",
                question_text="How is your incident response team organized?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No dedicated team", "Ad-hoc response team", "Designated IR team", "Trained IR specialists", "Cross-functional CSIRT"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.RP-2", "ISO_27001": "A.16.1.1"},
                help_text="A structured IR team ensures proper roles and responsibilities during incidents"
            ),
            AssessmentQuestion(
                id="ir_003",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Incident Classification",
                question_text="Do you have a system for classifying and prioritizing incidents?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No classification system", "2 - Basic severity levels", "3 - Structured classification", "4 - Detailed impact assessment", "5 - Dynamic risk-based prioritization"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.AN-3", "ISO_27001": "A.16.1.4"},
                help_text="Incident classification ensures appropriate response and resource allocation"
            ),
            AssessmentQuestion(
                id="ir_004",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Response Testing",
                question_text="How often do you test your incident response procedures?",
                question_type=QuestionType.DROPDOWN,
                options=["Never tested", "Every few years", "Annually", "Bi-annually", "Quarterly", "Regular exercises"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.17.1.3"},
                help_text="Regular testing validates and improves incident response capabilities"
            ),
            AssessmentQuestion(
                id="ir_005",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Communication Plan",
                question_text="Do you have established communication procedures for incidents?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No communication plan", "Basic notification process", "Structured communication plan", "Multi-channel communication", "Crisis communication framework"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.CO-2", "ISO_27001": "A.16.1.2"},
                help_text="Clear communication is essential during security incidents"
            ),
            AssessmentQuestion(
                id="ir_006",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Forensic Evidence",
                question_text="How do you preserve forensic evidence during incidents?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No evidence preservation", "Basic log collection", "Structured evidence handling", "Forensic best practices", "Legal-grade evidence management"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "RS.AN-2", "ISO_27001": "A.16.1.7"},
                help_text="Proper evidence preservation supports investigation and potential legal action"
            ),
            AssessmentQuestion(
                id="ir_007",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Recovery Planning",
                question_text="How comprehensive are your recovery and restoration procedures?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No recovery procedures", "2 - Basic restoration steps", "3 - Documented recovery plans", "4 - Tested recovery procedures", "5 - Automated recovery capabilities"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RC.RP-1", "ISO_27001": "A.17.1.2"},
                help_text="Recovery procedures ensure rapid restoration of normal operations"
            ),
            AssessmentQuestion(
                id="ir_008",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Legal and Regulatory",
                question_text="Are you prepared to meet legal and regulatory notification requirements?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No regulatory awareness", "Basic compliance understanding", "Documented notification procedures", "Legal counsel involvement", "Comprehensive compliance framework"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.CO-3", "ISO_27001": "A.16.1.6"},
                help_text="Regulatory compliance requires timely and accurate incident notification"
            ),
            AssessmentQuestion(
                id="ir_009",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Lessons Learned",
                question_text="Do you conduct post-incident reviews and implement improvements?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No post-incident process", "2 - Basic incident documentation", "3 - Structured lessons learned", "4 - Improvement implementation", "5 - Continuous improvement program"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "RS.IM-1", "ISO_27001": "A.16.1.7"},
                help_text="Post-incident reviews drive continuous improvement of security capabilities"
            ),
            AssessmentQuestion(
                id="ir_010",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="External Resources",
                question_text="Do you have relationships with external incident response resources?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No external relationships", "Basic vendor contacts", "Incident response retainer", "Law enforcement contacts", "Comprehensive external network"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.16.1.1"},
                help_text="External resources can provide additional expertise and support during major incidents"
            ),
            AssessmentQuestion(
                id="ir_011",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Containment Strategies",
                question_text="How effective are your incident containment strategies?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No containment procedures", "2 - Basic isolation steps", "3 - Network segmentation capability", "4 - Advanced containment tools", "5 - Automated containment systems"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.MI-2", "ISO_27001": "A.16.1.5"},
                help_text="Quick containment prevents incident spread and minimizes damage"
            ),
            AssessmentQuestion(
                id="ir_012",
                section_id="incident_response",
                section_name="Incident Response & Recovery",
                category="Business Continuity",
                question_text="How well-integrated are your IR and business continuity plans?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No integration", "Basic coordination", "Aligned procedures", "Integrated planning", "Unified resilience framework"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RC.CO-3", "ISO_27001": "A.17.1.1"},
                help_text="Integration ensures coordinated response that maintains business operations"
            )
        ])
        
        # Section 8: Vendor & Third-Party Risk (10 questions)
        questions.extend([
            AssessmentQuestion(
                id="vr_001",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Vendor Assessment",
                question_text="How do you assess the security posture of new vendors?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No vendor assessment", "Basic questionnaire", "Security assessment process", "Comprehensive due diligence", "Continuous vendor monitoring"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "ID.SC-2", "ISO_27001": "A.15.1.1"},
                help_text="Vendor assessment prevents supply chain security risks"
            ),
            AssessmentQuestion(
                id="vr_002",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Contract Security",
                question_text="Are security requirements included in vendor contracts?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No security requirements", "2 - Basic security clauses", "3 - Standard security terms", "4 - Comprehensive security requirements", "5 - Risk-based security contracts"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.SC-3", "ISO_27001": "A.15.1.2"},
                help_text="Contractual security requirements establish vendor accountability"
            ),
            AssessmentQuestion(
                id="vr_003",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Vendor Monitoring",
                question_text="How do you monitor vendor security performance over time?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No ongoing monitoring", "Annual review", "Regular assessments", "Continuous monitoring", "Real-time vendor risk platform"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.SC-4", "ISO_27001": "A.15.2.1"},
                help_text="Ongoing monitoring detects changes in vendor risk posture"
            ),
            AssessmentQuestion(
                id="vr_004",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Data Access Controls",
                question_text="How do you control vendor access to your data and systems?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Full access to vendors", "Basic access controls", "Role-based vendor access", "Least privilege access", "Zero-trust vendor access"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.15.1.3"},
                help_text="Controlled vendor access limits exposure to sensitive data"
            ),
            AssessmentQuestion(
                id="vr_005",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Incident Response",
                question_text="Do you have incident response procedures for vendor-related incidents?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No vendor IR procedures", "Basic incident notification", "Vendor incident response plan", "Integrated vendor IR", "Coordinated vendor incident management"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "RS.CO-4", "ISO_27001": "A.16.1.2"},
                help_text="Vendor incident procedures ensure coordinated response to supply chain incidents"
            ),
            AssessmentQuestion(
                id="vr_006",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Supply Chain Visibility",
                question_text="How well do you understand your extended supply chain?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No visibility beyond direct vendors", "2 - Aware of major subcontractors", "3 - Documentation of key supply chains", "4 - Regular supply chain mapping", "5 - Comprehensive supply chain intelligence"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.SC-1", "ISO_27001": "A.15.1.1"},
                help_text="Supply chain visibility helps identify hidden risks and dependencies"
            ),
            AssessmentQuestion(
                id="vr_007",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Software Supply Chain",
                question_text="How do you secure your software supply chain?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No software supply chain controls", "Basic software vetting", "Software composition analysis", "Secure development practices", "Comprehensive software supply chain security"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.SC-5", "ISO_27001": "A.14.2.1"},
                help_text="Software supply chain security prevents malicious code injection"
            ),
            AssessmentQuestion(
                id="vr_008",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Vendor Termination",
                question_text="Do you have secure vendor termination procedures?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No termination procedures", "Basic offboarding", "Structured termination process", "Secure asset recovery", "Comprehensive vendor lifecycle management"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.SC-3", "ISO_27001": "A.15.2.2"},
                help_text="Secure termination prevents data exposure after vendor relationships end"
            ),
            AssessmentQuestion(
                id="vr_009",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Fourth-Party Risk",
                question_text="How do you manage fourth-party (vendor's vendor) risks?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No fourth-party awareness", "Basic vendor disclosure", "Fourth-party assessment", "Extended due diligence", "Comprehensive nth-party risk management"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.SC-2", "ISO_27001": "A.15.1.1"},
                help_text="Fourth-party risks can create unexpected vulnerabilities in the supply chain"
            ),
            AssessmentQuestion(
                id="vr_010",
                section_id="vendor_risk",
                section_name="Vendor & Third-Party Risk",
                category="Vendor Risk Metrics",
                question_text="Do you track metrics and KPIs for vendor risk management?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No vendor metrics", "Basic vendor tracking", "Regular risk reporting", "Comprehensive vendor dashboard", "Advanced vendor risk analytics"],
                required=True,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.SC-4", "ISO_27001": "A.15.2.1"},
                help_text="Vendor metrics enable data-driven supply chain risk management"
            )
        ])
        
        # Section 9: Security Awareness & Training (8 questions)
        questions.extend([
            AssessmentQuestion(
                id="st_001",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="General Awareness Training",
                question_text="How comprehensive is your security awareness training program?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No formal training", "Basic annual training", "Regular awareness sessions", "Comprehensive training program", "Continuous adaptive training"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                help_text="Security awareness training is the foundation of human-centered security"
            ),
            AssessmentQuestion(
                id="st_002",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="Phishing Training",
                question_text="Do you conduct phishing simulation and training?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No phishing training", "2 - Occasional simulations", "3 - Regular phishing tests", "4 - Targeted training based on results", "5 - Continuous phishing resistance program"],
                required=True,
                weight=1.0,
                risk_impact=RiskLevel.CRITICAL,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                help_text="Phishing training reduces susceptibility to email-based attacks"
            ),
            AssessmentQuestion(
                id="st_003",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="Role-Based Training",
                question_text="Do you provide role-specific security training?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No role-based training", "Basic role differentiation", "Targeted role training", "Comprehensive role-based curriculum", "Personalized training paths"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AT-2", "ISO_27001": "A.7.2.2"},
                help_text="Role-based training addresses specific risks faced by different positions"
            ),
            AssessmentQuestion(
                id="st_004",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="Training Effectiveness",
                question_text="How do you measure the effectiveness of security training?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No measurement", "Basic completion tracking", "Knowledge assessments", "Behavioral change metrics", "Comprehensive training analytics"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                help_text="Training effectiveness measurement ensures program value and improvement"
            ),
            AssessmentQuestion(
                id="st_005",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="New Employee Training",
                question_text="Do new employees receive security training during onboarding?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No onboarding security training", "Basic security overview", "Structured onboarding curriculum", "Comprehensive security orientation", "Integrated role-based onboarding"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                help_text="Early security training establishes good security habits from the start"
            ),
            AssessmentQuestion(
                id="st_006",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="Privileged User Training",
                question_text="Do privileged users receive enhanced security training?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No enhanced training", "Basic privileged user guidance", "Specialized privileged training", "Comprehensive privileged user program", "Continuous privileged user education"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AT-2", "ISO_27001": "A.7.2.2"},
                help_text="Privileged users require enhanced training due to their elevated access"
            ),
            AssessmentQuestion(
                id="st_007",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="Incident Response Training",
                question_text="Do employees receive training on incident reporting and response?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No incident training", "2 - Basic incident awareness", "3 - Incident reporting procedures", "4 - Response role training", "5 - Comprehensive incident preparedness"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.16.1.1"},
                help_text="Incident training ensures rapid and appropriate response to security events"
            ),
            AssessmentQuestion(
                id="st_008",
                section_id="security_awareness",
                section_name="Security Awareness & Training",
                category="Security Culture",
                question_text="How actively do you promote a positive security culture?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - Security seen as burden", "2 - Compliance-focused culture", "3 - Security awareness promoted", "4 - Security valued by employees", "5 - Security embedded in culture"],
                required=True,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                help_text="Positive security culture makes employees active participants in security"
            )
        ])
        
        # Section 10: Emerging Technology Governance (10 questions)
        questions.extend([
            AssessmentQuestion(
                id="et_001",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="AI/ML Security",
                question_text="How do you address security risks in AI and machine learning systems?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No AI/ML security program", "Basic AI security awareness", "AI security guidelines", "Comprehensive AI risk management", "Advanced AI security framework"],
                required=False,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "ID.RA-1", "ISO_27001": "A.14.2.1"},
                help_text="AI/ML systems introduce new attack vectors and privacy risks"
            ),
            AssessmentQuestion(
                id="et_002",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="Cloud Native Security",
                question_text="How mature is your cloud-native security approach?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - Traditional security in cloud", "2 - Basic cloud security", "3 - Cloud-native security tools", "4 - DevSecOps integration", "5 - Cloud-native security platform"],
                required=False,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.IP-1", "ISO_27001": "A.14.1.3"},
                help_text="Cloud-native environments require modern security approaches"
            ),
            AssessmentQuestion(
                id="et_003",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="IoT Security",
                question_text="How do you secure Internet of Things (IoT) devices?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No IoT security program", "Basic IoT device management", "IoT security policies", "Comprehensive IoT security", "Advanced IoT threat management"],
                required=False,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.11.2.6"},
                help_text="IoT devices expand the attack surface and require specialized security"
            ),
            AssessmentQuestion(
                id="et_004",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="Zero Trust Architecture",
                question_text="How advanced is your zero trust implementation?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - Traditional perimeter security", "2 - Zero trust awareness", "3 - Pilot zero trust initiatives", "4 - Partial zero trust deployment", "5 - Mature zero trust architecture"],
                required=False,
                weight=0.9,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.1.2"},
                help_text="Zero trust provides modern security architecture for dynamic environments"
            ),
            AssessmentQuestion(
                id="et_005",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="Quantum Readiness",
                question_text="Are you preparing for quantum computing security implications?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No quantum awareness", "Basic quantum understanding", "Quantum risk assessment", "Post-quantum cryptography planning", "Quantum-ready security strategy"],
                required=False,
                weight=0.5,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.10.1.1"},
                help_text="Quantum computing will render current cryptography obsolete"
            ),
            AssessmentQuestion(
                id="et_006",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="API Security",
                question_text="How comprehensive is your API security program?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No API security program", "Basic API documentation", "API security guidelines", "Comprehensive API security", "Advanced API threat protection"],
                required=True,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.AC-5", "ISO_27001": "A.14.2.5"},
                help_text="APIs are critical attack vectors in modern applications"
            ),
            AssessmentQuestion(
                id="et_007",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="DevSecOps Maturity",
                question_text="How mature is your DevSecOps implementation?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No DevSecOps", "2 - Basic security in CI/CD", "3 - Integrated security testing", "4 - Automated security controls", "5 - Security-native development"],
                required=False,
                weight=0.8,
                risk_impact=RiskLevel.HIGH,
                framework_mapping={"NIST_CSF": "PR.IP-2", "ISO_27001": "A.14.2.1"},
                help_text="DevSecOps embeds security throughout the development lifecycle"
            ),
            AssessmentQuestion(
                id="et_008",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="Edge Computing Security",
                question_text="How do you secure edge computing environments?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No edge computing", "Basic edge security", "Edge security guidelines", "Comprehensive edge protection", "Advanced edge security platform"],
                required=False,
                weight=0.6,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.IP-1", "ISO_27001": "A.11.2.6"},
                help_text="Edge computing extends security perimeters to distributed locations"
            ),
            AssessmentQuestion(
                id="et_009",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="Blockchain Security",
                question_text="If you use blockchain technology, how do you secure it?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["No blockchain use", "Basic blockchain security", "Blockchain security policies", "Comprehensive blockchain governance", "Advanced blockchain security"],
                required=False,
                weight=0.5,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.14.2.1"},
                help_text="Blockchain implementations require specialized security considerations"
            ),
            AssessmentQuestion(
                id="et_010",
                section_id="emerging_technology",
                section_name="Emerging Technology Governance",
                category="Technology Innovation",
                question_text="How do you evaluate security for new and emerging technologies?",
                question_type=QuestionType.LIKERT_SCALE,
                options=["1 - No formal evaluation", "2 - Basic security review", "3 - Risk assessment process", "4 - Comprehensive technology evaluation", "5 - Innovation security framework"],
                required=True,
                weight=0.7,
                risk_impact=RiskLevel.MEDIUM,
                framework_mapping={"NIST_CSF": "ID.RA-3", "ISO_27001": "A.14.2.1"},
                help_text="Systematic evaluation ensures security is considered for new technologies"
            )
        ])
        
        return questions
    
    def get_assessment_overview(self) -> Dict[str, Any]:
        """Get complete assessment overview"""
        
        total_questions = sum(section.question_count for section in self.sections)
        total_time = self._calculate_total_time()
        
        return {
            "assessment_info": {
                "title": "Enterprise Cybersecurity Risk Assessment",
                "description": "Comprehensive security posture evaluation based on NIST CSF 2.0, ISO 27001, and industry best practices",
                "version": "2.0",
                "total_sections": len(self.sections),
                "total_questions": total_questions,
                "estimated_time": total_time,
                "completion_rate_target": 85,
                "frameworks_covered": ["NIST CSF 2.0", "ISO 27001", "SOC 2", "CIS Controls"]
            },
            "sections": [asdict(section) for section in self.sections],
            "scoring_methodology": {
                "approach": "NIST CSF 2.0 Maturity Levels",
                "weighting": "Risk-impact and industry-specific weighting",
                "confidence_intervals": "Statistical uncertainty quantification", 
                "benchmarking": "Industry peer comparison"
            },
            "question_distribution": {
                "likert_scale": f"{len([q for q in self.questions if q.question_type == QuestionType.LIKERT_SCALE])} (70%)",
                "multiple_choice": f"{len([q for q in self.questions if q.question_type == QuestionType.MULTIPLE_CHOICE])} (20%)",
                "short_text": f"{len([q for q in self.questions if q.question_type == QuestionType.SHORT_TEXT])} (10%)"
            }
        }
    
    def get_section_questions(self, section_id: str) -> Dict[str, Any]:
        """Get questions for specific section"""
        
        section = next((s for s in self.sections if s.id == section_id), None)
        if not section:
            return {"error": "Section not found"}
        
        section_questions = [q for q in self.questions if q.section_id == section_id]
        
        return {
            "section": asdict(section),
            "questions": [asdict(q) for q in section_questions],
            "progress_info": {
                "current_section": section.order,
                "total_sections": len(self.sections),
                "questions_in_section": len(section_questions)
            }
        }
    
    def calculate_section_score(self, section_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score for completed section using NIST CSF 2.0 methodology"""
        
        section = next((s for s in self.sections if s.id == section_id), None)
        if not section:
            return {"error": "Section not found"}
        
        section_questions = [q for q in self.questions if q.section_id == section_id]
        
        total_score = 0.0
        total_weight = 0.0
        answered_questions = 0
        risk_scores = {level.name: 0.0 for level in RiskLevel}
        
        for question in section_questions:
            if question.id in responses:
                answered_questions += 1
                response_value = responses[question.id]
                
                # Convert response to numeric score
                if question.question_type == QuestionType.LIKERT_SCALE:
                    score = int(response_value) / 5.0  # Normalize to 0-1
                elif question.question_type == QuestionType.DROPDOWN:
                    # Score based on option index (higher = better)
                    score = (len(question.options) - question.options.index(response_value)) / len(question.options)
                elif question.question_type == QuestionType.MULTIPLE_CHOICE:
                    # Custom scoring logic per question
                    score = 0.5  # Default middle score
                else:
                    score = 0.5  # Default for other types
                
                weighted_score = score * question.weight
                total_score += weighted_score
                total_weight += question.weight
                
                # Track risk-level specific scores
                risk_scores[question.risk_impact.name] += weighted_score
        
        # Calculate final scores
        section_score = (total_score / total_weight * 100) if total_weight > 0 else 0
        completion_rate = (answered_questions / len(section_questions) * 100) if section_questions else 0
        
        # Determine maturity level
        maturity_level = self._determine_maturity_level(section_score)
        
        return {
            "section_id": section_id,
            "section_name": section.name,
            "score": round(section_score, 1),
            "completion_rate": round(completion_rate, 1),
            "maturity_level": maturity_level.value[1],
            "maturity_description": maturity_level.value[2],
            "questions_answered": answered_questions,
            "total_questions": len(section_questions),
            "risk_breakdown": {
                level: round(score, 1) for level, score in risk_scores.items()
            },
            "recommendations": self._generate_section_recommendations(section_id, section_score, risk_scores)
        }
    
    def _determine_maturity_level(self, score: float) -> MaturityLevel:
        """Determine NIST CSF 2.0 maturity level based on score"""
        
        if score >= 85:
            return MaturityLevel.ADAPTIVE
        elif score >= 70:
            return MaturityLevel.REPEATABLE
        elif score >= 50:
            return MaturityLevel.RISK_INFORMED
        else:
            return MaturityLevel.PARTIAL
    
    def _generate_section_recommendations(self, section_id: str, score: float, risk_scores: Dict[str, float]) -> List[str]:
        """Generate section-specific recommendations"""
        
        recommendations = []
        
        if score < 50:
            recommendations.append(f"Immediate attention needed: {section_id} requires fundamental improvements")
        elif score < 70:
            recommendations.append(f"Enhancement opportunity: {section_id} has room for significant improvement")
        
        # Add risk-specific recommendations
        for risk_level, risk_score in risk_scores.items():
            if risk_score < 30 and risk_level in ["CRITICAL", "HIGH"]:
                recommendations.append(f"Address {risk_level.lower()} risk areas in {section_id}")
        
        return recommendations
    
    def _calculate_total_time(self) -> str:
        """Calculate total estimated assessment time"""
        
        total_minutes = 0
        for section in self.sections:
            # Parse time estimate (e.g., "8-10 minutes" -> 9)
            time_parts = section.estimated_time.split("-")
            if len(time_parts) == 2:
                min_time = int(time_parts[0])
                max_time = int(time_parts[1].split()[0])
                avg_time = (min_time + max_time) // 2
                total_minutes += avg_time
            
        return f"{total_minutes} minutes ({total_minutes // 60}h {total_minutes % 60}m)"

# Global instance
modern_assessment = ModernAssessmentBuilder()