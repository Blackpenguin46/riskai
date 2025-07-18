"""
Structured Assessment Framework

Creates a standardized assessment form based on industry frameworks
(NIST CSF, ISO 27001, CIS Controls, etc.) with clear, objective questions.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Types of assessment questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    BOOLEAN = "boolean"
    DROPDOWN = "dropdown"
    CHECKLIST = "checklist"

class MaturityLevel(Enum):
    """Maturity levels for assessment"""
    NONE = (0, "Not Implemented", "No implementation or awareness")
    BASIC = (1, "Basic", "Basic implementation with minimal documentation")
    DEFINED = (2, "Defined", "Documented processes and procedures")
    MANAGED = (3, "Managed", "Monitored and measured implementation")
    OPTIMIZED = (4, "Optimized", "Continuously improved and optimized")

@dataclass
class AssessmentQuestion:
    """Structured assessment question"""
    id: str
    section: str
    category: str
    question_text: str
    question_type: QuestionType
    options: List[Any]
    required: bool
    framework_mapping: Dict[str, str]  # Framework -> Control ID
    scoring_weight: float
    help_text: Optional[str] = None
    conditional_logic: Optional[Dict[str, Any]] = None

@dataclass
class AssessmentSection:
    """Section of the assessment"""
    id: str
    title: str
    description: str
    framework_reference: str
    questions: List[AssessmentQuestion]
    estimated_time: int  # minutes

class StructuredAssessmentBuilder:
    """Builds structured assessment based on industry frameworks"""
    
    def __init__(self):
        self.assessment_sections = self._build_assessment_sections()
        self.framework_mappings = self._initialize_framework_mappings()
    
    def _build_assessment_sections(self) -> List[AssessmentSection]:
        """Build comprehensive assessment sections"""
        
        sections = []
        
        # 1. Company Profile & Context
        sections.append(self._build_company_profile_section())
        
        # 2. Governance & Risk Management (NIST CSF: Identify)
        sections.append(self._build_governance_section())
        
        # 3. Asset Management (NIST CSF: Identify)
        sections.append(self._build_asset_management_section())
        
        # 4. Data Protection (ISO 27001: A.13, A.18)
        sections.append(self._build_data_protection_section())
        
        # 5. Access Control (NIST CSF: Protect, CIS Control 6)
        sections.append(self._build_access_control_section())
        
        # 6. Security Monitoring (NIST CSF: Detect, CIS Control 8)
        sections.append(self._build_monitoring_section())
        
        # 7. Incident Response (NIST CSF: Respond, ISO 27001: A.16)
        sections.append(self._build_incident_response_section())
        
        # 8. Business Continuity (NIST CSF: Recover, ISO 27001: A.17)
        sections.append(self._build_business_continuity_section())
        
        # 9. Security Awareness & Training (CIS Control 17)
        sections.append(self._build_security_awareness_section())
        
        # 10. Emerging Technology Governance
        sections.append(self._build_emerging_tech_section())
        
        return sections
    
    def _build_company_profile_section(self) -> AssessmentSection:
        """Build company profile section"""
        
        questions = [
            AssessmentQuestion(
                id="company_industry",
                section="profile",
                category="company_context",
                question_text="What industry does your organization operate in?",
                question_type=QuestionType.DROPDOWN,
                options=[
                    "Financial Services", "Healthcare", "Technology", "Manufacturing",
                    "Government", "Education", "Retail", "Energy & Utilities",
                    "Telecommunications", "Transportation", "Other"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.BE-3", "ISO_27001": "A.6.1.1"},
                scoring_weight=0.0,
                help_text="Industry determines applicable regulations and threat landscape"
            ),
            AssessmentQuestion(
                id="company_size",
                section="profile",
                category="company_context",
                question_text="What is your organization's size?",
                question_type=QuestionType.DROPDOWN,
                options=[
                    "Startup (1-50 employees)",
                    "Small Business (51-250 employees)",
                    "Medium Enterprise (251-1000 employees)",
                    "Large Enterprise (1001-5000 employees)",
                    "Very Large Enterprise (5000+ employees)"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.BE-1", "ISO_27001": "A.6.1.1"},
                scoring_weight=0.0,
                help_text="Organization size affects resource allocation and risk profile"
            ),
            AssessmentQuestion(
                id="regulatory_requirements",
                section="profile",
                category="compliance",
                question_text="Which regulatory frameworks apply to your organization?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "GDPR (General Data Protection Regulation)",
                    "HIPAA (Health Insurance Portability and Accountability Act)",
                    "SOX (Sarbanes-Oxley Act)",
                    "PCI DSS (Payment Card Industry Data Security Standard)",
                    "FISMA (Federal Information Security Management Act)",
                    "CCPA (California Consumer Privacy Act)",
                    "ISO 27001",
                    "NIST Cybersecurity Framework",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.GV-3", "ISO_27001": "A.18.1.1"},
                scoring_weight=0.0,
                help_text="Regulatory requirements drive mandatory security controls"
            )
        ]
        
        return AssessmentSection(
            id="company_profile",
            title="Company Profile & Context",
            description="Basic information about your organization's industry, size, and regulatory environment",
            framework_reference="NIST CSF: Identify Function",
            questions=questions,
            estimated_time=5
        )
    
    def _build_governance_section(self) -> AssessmentSection:
        """Build governance and risk management section"""
        
        questions = [
            AssessmentQuestion(
                id="governance_framework",
                section="governance",
                category="risk_management",
                question_text="What is the maturity level of your cybersecurity governance framework?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal governance framework exists",
                    "Basic governance policies documented but not consistently applied",
                    "Formal governance framework defined and documented",
                    "Governance framework actively managed and monitored",
                    "Governance framework continuously optimized and improved"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.GV-1", "ISO_27001": "A.5.1.1"},
                scoring_weight=0.15,
                help_text="Governance framework provides structure for cybersecurity decision-making"
            ),
            AssessmentQuestion(
                id="risk_assessment_process",
                section="governance",
                category="risk_management",
                question_text="How frequently does your organization conduct formal cybersecurity risk assessments?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Never or ad-hoc only",
                    "Only when required by regulations or incidents",
                    "Annually",
                    "Quarterly",
                    "Monthly or continuous monitoring"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.RA-1", "ISO_27001": "A.12.6.1"},
                scoring_weight=0.12,
                help_text="Regular risk assessments ensure current threat landscape is understood"
            ),
            AssessmentQuestion(
                id="board_oversight",
                section="governance",
                category="leadership",
                question_text="What level of cybersecurity oversight exists at the board/executive level?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No board-level cybersecurity oversight",
                    "Cybersecurity mentioned in board meetings occasionally",
                    "Regular cybersecurity updates provided to board",
                    "Dedicated board committee for cybersecurity oversight",
                    "Board actively involved in cybersecurity strategy and decision-making"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.GV-2", "ISO_27001": "A.6.1.1"},
                scoring_weight=0.10,
                help_text="Board oversight ensures cybersecurity is treated as business priority"
            ),
            AssessmentQuestion(
                id="policy_management",
                section="governance",
                category="policies",
                question_text="How are cybersecurity policies managed in your organization?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal cybersecurity policies exist",
                    "Basic policies exist but are outdated or not enforced",
                    "Policies are documented and reviewed annually",
                    "Policies are actively managed with regular updates and training",
                    "Policies are continuously monitored and automatically updated"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.GV-1", "ISO_27001": "A.5.1.2"},
                scoring_weight=0.08,
                help_text="Policy management ensures consistent application of security controls"
            )
        ]
        
        return AssessmentSection(
            id="governance",
            title="Governance & Risk Management",
            description="Leadership, policies, and risk management processes",
            framework_reference="NIST CSF: Identify Function (ID.GV, ID.RA)",
            questions=questions,
            estimated_time=10
        )
    
    def _build_asset_management_section(self) -> AssessmentSection:
        """Build asset management section"""
        
        questions = [
            AssessmentQuestion(
                id="asset_inventory",
                section="assets",
                category="inventory",
                question_text="What is the completeness of your IT asset inventory?",
                question_type=QuestionType.SCALE,
                options=list(range(1, 11)),  # 1-10 scale
                required=True,
                framework_mapping={"NIST_CSF": "ID.AM-1", "ISO_27001": "A.8.1.1", "CIS": "Control 1"},
                scoring_weight=0.12,
                help_text="Scale: 1 = No inventory, 10 = Complete real-time inventory of all assets"
            ),
            AssessmentQuestion(
                id="asset_classification",
                section="assets",
                category="classification",
                question_text="How are your information assets classified and labeled?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No asset classification system in place",
                    "Basic classification (e.g., public, internal, confidential)",
                    "Defined classification scheme with documented criteria",
                    "Classification actively enforced with automated labeling",
                    "Dynamic classification with continuous monitoring and adjustment"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.AM-5", "ISO_27001": "A.8.2.1"},
                scoring_weight=0.10,
                help_text="Asset classification drives appropriate protection measures"
            ),
            AssessmentQuestion(
                id="software_inventory",
                section="assets",
                category="inventory",
                question_text="How well do you maintain an inventory of authorized software?",
                question_type=QuestionType.SCALE,
                options=list(range(1, 11)),
                required=True,
                framework_mapping={"NIST_CSF": "ID.AM-2", "CIS": "Control 2"},
                scoring_weight=0.08,
                help_text="Scale: 1 = No software inventory, 10 = Complete automated software inventory"
            )
        ]
        
        return AssessmentSection(
            id="asset_management",
            title="Asset Management",
            description="Identification and classification of organizational assets",
            framework_reference="NIST CSF: Identify Function (ID.AM), CIS Controls 1-2",
            questions=questions,
            estimated_time=8
        )
    
    def _build_data_protection_section(self) -> AssessmentSection:
        """Build data protection section"""
        
        questions = [
            AssessmentQuestion(
                id="data_encryption",
                section="data_protection",
                category="encryption",
                question_text="What is the extent of data encryption in your organization?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "Data at rest encryption",
                    "Data in transit encryption",
                    "Database encryption",
                    "Email encryption",
                    "Backup encryption",
                    "Mobile device encryption",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.DS-1", "ISO_27001": "A.13.1.1"},
                scoring_weight=0.15,
                help_text="Multiple layers of encryption provide defense in depth"
            ),
            AssessmentQuestion(
                id="data_backup",
                section="data_protection",
                category="backup",
                question_text="How frequently are critical data backups performed and tested?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No regular backup process",
                    "Monthly backups, no testing",
                    "Weekly backups, annual testing",
                    "Daily backups, quarterly testing",
                    "Continuous/real-time backups, monthly testing"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.DS-4", "ISO_27001": "A.12.3.1"},
                scoring_weight=0.12,
                help_text="Regular backups and testing ensure data recovery capabilities"
            ),
            AssessmentQuestion(
                id="data_loss_prevention",
                section="data_protection",
                category="dlp",
                question_text="What data loss prevention (DLP) measures are in place?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "Network-based DLP",
                    "Endpoint DLP",
                    "Cloud DLP",
                    "Email DLP",
                    "Web DLP",
                    "Database activity monitoring",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.DS-3", "ISO_27001": "A.13.2.1"},
                scoring_weight=0.10,
                help_text="DLP prevents unauthorized data exfiltration"
            )
        ]
        
        return AssessmentSection(
            id="data_protection",
            title="Data Protection",
            description="Safeguarding of information assets through encryption, backup, and loss prevention",
            framework_reference="NIST CSF: Protect Function (PR.DS), ISO 27001: A.13",
            questions=questions,
            estimated_time=12
        )
    
    def _build_access_control_section(self) -> AssessmentSection:
        """Build access control section"""
        
        questions = [
            AssessmentQuestion(
                id="multi_factor_auth",
                section="access_control",
                category="authentication",
                question_text="Where is multi-factor authentication (MFA) implemented?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "All administrative accounts",
                    "All user accounts",
                    "Remote access (VPN)",
                    "Cloud services",
                    "Critical applications",
                    "Privileged access management",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.AC-1", "ISO_27001": "A.9.4.2", "CIS": "Control 6"},
                scoring_weight=0.15,
                help_text="MFA significantly reduces risk of account compromise"
            ),
            AssessmentQuestion(
                id="privileged_access",
                section="access_control",
                category="privileged_access",
                question_text="How is privileged access managed in your organization?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal privileged access management",
                    "Shared privileged accounts with basic controls",
                    "Individual privileged accounts with logging",
                    "Privileged access management (PAM) solution implemented",
                    "Just-in-time privileged access with full monitoring and approval"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.AC-4", "ISO_27001": "A.9.2.3"},
                scoring_weight=0.12,
                help_text="Privileged access management prevents unauthorized administrative actions"
            ),
            AssessmentQuestion(
                id="access_reviews",
                section="access_control",
                category="governance",
                question_text="How frequently are user access rights reviewed and updated?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Never or only when issues are discovered",
                    "When employees leave the organization",
                    "Annually for all users",
                    "Quarterly for privileged users, annually for others",
                    "Monthly or automated continuous monitoring"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.AC-4", "ISO_27001": "A.9.2.6"},
                scoring_weight=0.10,
                help_text="Regular access reviews prevent privilege creep and unauthorized access"
            )
        ]
        
        return AssessmentSection(
            id="access_control",
            title="Access Control",
            description="Authentication, authorization, and privileged access management",
            framework_reference="NIST CSF: Protect Function (PR.AC), ISO 27001: A.9, CIS Control 6",
            questions=questions,
            estimated_time=10
        )
    
    def _build_monitoring_section(self) -> AssessmentSection:
        """Build security monitoring section"""
        
        questions = [
            AssessmentQuestion(
                id="log_management",
                section="monitoring",
                category="logging",
                question_text="What is the scope of your security logging and monitoring?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "Network traffic logging",
                    "System event logging",
                    "Application logging",
                    "Database activity logging",
                    "User activity logging",
                    "Cloud service logging",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "DE.AE-3", "ISO_27001": "A.12.4.1", "CIS": "Control 8"},
                scoring_weight=0.12,
                help_text="Comprehensive logging provides visibility into security events"
            ),
            AssessmentQuestion(
                id="siem_capability",
                section="monitoring",
                category="siem",
                question_text="What security information and event management (SIEM) capabilities do you have?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No SIEM or centralized logging",
                    "Basic log aggregation without correlation",
                    "SIEM with basic correlation rules",
                    "SIEM with advanced analytics and threat detection",
                    "AI-powered SIEM with automated response capabilities"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "DE.AE-2", "ISO_27001": "A.12.4.1"},
                scoring_weight=0.15,
                help_text="SIEM provides centralized visibility and correlation of security events"
            ),
            AssessmentQuestion(
                id="threat_detection",
                section="monitoring",
                category="detection",
                question_text="What threat detection capabilities are deployed?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "Intrusion detection system (IDS)",
                    "Intrusion prevention system (IPS)",
                    "Endpoint detection and response (EDR)",
                    "Network detection and response (NDR)",
                    "User behavior analytics (UBA)",
                    "Threat intelligence feeds",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "DE.CM-1", "ISO_27001": "A.12.4.1"},
                scoring_weight=0.13,
                help_text="Multiple detection technologies provide layered security monitoring"
            )
        ]
        
        return AssessmentSection(
            id="monitoring",
            title="Security Monitoring & Detection",
            description="Continuous monitoring and threat detection capabilities",
            framework_reference="NIST CSF: Detect Function (DE.AE, DE.CM), CIS Control 8",
            questions=questions,
            estimated_time=10
        )
    
    def _build_incident_response_section(self) -> AssessmentSection:
        """Build incident response section"""
        
        questions = [
            AssessmentQuestion(
                id="incident_response_plan",
                section="incident_response",
                category="planning",
                question_text="What is the maturity level of your incident response plan?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal incident response plan",
                    "Basic incident response procedures documented",
                    "Comprehensive plan with defined roles and responsibilities",
                    "Plan regularly tested and updated with lessons learned",
                    "Continuously optimized plan with automated response capabilities"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.16.1.1"},
                scoring_weight=0.15,
                help_text="Incident response plan ensures coordinated response to security incidents"
            ),
            AssessmentQuestion(
                id="incident_response_team",
                section="incident_response",
                category="organization",
                question_text="Do you have a dedicated incident response team?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No dedicated team or roles",
                    "Informal team with basic training",
                    "Formal team with defined roles and basic training",
                    "Dedicated team with regular training and exercises",
                    "Highly skilled team with advanced training and 24/7 capability"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.16.1.1"},
                scoring_weight=0.12,
                help_text="Trained incident response team ensures effective incident handling"
            ),
            AssessmentQuestion(
                id="incident_testing",
                section="incident_response",
                category="testing",
                question_text="How frequently do you test your incident response capabilities?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Never tested",
                    "Only after actual incidents",
                    "Annual tabletop exercises",
                    "Quarterly exercises with different scenarios",
                    "Monthly exercises with automated testing"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "RS.RP-1", "ISO_27001": "A.16.1.7"},
                scoring_weight=0.10,
                help_text="Regular testing ensures incident response plan effectiveness"
            )
        ]
        
        return AssessmentSection(
            id="incident_response",
            title="Incident Response",
            description="Preparation, detection, and response to security incidents",
            framework_reference="NIST CSF: Respond Function (RS.RP), ISO 27001: A.16",
            questions=questions,
            estimated_time=8
        )
    
    def _build_business_continuity_section(self) -> AssessmentSection:
        """Build business continuity section"""
        
        questions = [
            AssessmentQuestion(
                id="business_continuity_plan",
                section="continuity",
                category="planning",
                question_text="What is the maturity of your business continuity/disaster recovery plan?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal business continuity plan",
                    "Basic disaster recovery procedures documented",
                    "Comprehensive plan with defined recovery objectives",
                    "Plan regularly tested with documented recovery capabilities",
                    "Continuously optimized plan with automated failover"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "RC.RP-1", "ISO_27001": "A.17.1.1"},
                scoring_weight=0.15,
                help_text="Business continuity plan ensures recovery from disruptions"
            ),
            AssessmentQuestion(
                id="backup_testing",
                section="continuity",
                category="testing",
                question_text="How frequently are backup and recovery procedures tested?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Never tested",
                    "Only when needed for actual recovery",
                    "Annual testing of critical systems",
                    "Quarterly testing with documented results",
                    "Monthly automated testing with verified recovery"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "RC.RP-1", "ISO_27001": "A.17.1.3"},
                scoring_weight=0.12,
                help_text="Regular testing ensures recovery capabilities work when needed"
            )
        ]
        
        return AssessmentSection(
            id="business_continuity",
            title="Business Continuity & Recovery",
            description="Preparation for and recovery from business disruptions",
            framework_reference="NIST CSF: Recover Function (RC.RP), ISO 27001: A.17",
            questions=questions,
            estimated_time=6
        )
    
    def _build_security_awareness_section(self) -> AssessmentSection:
        """Build security awareness section"""
        
        questions = [
            AssessmentQuestion(
                id="security_training",
                section="awareness",
                category="training",
                question_text="What is the frequency and scope of security awareness training?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal security training program",
                    "Basic security briefing during onboarding only",
                    "Annual security awareness training for all employees",
                    "Regular training with role-specific content and testing",
                    "Continuous security education with personalized content"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2", "CIS": "Control 17"},
                scoring_weight=0.12,
                help_text="Regular training keeps employees aware of current threats"
            ),
            AssessmentQuestion(
                id="phishing_testing",
                section="awareness",
                category="testing",
                question_text="Do you conduct phishing simulation exercises?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No phishing simulations",
                    "Annual phishing simulations",
                    "Quarterly phishing simulations",
                    "Monthly phishing simulations with targeted training",
                    "Continuous phishing simulations with personalized training"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.AT-1", "ISO_27001": "A.7.2.2"},
                scoring_weight=0.10,
                help_text="Phishing simulations test and improve employee awareness"
            )
        ]
        
        return AssessmentSection(
            id="security_awareness",
            title="Security Awareness & Training",
            description="Employee education and awareness programs",
            framework_reference="NIST CSF: Protect Function (PR.AT), CIS Control 17",
            questions=questions,
            estimated_time=5
        )
    
    def _build_emerging_tech_section(self) -> AssessmentSection:
        """Build emerging technology governance section"""
        
        questions = [
            AssessmentQuestion(
                id="emerging_tech_governance",
                section="emerging_tech",
                category="governance",
                question_text="How does your organization govern the adoption of emerging technologies?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "No formal governance for emerging technologies",
                    "Basic approval process for new technology adoption",
                    "Defined governance framework with risk assessment",
                    "Comprehensive governance with security integration",
                    "Advanced governance with continuous monitoring and optimization"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "ID.GV-1", "ISO_27001": "A.14.1.1"},
                scoring_weight=0.12,
                help_text="Governance ensures emerging technologies are adopted securely"
            ),
            AssessmentQuestion(
                id="ai_governance",
                section="emerging_tech",
                category="ai",
                question_text="What AI governance measures are in place?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "AI ethics guidelines",
                    "AI risk assessment procedures",
                    "AI model validation and testing",
                    "AI data governance",
                    "AI bias detection and mitigation",
                    "AI transparency and explainability",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_AI": "GOVERN-1.1", "ISO_27001": "A.14.1.1"},
                scoring_weight=0.10,
                help_text="AI governance ensures responsible AI implementation"
            ),
            AssessmentQuestion(
                id="cloud_security",
                section="emerging_tech",
                category="cloud",
                question_text="What cloud security measures are implemented?",
                question_type=QuestionType.CHECKLIST,
                options=[
                    "Cloud security posture management (CSPM)",
                    "Cloud access security broker (CASB)",
                    "Cloud workload protection",
                    "Cloud identity and access management",
                    "Cloud security monitoring",
                    "Multi-cloud security management",
                    "None of the above"
                ],
                required=True,
                framework_mapping={"NIST_CSF": "PR.AC-5", "ISO_27001": "A.14.1.1"},
                scoring_weight=0.08,
                help_text="Cloud security measures protect cloud-based assets and workloads"
            )
        ]
        
        return AssessmentSection(
            id="emerging_technology",
            title="Emerging Technology Governance",
            description="Governance and security for AI, cloud, and other emerging technologies",
            framework_reference="NIST AI RMF, NIST CSF: Identify Function",
            questions=questions,
            estimated_time=8
        )
    
    def _initialize_framework_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize framework mappings"""
        
        return {
            "NIST_CSF": {
                "name": "NIST Cybersecurity Framework",
                "version": "1.1",
                "url": "https://www.nist.gov/cyberframework"
            },
            "ISO_27001": {
                "name": "ISO/IEC 27001:2013",
                "version": "2013",
                "url": "https://www.iso.org/isoiec-27001-information-security.html"
            },
            "CIS": {
                "name": "CIS Controls",
                "version": "8",
                "url": "https://www.cisecurity.org/controls/"
            },
            "NIST_AI": {
                "name": "NIST AI Risk Management Framework",
                "version": "1.0",
                "url": "https://www.nist.gov/itl/ai-risk-management-framework"
            }
        }
    
    def get_full_assessment(self) -> Dict[str, Any]:
        """Get complete structured assessment"""
        
        return {
            "assessment_info": {
                "title": "Cybersecurity Risk Assessment",
                "description": "Comprehensive assessment based on industry frameworks",
                "version": "2.0",
                "frameworks": list(self.framework_mappings.keys()),
                "estimated_time": sum(section.estimated_time for section in self.assessment_sections)
            },
            "sections": [asdict(section) for section in self.assessment_sections],
            "framework_mappings": self.framework_mappings
        }
    
    def get_section(self, section_id: str) -> Optional[AssessmentSection]:
        """Get specific assessment section"""
        
        return next((section for section in self.assessment_sections if section.id == section_id), None)
    
    def calculate_section_score(self, section_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score for a specific section"""
        
        section = self.get_section(section_id)
        if not section:
            return {"error": f"Section {section_id} not found"}
        
        total_score = 0.0
        max_score = 0.0
        question_scores = []
        
        for question in section.questions:
            if question.id in responses:
                response = responses[question.id]
                question_score = self._calculate_question_score(question, response)
                weighted_score = question_score * question.scoring_weight
                
                total_score += weighted_score
                max_score += question.scoring_weight
                
                question_scores.append({
                    "question_id": question.id,
                    "raw_score": question_score,
                    "weighted_score": weighted_score,
                    "weight": question.scoring_weight
                })
        
        normalized_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        return {
            "section_id": section_id,
            "section_title": section.title,
            "normalized_score": normalized_score,
            "raw_score": total_score,
            "max_score": max_score,
            "question_scores": question_scores
        }
    
    def _calculate_question_score(self, question: AssessmentQuestion, response: Any) -> float:
        """Calculate score for individual question"""
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            # Score based on option index (higher index = better score)
            if isinstance(response, str):
                try:
                    option_index = question.options.index(response)
                    return (option_index / (len(question.options) - 1)) * 10
                except ValueError:
                    return 0.0
            return 0.0
        
        elif question.question_type == QuestionType.SCALE:
            # Direct score mapping
            if isinstance(response, (int, float)):
                return float(response)
            return 0.0
        
        elif question.question_type == QuestionType.BOOLEAN:
            # Boolean scoring
            return 10.0 if response else 0.0
        
        elif question.question_type == QuestionType.CHECKLIST:
            # Score based on percentage of items selected
            if isinstance(response, list):
                selected_count = len([item for item in response if item != "None of the above"])
                total_options = len(question.options) - 1  # Exclude "None of the above"
                return (selected_count / total_options) * 10 if total_options > 0 else 0.0
            return 0.0
        
        elif question.question_type == QuestionType.DROPDOWN:
            # For dropdown, treat as multiple choice
            if isinstance(response, str):
                try:
                    option_index = question.options.index(response)
                    return (option_index / (len(question.options) - 1)) * 10
                except ValueError:
                    return 0.0
            return 0.0
        
        return 0.0

# Global instance
structured_assessment = StructuredAssessmentBuilder()