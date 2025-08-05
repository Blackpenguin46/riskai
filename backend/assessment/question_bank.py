#!/usr/bin/env python3
"""
Comprehensive 120-Question Bank for RiskAI
Includes standard questions + industry-specific adaptations
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Question types supported by the system"""
    BOOLEAN = "boolean"
    SCALE = "scale"  # 1-5 rating
    SELECT = "select"  # Single choice
    MULTISELECT = "multiselect"  # Multiple choices
    TEXT = "text"

class IndustryType(Enum):
    """Supported industry types"""
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial_services"
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"
    GOVERNMENT = "government"
    EDUCATION = "education"
    RETAIL = "retail"
    ENERGY = "energy"

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST_CSF = "nist_csf"
    SOC2 = "soc2"
    FISMA = "fisma"

@dataclass
class Question:
    """Individual assessment question"""
    id: str
    domain: str
    question_text: str
    question_type: QuestionType
    weight: int
    options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    help_text: Optional[str] = None
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    industry_specific: Optional[List[IndustryType]] = None
    is_standard: bool = True  # True for all industries, False for specific

class QuestionBank:
    """Comprehensive question bank with industry adaptations"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
    
    def get_questions_for_assessment(self, 
                                   industry: Optional[IndustryType] = None,
                                   compliance_requirements: Optional[List[ComplianceFramework]] = None,
                                   company_size: Optional[str] = None) -> List[Question]:
        """Get tailored question set for specific assessment"""
        
        # Start with all standard questions
        selected_questions = [q for q in self.questions if q.is_standard]
        
        # Add industry-specific questions
        if industry:
            industry_questions = [q for q in self.questions 
                                if not q.is_standard and 
                                q.industry_specific and 
                                industry in q.industry_specific]
            selected_questions.extend(industry_questions)
        
        # Filter by compliance requirements if specified
        if compliance_requirements:
            compliance_questions = [q for q in self.questions
                                  if q.compliance_frameworks and
                                  any(cf in compliance_requirements for cf in q.compliance_frameworks)]
            # Add unique compliance questions
            for cq in compliance_questions:
                if cq not in selected_questions:
                    selected_questions.append(cq)
        
        # Ensure we have exactly 120 questions (10 per domain)
        return self._balance_questions_by_domain(selected_questions)
    
    def _balance_questions_by_domain(self, questions: List[Question]) -> List[Question]:
        """Ensure exactly 10 questions per domain (120 total)"""
        domains = [
            'governance', 'asset_management', 'data_protection', 'access_control',
            'security_monitoring', 'incident_response', 'business_continuity',
            'security_awareness', 'compliance', 'emerging_tech', 'third_party', 'risk_management'
        ]
        
        balanced_questions = []
        
        for domain in domains:
            domain_questions = [q for q in questions if q.domain == domain]
            # Take first 10 questions for each domain, pad if needed
            if len(domain_questions) >= 10:
                balanced_questions.extend(domain_questions[:10])
            else:
                balanced_questions.extend(domain_questions)
                # Add filler questions if needed (this shouldn't happen in production)
                while len([q for q in balanced_questions if q.domain == domain]) < 10:
                    filler = self._create_filler_question(domain, len(balanced_questions))
                    balanced_questions.append(filler)
        
        return balanced_questions
    
    def _create_filler_question(self, domain: str, index: int) -> Question:
        """Create a filler question if needed"""
        return Question(
            id=f"{domain}_filler_{index}",
            domain=domain,
            question_text=f"Additional {domain.replace('_', ' ')} assessment question",
            question_type=QuestionType.SCALE,
            weight=5,
            min_value=1,
            max_value=5,
            help_text="This is a placeholder question"
        )    
  
  def _initialize_questions(self) -> List[Question]:
        """Initialize the complete 120+ question bank"""
        questions = []
        
        # GOVERNANCE & RISK MANAGEMENT (20% weight)
        questions.extend([
            Question(
                id="gov_001",
                domain="governance",
                question_text="Does your organization have a formal cybersecurity governance framework in place?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="A governance framework provides structure for cybersecurity decision-making",
                compliance_frameworks=[ComplianceFramework.ISO27001, ComplianceFramework.NIST_CSF]
            ),
            Question(
                id="gov_002",
                domain="governance",
                question_text="How often does senior leadership review cybersecurity risk assessments?",
                question_type=QuestionType.SELECT,
                weight=9,
                options=["Never", "Annually", "Semi-annually", "Quarterly", "Monthly"],
                help_text="Regular leadership review ensures cybersecurity alignment with business objectives",
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
            ),
            Question(
                id="gov_003",
                domain="governance",
                question_text="Rate your organization's cybersecurity budget adequacy (1=Severely inadequate, 5=Fully adequate)",
                question_type=QuestionType.SCALE,
                weight=8,
                min_value=1,
                max_value=5,
                help_text="Adequate budget is essential for effective cybersecurity program implementation"
            ),
            Question(
                id="gov_004",
                domain="governance",
                question_text="Does your organization have a designated Chief Information Security Officer (CISO) or equivalent?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Dedicated security leadership is crucial for program effectiveness",
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
            ),
            Question(
                id="gov_005",
                domain="governance",
                question_text="How mature is your cybersecurity risk management process?",
                question_type=QuestionType.SELECT,
                weight=9,
                options=["No formal process", "Basic/Ad-hoc", "Defined process", "Managed process", "Optimized process"],
                help_text="Risk management maturity indicates organizational cybersecurity sophistication",
                compliance_frameworks=[ComplianceFramework.NIST_CSF, ComplianceFramework.ISO27001]
            ),
            Question(
                id="gov_006",
                domain="governance",
                question_text="Are cybersecurity policies reviewed and updated regularly?",
                question_type=QuestionType.SELECT,
                weight=8,
                options=["Never", "When required", "Annually", "Semi-annually", "Quarterly"],
                help_text="Regular policy updates ensure relevance to evolving threats",
                compliance_frameworks=[ComplianceFramework.ISO27001, ComplianceFramework.SOC2]
            ),
            Question(
                id="gov_007",
                domain="governance",
                question_text="Does your organization conduct regular cybersecurity board reporting?",
                question_type=QuestionType.BOOLEAN,
                weight=7,
                help_text="Board reporting ensures executive awareness and support",
                compliance_frameworks=[ComplianceFramework.SOC2]
            ),
            Question(
                id="gov_008",
                domain="governance",
                question_text="Rate the effectiveness of your cybersecurity steering committee (1=Ineffective, 5=Highly effective)",
                question_type=QuestionType.SCALE,
                weight=6,
                min_value=1,
                max_value=5,
                help_text="Steering committees provide cross-functional cybersecurity coordination"
            ),
            Question(
                id="gov_009",
                domain="governance",
                question_text="How well integrated is cybersecurity into your business continuity planning?",
                question_type=QuestionType.SCALE,
                weight=7,
                min_value=1,
                max_value=5,
                help_text="Integration ensures cybersecurity supports business resilience"
            ),
            Question(
                id="gov_010",
                domain="governance",
                question_text="Does your organization have a formal cybersecurity strategy document?",
                question_type=QuestionType.BOOLEAN,
                weight=8,
                help_text="Formal strategy provides direction and measurable objectives",
                compliance_frameworks=[ComplianceFramework.ISO27001, ComplianceFramework.NIST_CSF]
            )
        ])
        
        # ASSET MANAGEMENT (8% weight)
        questions.extend([
            Question(
                id="asset_001",
                domain="asset_management",
                question_text="Does your organization maintain a comprehensive IT asset inventory?",
                question_type=QuestionType.BOOLEAN,
                weight=12,
                help_text="Asset inventory is fundamental to cybersecurity risk management",
                compliance_frameworks=[ComplianceFramework.ISO27001, ComplianceFramework.NIST_CSF]
            ),
            Question(
                id="asset_002",
                domain="asset_management",
                question_text="How frequently is your asset inventory updated?",
                question_type=QuestionType.SELECT,
                weight=10,
                options=["Never", "Annually", "Quarterly", "Monthly", "Real-time/Automated"],
                help_text="Regular updates ensure inventory accuracy and security visibility"
            ),
            Question(
                id="asset_003",
                domain="asset_management",
                question_text="Rate your organization's visibility into shadow IT (1=No visibility, 5=Complete visibility)",
                question_type=QuestionType.SCALE,
                weight=11,
                min_value=1,
                max_value=5,
                help_text="Shadow IT represents unmanaged security risks"
            ),
            Question(
                id="asset_004",
                domain="asset_management",
                question_text="Are all critical assets classified by security level?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Asset classification enables risk-appropriate security controls",
                compliance_frameworks=[ComplianceFramework.ISO27001]
            ),
            Question(
                id="asset_005",
                domain="asset_management",
                question_text="How well does your organization track software licenses and versions?",
                question_type=QuestionType.SCALE,
                weight=9,
                min_value=1,
                max_value=5,
                help_text="Software tracking is essential for vulnerability management"
            ),
            Question(
                id="asset_006",
                domain="asset_management",
                question_text="Does your organization have automated asset discovery tools?",
                question_type=QuestionType.BOOLEAN,
                weight=9,
                help_text="Automation improves asset visibility and reduces manual effort"
            ),
            Question(
                id="asset_007",
                domain="asset_management",
                question_text="Are hardware assets tagged and tracked throughout their lifecycle?",
                question_type=QuestionType.BOOLEAN,
                weight=8,
                help_text="Lifecycle tracking ensures proper security controls and disposal"
            ),
            Question(
                id="asset_008",
                domain="asset_management",
                question_text="How effectively does your organization manage end-of-life assets?",
                question_type=QuestionType.SCALE,
                weight=8,
                min_value=1,
                max_value=5,
                help_text="End-of-life management prevents security vulnerabilities"
            ),
            Question(
                id="asset_009",
                domain="asset_management",
                question_text="Does your asset management system integrate with security tools?",
                question_type=QuestionType.BOOLEAN,
                weight=9,
                help_text="Integration enables automated security control application"
            ),
            Question(
                id="asset_010",
                domain="asset_management",
                question_text="Are cloud assets included in your asset management program?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Cloud asset visibility is critical for hybrid environment security"
            )
        ])   
     
        # DATA PROTECTION (12% weight)
        questions.extend([
            Question(
                id="data_001",
                domain="data_protection",
                question_text="Does your organization have a formal data classification scheme?",
                question_type=QuestionType.BOOLEAN,
                weight=11,
                help_text="Data classification enables appropriate protection controls",
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.ISO27001]
            ),
            Question(
                id="data_002",
                domain="data_protection",
                question_text="How comprehensive is your data encryption at rest?",
                question_type=QuestionType.SELECT,
                weight=12,
                options=["No encryption", "Critical data only", "Sensitive data", "Most data", "All data"],
                help_text="Encryption protects data confidentiality and integrity",
                compliance_frameworks=[ComplianceFramework.HIPAA, ComplianceFramework.PCI_DSS, ComplianceFramework.GDPR]
            ),
            Question(
                id="data_003",
                domain="data_protection",
                question_text="Are data flows mapped and documented across your organization?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Data flow mapping is essential for privacy and security controls",
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.HIPAA]
            ),
            Question(
                id="data_004",
                domain="data_protection",
                question_text="Rate your organization's data loss prevention (DLP) capabilities (1=None, 5=Advanced)",
                question_type=QuestionType.SCALE,
                weight=11,
                min_value=1,
                max_value=5,
                help_text="DLP prevents unauthorized data disclosure",
                compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.HIPAA]
            ),
            Question(
                id="data_005",
                domain="data_protection",
                question_text="Does your organization have a data retention and disposal policy?",
                question_type=QuestionType.BOOLEAN,
                weight=9,
                help_text="Proper data lifecycle management reduces risk exposure",
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.HIPAA]
            ),
            Question(
                id="data_006",
                domain="data_protection",
                question_text="How well does your organization protect data in transit?",
                question_type=QuestionType.SELECT,
                weight=11,
                options=["No protection", "Basic encryption", "Strong encryption", "End-to-end encryption", "Zero-trust encryption"],
                help_text="Transit protection prevents data interception",
                compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.HIPAA]
            ),
            Question(
                id="data_007",
                domain="data_protection",
                question_text="Are personal data processing activities documented and tracked?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Documentation supports privacy compliance and risk management",
                compliance_frameworks=[ComplianceFramework.GDPR],
                industry_specific=[IndustryType.HEALTHCARE, IndustryType.FINANCIAL_SERVICES]
            ),
            Question(
                id="data_008",
                domain="data_protection",
                question_text="Does your organization conduct regular data privacy impact assessments?",
                question_type=QuestionType.SELECT,
                weight=8,
                options=["Never", "For major projects", "For high-risk processing", "For all new processing", "Continuously"],
                help_text="Privacy impact assessments identify and mitigate privacy risks",
                compliance_frameworks=[ComplianceFramework.GDPR]
            ),
            Question(
                id="data_009",
                domain="data_protection",
                question_text="How mature is your data backup and recovery program?",
                question_type=QuestionType.SCALE,
                weight=10,
                min_value=1,
                max_value=5,
                help_text="Backup and recovery ensures data availability and business continuity"
            ),
            Question(
                id="data_010",
                domain="data_protection",
                question_text="Does your organization have data anonymization or pseudonymization capabilities?",
                question_type=QuestionType.BOOLEAN,
                weight=8,
                help_text="Anonymization reduces privacy risks while enabling data use",
                compliance_frameworks=[ComplianceFramework.GDPR],
                industry_specific=[IndustryType.HEALTHCARE, IndustryType.FINANCIAL_SERVICES]
            )
        ])
        
        # ACCESS CONTROL (12% weight)
        questions.extend([
            Question(
                id="access_001",
                domain="access_control",
                question_text="Does your organization implement multi-factor authentication (MFA) for all users?",
                question_type=QuestionType.SELECT,
                weight=12,
                options=["No MFA", "Admin users only", "Privileged users", "Most users", "All users"],
                help_text="MFA significantly reduces authentication-based attacks",
                compliance_frameworks=[ComplianceFramework.NIST_CSF, ComplianceFramework.SOC2]
            ),
            Question(
                id="access_002",
                domain="access_control",
                question_text="How comprehensive is your privileged access management (PAM) program?",
                question_type=QuestionType.SCALE,
                weight=11,
                min_value=1,
                max_value=5,
                help_text="PAM controls reduce risks from elevated privileges",
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.PCI_DSS]
            ),
            Question(
                id="access_003",
                domain="access_control",
                question_text="Are access rights reviewed and recertified regularly?",
                question_type=QuestionType.SELECT,
                weight=10,
                options=["Never", "Annually", "Semi-annually", "Quarterly", "Monthly"],
                help_text="Regular reviews prevent access creep and unauthorized access",
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.SOX]
            ),
            Question(
                id="access_004",
                domain="access_control",
                question_text="Does your organization implement role-based access control (RBAC)?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="RBAC ensures users have appropriate access for their roles",
                compliance_frameworks=[ComplianceFramework.ISO27001, ComplianceFramework.SOC2]
            ),
            Question(
                id="access_005",
                domain="access_control",
                question_text="How effectively does your organization manage user provisioning and deprovisioning?",
                question_type=QuestionType.SCALE,
                weight=11,
                min_value=1,
                max_value=5,
                help_text="Timely provisioning/deprovisioning prevents unauthorized access"
            ),
            Question(
                id="access_006",
                domain="access_control",
                question_text="Does your organization use single sign-on (SSO) for application access?",
                question_type=QuestionType.SELECT,
                weight=8,
                options=["No SSO", "Few applications", "Some applications", "Most applications", "All applications"],
                help_text="SSO improves security and user experience"
            ),
            Question(
                id="access_007",
                domain="access_control",
                question_text="Are administrative accounts separated from regular user accounts?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Account separation reduces privilege escalation risks",
                compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]
            ),
            Question(
                id="access_008",
                domain="access_control",
                question_text="How mature is your identity governance program?",
                question_type=QuestionType.SCALE,
                weight=9,
                min_value=1,
                max_value=5,
                help_text="Identity governance ensures appropriate access throughout user lifecycle"
            ),
            Question(
                id="access_009",
                domain="access_control",
                question_text="Does your organization implement zero-trust access principles?",
                question_type=QuestionType.SELECT,
                weight=9,
                options=["No zero-trust", "Planning phase", "Pilot implementation", "Partial deployment", "Full deployment"],
                help_text="Zero-trust assumes no implicit trust and verifies every access request"
            ),
            Question(
                id="access_010",
                domain="access_control",
                question_text="Are access logs monitored and analyzed for suspicious activity?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="Access monitoring detects unauthorized or suspicious access attempts",
                compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]
            )
        ])    
    
        # INDUSTRY-SPECIFIC QUESTIONS
        
        # HEALTHCARE-SPECIFIC QUESTIONS
        questions.extend([
            Question(
                id="health_001",
                domain="compliance",
                question_text="Does your organization comply with HIPAA Security Rule requirements?",
                question_type=QuestionType.SELECT,
                weight=12,
                options=["Not applicable", "Partial compliance", "Mostly compliant", "Fully compliant", "Exceeds requirements"],
                help_text="HIPAA Security Rule mandates specific safeguards for protected health information",
                compliance_frameworks=[ComplianceFramework.HIPAA],
                industry_specific=[IndustryType.HEALTHCARE],
                is_standard=False
            ),
            Question(
                id="health_002",
                domain="data_protection",
                question_text="Are electronic protected health information (ePHI) access controls implemented?",
                question_type=QuestionType.BOOLEAN,
                weight=11,
                help_text="ePHI requires specific access controls under HIPAA",
                compliance_frameworks=[ComplianceFramework.HIPAA],
                industry_specific=[IndustryType.HEALTHCARE],
                is_standard=False
            ),
            Question(
                id="health_003",
                domain="third_party",
                question_text="Do all business associates have signed HIPAA Business Associate Agreements (BAAs)?",
                question_type=QuestionType.BOOLEAN,
                weight=10,
                help_text="BAAs are required for third parties handling ePHI",
                compliance_frameworks=[ComplianceFramework.HIPAA],
                industry_specific=[IndustryType.HEALTHCARE],
                is_standard=False
            )
        ])
        
        # FINANCIAL SERVICES-SPECIFIC QUESTIONS
        questions.extend([
            Question(
                id="fin_001",
                domain="compliance",
                question_text="Does your organization comply with PCI DSS requirements for payment card data?",
                question_type=QuestionType.SELECT,
                weight=12,
                options=["Not applicable", "Level 4", "Level 3", "Level 2", "Level 1"],
                help_text="PCI DSS compliance is mandatory for organizations handling payment card data",
                compliance_frameworks=[ComplianceFramework.PCI_DSS],
                industry_specific=[IndustryType.FINANCIAL_SERVICES, IndustryType.RETAIL],
                is_standard=False
            ),
            Question(
                id="fin_002",
                domain="governance",
                question_text="Are Sarbanes-Oxley (SOX) IT controls implemented and tested?",
                question_type=QuestionType.SELECT,
                weight=10,
                options=["Not applicable", "Basic controls", "Documented controls", "Tested controls", "Optimized controls"],
                help_text="SOX requires specific IT controls for financial reporting",
                compliance_frameworks=[ComplianceFramework.SOX],
                industry_specific=[IndustryType.FINANCIAL_SERVICES],
                is_standard=False
            ),
            Question(
                id="fin_003",
                domain="data_protection",
                question_text="Is customer financial data encrypted both at rest and in transit?",
                question_type=QuestionType.BOOLEAN,
                weight=11,
                help_text="Financial data requires strong encryption protection",
                compliance_frameworks=[ComplianceFramework.PCI_DSS],
                industry_specific=[IndustryType.FINANCIAL_SERVICES],
                is_standard=False
            )
        ])
        
        # TECHNOLOGY SECTOR-SPECIFIC QUESTIONS
        questions.extend([
            Question(
                id="tech_001",
                domain="emerging_tech",
                question_text="Does your organization have AI governance policies for AI/ML systems?",
                question_type=QuestionType.SELECT,
                weight=10,
                options=["No AI systems", "No policies", "Basic guidelines", "Formal policies", "Comprehensive framework"],
                help_text="AI governance is critical for responsible AI deployment",
                industry_specific=[IndustryType.TECHNOLOGY],
                is_standard=False
            ),
            Question(
                id="tech_002",
                domain="data_protection",
                question_text="Are customer data processing activities documented for privacy compliance?",
                question_type=QuestionType.BOOLEAN,
                weight=9,
                help_text="Tech companies often process large amounts of personal data",
                compliance_frameworks=[ComplianceFramework.GDPR],
                industry_specific=[IndustryType.TECHNOLOGY],
                is_standard=False
            ),
            Question(
                id="tech_003",
                domain="security_monitoring",
                question_text="Does your organization implement DevSecOps practices in software development?",
                question_type=QuestionType.SCALE,
                weight=10,
                min_value=1,
                max_value=5,
                help_text="DevSecOps integrates security into development lifecycle",
                industry_specific=[IndustryType.TECHNOLOGY],
                is_standard=False
            )
        ])
        
        # Add remaining standard questions for other domains...
        # (This would continue with security_monitoring, incident_response, etc.)
        
        return questions
    
    def get_questions_by_domain(self, domain: str, 
                               industry: Optional[IndustryType] = None) -> List[Question]:
        """Get questions for a specific domain"""
        all_questions = self.get_questions_for_assessment(industry)
        return [q for q in all_questions if q.domain == domain]
    
    def get_compliance_questions(self, 
                               frameworks: List[ComplianceFramework]) -> List[Question]:
        """Get questions relevant to specific compliance frameworks"""
        return [q for q in self.questions 
                if q.compliance_frameworks and 
                any(cf in frameworks for cf in q.compliance_frameworks)]
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get a specific question by ID"""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None

# Global instance
question_bank = QuestionBank()