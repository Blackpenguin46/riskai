#!/usr/bin/env python3
"""
Enterprise Assessment API
Real enterprise assessment with dynamic scoring
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
import logging
import uuid
from datetime import datetime

from scoring.dynamic_scoring_engine import dynamic_scoring_engine
from assessment.ai_feedback_generator import ai_feedback_generator

logger = logging.getLogger(__name__)

router = APIRouter()

class CompanyProfile(BaseModel):
    name: str
    industry: str
    size: str  # small, medium, large, enterprise
    country: Optional[str] = "US"
    compliance_requirements: List[str] = []
    technology_adoption: str = "medium"
    data_types: List[str] = []
    risk_tolerance: str = "medium"

class AssessmentAnswer(BaseModel):
    question_id: str
    answer: Union[str, int, float, bool]
    section_id: str

class AssessmentSubmission(BaseModel):
    company_profile: CompanyProfile
    answers: List[AssessmentAnswer]

# Complete 120-Question Enterprise Assessment with Dynamic Scoring
ENTERPRISE_QUESTIONS = {
    "governance": {
        "name": "Governance & Risk Management",
        "weight": 0.20,
        "description": "Leadership, policies, and risk management framework",
        "questions": [
            {
                "id": "gov_001",
                "text": "How mature is your organization's cybersecurity governance?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No formal governance", "score": 1},
                    {"value": "basic", "label": "Basic policies exist", "score": 3},
                    {"value": "managed", "label": "Managed with oversight", "score": 6},
                    {"value": "optimized", "label": "Continuously optimized", "score": 10}
                ]
            },
            {
                "id": "gov_002",
                "text": "Rate your cybersecurity budget adequacy (1-10 scale)",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Severely inadequate, 10 = More than sufficient"
            },
            {
                "id": "gov_003",
                "text": "How often does leadership receive cybersecurity risk reports?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never", "score": 1},
                    {"value": "annually", "label": "Annually", "score": 3},
                    {"value": "quarterly", "label": "Quarterly", "score": 7},
                    {"value": "monthly", "label": "Monthly or more", "score": 10}
                ]
            },
            {
                "id": "gov_004",
                "text": "Do you have a designated CISO or equivalent security leader?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "gov_005",
                "text": "Describe your risk assessment process and frequency",
                "type": "text",
                "required": False,
                "placeholder": "Describe how often you assess risks and the process used..."
            },
            {
                "id": "gov_006",
                "text": "How often are cybersecurity policies reviewed and updated?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never or only when required", "score": 1},
                    {"value": "3years", "label": "Every 2-3 years", "score": 3},
                    {"value": "annually", "label": "Annually", "score": 7},
                    {"value": "continuous", "label": "Continuous review process", "score": 10}
                ]
            },
            {
                "id": "gov_007",
                "text": "Does your board receive regular cybersecurity briefings?",
                "type": "boolean",
                "required": True,
                "true_score": 9,
                "false_score": 2
            },
            {
                "id": "gov_008",
                "text": "Rate the effectiveness of your cybersecurity committee/steering group",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No committee exists, 10 = Highly effective committee"
            },
            {
                "id": "gov_009",
                "text": "Do you have documented cybersecurity roles and responsibilities?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 1
            },
            {
                "id": "gov_010",
                "text": "Describe your cybersecurity strategy alignment with business objectives",
                "type": "text",
                "required": False,
                "placeholder": "How does cybersecurity support business goals..."
            },
            {
                "id": "gov_011",
                "text": "Do you have cybersecurity insurance coverage?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "gov_012",
                "text": "Rate your third-party risk management program maturity",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No program, 10 = Comprehensive vendor risk management"
            },
            {
                "id": "gov_013",
                "text": "How often do you conduct cybersecurity maturity assessments?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never", "score": 1},
                    {"value": "3years", "label": "Every 2-3 years", "score": 4},
                    {"value": "annually", "label": "Annually", "score": 7},
                    {"value": "quarterly", "label": "Quarterly", "score": 10}
                ]
            },
            {
                "id": "gov_014",
                "text": "Do you have a formal cybersecurity metrics and KPI program?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "gov_015",
                "text": "Rate your regulatory compliance management capabilities",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Reactive compliance, 10 = Proactive compliance automation"
            }
        ]
    },
    "access_control": {
        "name": "Access Control & Identity Management",
        "weight": 0.15,
        "description": "User access, authentication, and privilege management",
        "questions": [
            {
                "id": "access_001",
                "text": "What percentage of users have multi-factor authentication (MFA)?",
                "type": "percentage",
                "required": True,
                "benchmark": 85  # Industry benchmark
            },
            {
                "id": "access_002",
                "text": "How frequently are access rights reviewed?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never", "score": 1},
                    {"value": "annually", "label": "Annually", "score": 4},
                    {"value": "quarterly", "label": "Quarterly", "score": 7},
                    {"value": "monthly", "label": "Monthly", "score": 9},
                    {"value": "continuous", "label": "Continuous monitoring", "score": 10}
                ]
            },
            {
                "id": "access_003",
                "text": "Rate your privileged access management maturity (1-10)",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No PAM controls, 10 = Full PAM solution"
            },
            {
                "id": "access_004",
                "text": "Do you implement just-in-time (JIT) access for privileged operations?",
                "type": "boolean",
                "required": True,
                "true_score": 9,
                "false_score": 3
            },
            {
                "id": "access_005",
                "text": "How often are user access rights recertified?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never", "score": 1},
                    {"value": "3years", "label": "Every 2-3 years", "score": 3},
                    {"value": "annually", "label": "Annually", "score": 6},
                    {"value": "quarterly", "label": "Quarterly", "score": 8},
                    {"value": "monthly", "label": "Monthly", "score": 10}
                ]
            },
            {
                "id": "access_006",
                "text": "What percentage of admin accounts use dedicated admin workstations?",
                "type": "percentage",
                "required": True,
                "benchmark": 90
            },
            {
                "id": "access_007",
                "text": "Do you have identity governance and administration (IGA) tools?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "access_008",
                "text": "Rate the maturity of your role-based access control (RBAC) implementation",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No RBAC, 10 = Fully automated RBAC with dynamic roles"
            },
            {
                "id": "access_009",
                "text": "How do you handle emergency access procedures?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No formal procedure", "score": 1},
                    {"value": "manual", "label": "Manual break-glass process", "score": 4},
                    {"value": "automated", "label": "Automated emergency access", "score": 7},
                    {"value": "monitored", "label": "Automated with real-time monitoring", "score": 10}
                ]
            },
            {
                "id": "access_010",
                "text": "What is your account lockout policy for failed login attempts?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No lockout policy", "score": 1},
                    {"value": "10plus", "label": "10+ failed attempts", "score": 3},
                    {"value": "5to9", "label": "5-9 failed attempts", "score": 6},
                    {"value": "3to4", "label": "3-4 failed attempts", "score": 8},
                    {"value": "1to2", "label": "1-2 failed attempts", "score": 10}
                ]
            },
            {
                "id": "access_011",
                "text": "Do you implement single sign-on (SSO) across enterprise applications?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "access_012",
                "text": "Rate your password policy strength and enforcement",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Weak/no policy, 10 = Strong policy with technical enforcement"
            },
            {
                "id": "access_013",
                "text": "What percentage of accounts use passwordless authentication?",
                "type": "percentage",
                "required": True,
                "benchmark": 25
            },
            {
                "id": "access_014",
                "text": "How do you monitor and detect account compromise?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No monitoring", "score": 1},
                    {"value": "basic", "label": "Basic log monitoring", "score": 3},
                    {"value": "ueba", "label": "User behavior analytics", "score": 7},
                    {"value": "ai", "label": "AI-powered anomaly detection", "score": 10}
                ]
            },
            {
                "id": "access_015",
                "text": "Describe your privileged access monitoring and session recording capabilities",
                "type": "text",
                "required": False,
                "placeholder": "Describe session recording, monitoring, and audit capabilities..."
            }
        ]
    },
    "data_protection": {
        "name": "Data Protection & Privacy",
        "weight": 0.15,
        "description": "Data classification, encryption, and privacy controls",
        "questions": [
            {
                "id": "data_001",
                "text": "What percentage of sensitive data is encrypted at rest?",
                "type": "percentage",
                "required": True,
                "benchmark": 90
            },
            {
                "id": "data_002",
                "text": "Is data classified according to sensitivity levels?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "data_003",
                "text": "How often are data backups tested for restoration?",
                "type": "frequency",
                "required": True,
                "description": "Testing frequency affects reliability confidence"
            },
            {
                "id": "data_004",
                "text": "Describe your data loss prevention (DLP) implementation",
                "type": "text",
                "required": False,
                "placeholder": "Describe DLP tools, policies, and monitoring..."
            },
            {
                "id": "data_005",
                "text": "What percentage of data in transit is encrypted?",
                "type": "percentage",
                "required": True,
                "benchmark": 95
            },
            {
                "id": "data_006",
                "text": "Do you have a formal data retention and disposal policy?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "data_007",
                "text": "How often do you conduct data discovery and classification reviews?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never", "score": 1},
                    {"value": "annually", "label": "Annually", "score": 4},
                    {"value": "quarterly", "label": "Quarterly", "score": 7},
                    {"value": "monthly", "label": "Monthly", "score": 9},
                    {"value": "continuous", "label": "Continuous monitoring", "score": 10}
                ]
            },
            {
                "id": "data_008",
                "text": "Rate your database security controls maturity",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Basic controls, 10 = Advanced DAM, encryption, monitoring"
            },
            {
                "id": "data_009",
                "text": "Do you implement data masking for non-production environments?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "data_010",
                "text": "What is your recovery point objective (RPO) for critical data?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "days", "label": "Days", "score": 2},
                    {"value": "hours", "label": "Hours", "score": 5},
                    {"value": "minutes", "label": "Minutes", "score": 8},
                    {"value": "seconds", "label": "Seconds (real-time)", "score": 10}
                ]
            },
            {
                "id": "data_011",
                "text": "Do you have automated data breach detection capabilities?",
                "type": "boolean",
                "required": True,
                "true_score": 9,
                "false_score": 2
            },
            {
                "id": "data_012",
                "text": "Rate your cloud data protection controls",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Basic controls, 10 = Advanced CASB, encryption, monitoring"
            },
            {
                "id": "data_013",
                "text": "What percentage of sensitive data repositories have access monitoring?",
                "type": "percentage",
                "required": True,
                "benchmark": 90
            },
            {
                "id": "data_014",
                "text": "Do you implement rights management for documents and files?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "data_015",
                "text": "How do you handle data subject rights requests (GDPR/CCPA)?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "manual", "label": "Manual process", "score": 3},
                    {"value": "semi", "label": "Semi-automated", "score": 6},
                    {"value": "automated", "label": "Fully automated", "score": 10},
                    {"value": "none", "label": "No formal process", "score": 1}
                ]
            }
        ]
    },
    "security_monitoring": {
        "name": "Security Monitoring & Detection",
        "weight": 0.12,
        "description": "Logging, monitoring, and threat detection capabilities",
        "questions": [
            {
                "id": "monitor_001",
                "text": "Rate your security monitoring maturity (1-10)",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Basic logging, 10 = Advanced SIEM/SOAR"
            },
            {
                "id": "monitor_002",
                "text": "How quickly can you detect a security incident?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "weeks", "label": "Weeks", "score": 1},
                    {"value": "days", "label": "Days", "score": 3},
                    {"value": "hours", "label": "Hours", "score": 6},
                    {"value": "minutes", "label": "Minutes", "score": 8},
                    {"value": "real_time", "label": "Real-time", "score": 10}
                ]
            },
            {
                "id": "monitor_003",
                "text": "Do you have 24/7 security monitoring?",
                "type": "boolean",
                "required": True,
                "true_score": 9,
                "false_score": 3
            },
            {
                "id": "monitor_004",
                "text": "Rate your endpoint detection and response (EDR) capabilities",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Basic antivirus, 10 = Advanced EDR with behavioral analysis"
            },
            {
                "id": "monitor_005",
                "text": "What percentage of endpoints have security monitoring agents?",
                "type": "percentage",
                "required": True,
                "benchmark": 95
            },
            {
                "id": "monitor_006",
                "text": "Do you have network segmentation monitoring capabilities?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "monitor_007",
                "text": "How do you handle security alert triage and prioritization?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "manual", "label": "Manual review", "score": 3},
                    {"value": "basic", "label": "Basic automation", "score": 5},
                    {"value": "advanced", "label": "Advanced SOAR automation", "score": 8},
                    {"value": "ai", "label": "AI-powered prioritization", "score": 10}
                ]
            },
            {
                "id": "monitor_008",
                "text": "Rate your threat hunting capabilities",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No threat hunting, 10 = Proactive threat hunting team"
            },
            {
                "id": "monitor_009",
                "text": "Do you integrate threat intelligence feeds into your monitoring?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 4
            },
            {
                "id": "monitor_010",
                "text": "What is your mean time to detect (MTTD) for security incidents?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "days", "label": "Days", "score": 2},
                    {"value": "hours", "label": "Hours", "score": 5},
                    {"value": "minutes", "label": "Minutes", "score": 8},
                    {"value": "seconds", "label": "Seconds", "score": 10}
                ]
            },
            {
                "id": "monitor_011",
                "text": "Do you monitor cloud infrastructure for security events?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "monitor_012",
                "text": "Rate your security orchestration and automated response (SOAR) maturity",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No automation, 10 = Comprehensive SOAR platform"
            },
            {
                "id": "monitor_013",
                "text": "What percentage of security alerts are automatically triaged?",
                "type": "percentage",
                "required": True,
                "benchmark": 70
            },
            {
                "id": "monitor_014",
                "text": "Do you have user and entity behavior analytics (UEBA) capabilities?",
                "type": "boolean",
                "required": True,
                "true_score": 9,
                "false_score": 3
            },
            {
                "id": "monitor_015",
                "text": "Describe your security monitoring coverage across hybrid/multi-cloud environments",
                "type": "text",
                "required": False,
                "placeholder": "Describe monitoring capabilities across on-premise, cloud, and hybrid environments..."
            }
        ]
    },
    "incident_response": {
        "name": "Incident Response & Recovery",
        "weight": 0.12,
        "description": "Incident handling, response, and recovery procedures",
        "questions": [
            {
                "id": "ir_001",
                "text": "Rate your incident response plan maturity (1-10)",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No plan, 10 = Comprehensive tested plan"
            },
            {
                "id": "ir_002",
                "text": "How often do you test incident response procedures?",
                "type": "frequency",
                "required": True
            },
            {
                "id": "ir_003",
                "text": "What is your average incident response time?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "days", "label": "Days", "score": 2},
                    {"value": "hours", "label": "Hours", "score": 5},
                    {"value": "minutes", "label": "Minutes", "score": 8},
                    {"value": "immediate", "label": "Immediate", "score": 10}
                ]
            },
            {
                "id": "ir_004",
                "text": "Do you have a dedicated incident response team?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "ir_005",
                "text": "Rate your incident classification and severity assignment process",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No formal process, 10 = Automated classification with clear SLAs"
            },
            {
                "id": "ir_006",
                "text": "How do you handle evidence collection and forensics?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No formal process", "score": 1},
                    {"value": "basic", "label": "Basic manual collection", "score": 4},
                    {"value": "tools", "label": "Forensic tools and procedures", "score": 7},
                    {"value": "automated", "label": "Automated evidence collection", "score": 10}
                ]
            },
            {
                "id": "ir_007",
                "text": "Do you have automated incident containment capabilities?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 4
            },
            {
                "id": "ir_008",
                "text": "Rate your incident communication and stakeholder notification process",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Ad-hoc communication, 10 = Automated stakeholder notifications"
            },
            {
                "id": "ir_009",
                "text": "How often do you conduct post-incident reviews and lessons learned?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never", "score": 1},
                    {"value": "major", "label": "Only for major incidents", "score": 4},
                    {"value": "most", "label": "For most incidents", "score": 7},
                    {"value": "all", "label": "For all incidents", "score": 10}
                ]
            },
            {
                "id": "ir_010",
                "text": "Do you have legal and regulatory notification procedures?",
                "type": "boolean",
                "required": True,
                "true_score": 9,
                "false_score": 2
            },
            {
                "id": "ir_011",
                "text": "Rate your incident response playbook completeness and currency",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No playbooks, 10 = Comprehensive, regularly updated playbooks"
            },
            {
                "id": "ir_012",
                "text": "What is your mean time to recovery (MTTR) for critical incidents?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "days", "label": "Days", "score": 2},
                    {"value": "hours", "label": "Hours", "score": 5},
                    {"value": "minutes", "label": "Minutes", "score": 8},
                    {"value": "immediate", "label": "Immediate", "score": 10}
                ]
            },
            {
                "id": "ir_013",
                "text": "Do you maintain incident response metrics and KPIs?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "ir_014",
                "text": "Rate your coordination with external parties (law enforcement, vendors)",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No coordination, 10 = Established relationships and procedures"
            },
            {
                "id": "ir_015",
                "text": "Describe your incident response tool integration and automation capabilities",
                "type": "text",
                "required": False,
                "placeholder": "Describe integration between SIEM, SOAR, ticketing, and communication tools..."
            }
        ]
    },
    "business_continuity": {
        "name": "Business Continuity & Resilience",
        "weight": 0.10,
        "description": "Disaster recovery and business continuity planning",
        "questions": [
            {
                "id": "bc_001",
                "text": "Do you have a tested business continuity plan?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 1
            },
            {
                "id": "bc_002",
                "text": "What is your recovery time objective (RTO) for critical systems?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "days", "label": "Days", "score": 2},
                    {"value": "hours", "label": "Hours", "score": 5},
                    {"value": "minutes", "label": "Minutes", "score": 8},
                    {"value": "seconds", "label": "Seconds (HA)", "score": 10}
                ]
            },
            {
                "id": "bc_003",
                "text": "How often do you conduct business impact analyses (BIA)?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "never", "label": "Never conducted", "score": 1},
                    {"value": "3years", "label": "Every 2-3 years", "score": 4},
                    {"value": "annually", "label": "Annually", "score": 7},
                    {"value": "continuous", "label": "Continuous assessment", "score": 10}
                ]
            },
            {
                "id": "bc_004",
                "text": "Rate your disaster recovery testing frequency and comprehensiveness",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Never tested, 10 = Regular comprehensive testing"
            },
            {
                "id": "bc_005",
                "text": "Do you have alternate processing sites for critical operations?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "bc_006",
                "text": "What percentage of critical business processes have documented recovery procedures?",
                "type": "percentage",
                "required": True,
                "benchmark": 95
            },
            {
                "id": "bc_007",
                "text": "Rate your supply chain continuity planning",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No planning, 10 = Comprehensive supplier continuity program"
            },
            {
                "id": "bc_008",
                "text": "Do you have emergency communication systems for business continuity?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "bc_009",
                "text": "How do you handle remote work continuity capabilities?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No remote work capability", "score": 1},
                    {"value": "limited", "label": "Limited remote access", "score": 4},
                    {"value": "partial", "label": "Partial workforce remote capable", "score": 7},
                    {"value": "full", "label": "Full workforce remote capable", "score": 10}
                ]
            },
            {
                "id": "bc_010",
                "text": "Rate your crisis management and executive decision-making processes",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No formal process, 10 = Well-defined crisis management structure"
            },
            {
                "id": "bc_011",
                "text": "Do you maintain insurance coverage for business interruption and cyber incidents?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "bc_012",
                "text": "Describe your business continuity plan maintenance and update process",
                "type": "text",
                "required": False,
                "placeholder": "Describe how you keep BC plans current and validated..."
            },
            {
                "id": "bc_013",
                "text": "Rate your pandemic and health crisis preparedness",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No preparation, 10 = Comprehensive pandemic response plans"
            },
            {
                "id": "bc_014",
                "text": "Do you have cross-training programs for critical roles?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "bc_015",
                "text": "Rate your business continuity exercise and simulation program",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No exercises, 10 = Regular comprehensive simulations"
            }
        ]
    },
    "asset_management": {
        "name": "Asset Management & Inventory",
        "weight": 0.08,
        "description": "IT asset visibility and management",
        "questions": [
            {
                "id": "asset_001",
                "text": "What percentage of IT assets are inventoried and tracked?",
                "type": "percentage",
                "required": True,
                "benchmark": 95
            },
            {
                "id": "asset_002",
                "text": "How frequently is your asset inventory updated?",
                "type": "frequency",
                "required": True
            },
            {
                "id": "asset_003",
                "text": "Rate your automated asset discovery capabilities",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Manual tracking, 10 = Comprehensive automated discovery"
            },
            {
                "id": "asset_004",
                "text": "Do you have a configuration management database (CMDB)?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "asset_005",
                "text": "What percentage of assets have approved security baselines?",
                "type": "percentage",
                "required": True,
                "benchmark": 90
            },
            {
                "id": "asset_006",
                "text": "Rate your software license management and compliance tracking",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No tracking, 10 = Automated compliance monitoring"
            },
            {
                "id": "asset_007",
                "text": "How do you handle end-of-life and asset disposal?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No formal process", "score": 1},
                    {"value": "basic", "label": "Basic disposal procedures", "score": 4},
                    {"value": "secure", "label": "Secure data wiping procedures", "score": 7},
                    {"value": "certified", "label": "Certified secure disposal", "score": 10}
                ]
            },
            {
                "id": "asset_008",
                "text": "Do you track and manage cloud assets and services?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 2
            },
            {
                "id": "asset_009",
                "text": "Rate your vulnerability assessment coverage across all assets",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Limited scanning, 10 = Comprehensive continuous assessment"
            },
            {
                "id": "asset_010",
                "text": "What percentage of critical assets have real-time monitoring?",
                "type": "percentage",
                "required": True,
                "benchmark": 85
            },
            {
                "id": "asset_011",
                "text": "Do you maintain asset ownership and custodian assignments?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "asset_012",
                "text": "Describe your mobile device and IoT asset management approach",
                "type": "text",
                "required": False,
                "placeholder": "Describe how you manage mobile devices, IoT, and edge computing assets..."
            },
            {
                "id": "asset_013",
                "text": "Do you have automated patch management across all asset types?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "asset_014",
                "text": "Rate your shadow IT discovery and management capabilities",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = No visibility, 10 = Comprehensive shadow IT management"
            },
            {
                "id": "asset_015",
                "text": "What percentage of assets have security agents or monitoring?",
                "type": "percentage",
                "required": True,
                "benchmark": 95
            }
        ]
    },
    "security_awareness": {
        "name": "Security Awareness & Training",
        "weight": 0.08,
        "description": "Employee security training and awareness programs",
        "questions": [
            {
                "id": "aware_001",
                "text": "How often do employees receive security training?",
                "type": "frequency",
                "required": True
            },
            {
                "id": "aware_002",
                "text": "Do you conduct phishing simulation exercises?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 2
            },
            {
                "id": "aware_003",
                "text": "Rate your role-based security training program maturity",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Generic training, 10 = Comprehensive role-specific programs"
            },
            {
                "id": "aware_004",
                "text": "What percentage of employees complete annual security training?",
                "type": "percentage",
                "required": True,
                "benchmark": 95
            },
            {
                "id": "aware_005",
                "text": "Do you have a security champion program across departments?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 3
            },
            {
                "id": "aware_006",
                "text": "How do you measure security awareness effectiveness?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "none", "label": "No measurement", "score": 1},
                    {"value": "completion", "label": "Training completion rates", "score": 4},
                    {"value": "testing", "label": "Knowledge testing and assessment", "score": 7},
                    {"value": "behavioral", "label": "Behavioral metrics and incident correlation", "score": 10}
                ]
            },
            {
                "id": "aware_007",
                "text": "Rate your incident reporting culture and employee participation",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Poor reporting culture, 10 = High employee engagement in reporting"
            },
            {
                "id": "aware_008",
                "text": "Do you provide just-in-time security awareness notifications?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            },
            {
                "id": "aware_009",
                "text": "What is your phishing simulation click rate?",
                "type": "multiple_choice",
                "required": True,
                "options": [
                    {"value": "high", "label": "Over 15%", "score": 2},
                    {"value": "medium", "label": "10-15%", "score": 5},
                    {"value": "low", "label": "5-10%", "score": 8},
                    {"value": "verylow", "label": "Under 5%", "score": 10}
                ]
            },
            {
                "id": "aware_010",
                "text": "Do you have security awareness metrics dashboard for leadership?",
                "type": "boolean",
                "required": True,
                "true_score": 8,
                "false_score": 4
            },
            {
                "id": "aware_011",
                "text": "Rate your new employee security onboarding program",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Basic orientation, 10 = Comprehensive security onboarding"
            },
            {
                "id": "aware_012",
                "text": "Describe your approach to security awareness for remote and hybrid workers",
                "type": "text",
                "required": False,
                "placeholder": "Describe security awareness programs tailored for remote work environments..."
            },
            {
                "id": "aware_013",
                "text": "Do you provide security awareness training in multiple languages?",
                "type": "boolean",
                "required": True,
                "true_score": 6,
                "false_score": 4
            },
            {
                "id": "aware_014",
                "text": "Rate your security culture maturity across the organization",
                "type": "scale",
                "required": True,
                "scale": {"min": 1, "max": 10},
                "description": "1 = Security seen as IT issue, 10 = Security-first culture"
            },
            {
                "id": "aware_015",
                "text": "Do you conduct regular security awareness surveys and culture assessments?",
                "type": "boolean",
                "required": True,
                "true_score": 7,
                "false_score": 3
            }
        ]
    }
}

@router.get("/assessment/enterprise/questions")
def get_enterprise_questions():
    """Get structured enterprise assessment questions"""
    try:
        total_questions = sum(len(section["questions"]) for section in ENTERPRISE_QUESTIONS.values())
        
        return {
            "assessment_type": "enterprise",
            "total_questions": total_questions,
            "total_sections": len(ENTERPRISE_QUESTIONS),
            "sections": ENTERPRISE_QUESTIONS,
            "estimated_time_minutes": total_questions * 1.5,
            "scoring_method": "dynamic_with_quantitative_support_and_ai_feedback",
            "frameworks_covered": ["NIST CSF", "ISO 27001", "CIS Controls", "COBIT", "PCI DSS"],
            "features": [
                "120 comprehensive questions across 8 security domains",
                "Dynamic scoring based on actual answers",
                "Industry-specific benchmarks and adjustments",
                "AI-powered feedback and recommendations",
                "Statistical confidence intervals",
                "Framework source attribution",
                "Improvement roadmap generation"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting enterprise questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

@router.post("/assessment/enterprise/submit")
def submit_enterprise_assessment(submission: AssessmentSubmission):
    """Submit enterprise assessment with dynamic scoring"""
    try:
        logger.info(f"Processing assessment for {submission.company_profile.name}")
        
        # Convert answers to format expected by scoring engine
        answers_dict = {}
        for answer in submission.answers:
            answers_dict[answer.question_id] = answer.answer
        
        # Use dynamic scoring engine
        scoring_result = dynamic_scoring_engine.score_assessment(
            answers_dict, 
            submission.company_profile.dict()
        )
        
        # Calculate risk level
        overall_score = scoring_result['overall_score']
        risk_level, risk_color = _get_risk_level(overall_score)
        
        # Create detailed section breakdown
        section_breakdown = []
        # Map abbreviated section IDs to full section names
        section_id_mapping = {
            "gov": "governance",
            "access": "access_control", 
            "data": "data_protection",
            "monitor": "security_monitoring",
            "ir": "incident_response",
            "bc": "business_continuity",
            "asset": "asset_management",
            "aware": "security_awareness"
        }
        
        for section_id, section_data in scoring_result['section_scores'].items():
            # Map abbreviated ID to full section key
            full_section_id = section_id_mapping.get(section_id, section_id)
            section_info = ENTERPRISE_QUESTIONS.get(full_section_id, {})
            
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
        
        # Generate AI-powered feedback
        try:
            ai_feedback = ai_feedback_generator.generate_comprehensive_feedback(
                {
                    'overall_score': overall_score,
                    'section_breakdown': section_breakdown,
                    'company_profile': submission.company_profile.dict()
                },
                submission.company_profile.dict()
            )
            
            # Convert AI feedback to dict format
            ai_recommendations = [{
                "priority": rec.priority,
                "category": rec.category,
                "title": rec.title,
                "description": rec.description,
                "implementation_steps": rec.implementation_steps,
                "estimated_effort": rec.estimated_effort,
                "timeframe": rec.timeframe,
                "framework_references": rec.framework_references,
                "risk_impact": rec.risk_impact,
                "confidence_score": rec.confidence_score
            } for rec in ai_feedback.recommendations]
            
        except Exception as e:
            logger.warning(f"AI feedback generation failed: {str(e)}")
            ai_feedback = None
            ai_recommendations = []
        
        # Generate comprehensive result
        result = {
            "assessment_id": str(uuid.uuid4()),
            "company_profile": submission.company_profile.dict(),
            "overall_score": overall_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "scoring_method": "dynamic_quantitative_qualitative",
            "section_breakdown": section_breakdown,
            "confidence_metrics": scoring_result['confidence_metrics'],
            "insights": scoring_result['insights'],
            "recommendations": scoring_result['recommendations'],
            "assessment_date": datetime.utcnow().isoformat(),
            "questions_answered": len(submission.answers),
            "total_questions": sum(len(section["questions"]) for section in ENTERPRISE_QUESTIONS.values()),
            "completion_rate": len(submission.answers) / sum(len(section["questions"]) for section in ENTERPRISE_QUESTIONS.values()),
            "quantitative_support": True,
            "industry_adjustments_applied": True,
            # AI-powered feedback
            "ai_feedback": {
                "overall_assessment": ai_feedback.overall_assessment if ai_feedback else "AI feedback temporarily unavailable",
                "key_strengths": ai_feedback.key_strengths if ai_feedback else [],
                "critical_gaps": ai_feedback.critical_gaps if ai_feedback else [],
                "ai_recommendations": ai_recommendations,
                "industry_comparison": ai_feedback.industry_comparison if ai_feedback else "Industry comparison pending",
                "next_steps": ai_feedback.next_steps if ai_feedback else [],
                "improvement_roadmap": ai_feedback.improvement_roadmap if ai_feedback else {}
            } if ai_feedback else {
                "overall_assessment": "AI feedback temporarily unavailable",
                "key_strengths": [],
                "critical_gaps": [],
                "ai_recommendations": [],
                "industry_comparison": "Industry comparison pending",
                "next_steps": [],
                "improvement_roadmap": {}
            }
        }
        
        logger.info(f"Assessment completed: {overall_score:.1f} ({risk_level}) for {submission.company_profile.name} with AI feedback")
        return result
        
    except Exception as e:
        logger.error(f"Error processing enterprise assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {str(e)}")

@router.get("/assessment/enterprise/sample")
def get_sample_responses():
    """Get sample responses for testing different scoring scenarios"""
    return {
        "low_maturity": {
            "gov_001": "none",
            "gov_002": 2,
            "gov_003": "never",
            "gov_004": False,
            "access_001": 10,
            "access_002": "never",
            "data_001": 20,
            "data_002": False,
            "monitor_001": 2,
            "ir_001": 1
        },
        "medium_maturity": {
            "gov_001": "basic",
            "gov_002": 6,
            "gov_003": "quarterly",
            "gov_004": True,
            "access_001": 70,
            "access_002": "quarterly",
            "data_001": 80,
            "data_002": True,
            "monitor_001": 6,
            "ir_001": 5
        },
        "high_maturity": {
            "gov_001": "optimized",
            "gov_002": 9,
            "gov_003": "monthly",
            "gov_004": True,
            "access_001": 95,
            "access_002": "continuous",
            "data_001": 98,
            "data_002": True,
            "monitor_001": 9,
            "ir_001": 9
        }
    }

@router.get("/assessment/enterprise/scoring-guide")
def get_scoring_guide():
    """Get detailed scoring methodology guide"""
    return {
        "scoring_methodology": "Dynamic Quantitative + Qualitative",
        "question_types": {
            "multiple_choice": "Direct score mapping from predefined options",
            "scale": "Linear scaling (1-10) with industry adjustments",
            "boolean": "Binary scoring with defined true/false values",
            "percentage": "Direct percentage mapping with benchmarks",
            "frequency": "Frequency-based scoring (never=0 to continuous=100)",
            "text": "NLP analysis with maturity indicators"
        },
        "adjustments": {
            "industry_specific": "Healthcare/Finance: +stricter governance, Tech: +innovation bonus",
            "company_size": "Small companies: +governance leniency, Large: +higher expectations",
            "quantitative_benchmarks": "Industry-specific percentage benchmarks applied"
        },
        "confidence_factors": [
            "Question type (boolean=95%, text=60%)",
            "Answer completeness",
            "Industry benchmark availability",
            "Quantitative support data"
        ],
        "maturity_levels": {
            "initial": "0-39% - No formal processes",
            "basic": "40-59% - Basic processes in place",
            "defined": "60-74% - Defined and documented",
            "managed": "75-89% - Managed and measured",
            "optimized": "90-100% - Continuously improving"
        }
    }

class AIFeedbackRequest(BaseModel):
    assessment_results: Dict[str, Any]
    company_profile: CompanyProfile

@router.post("/assessment/enterprise/ai-feedback")
def generate_ai_feedback(request: AIFeedbackRequest):
    """Generate AI-powered feedback for assessment results"""
    try:
        logger.info(f"Generating AI feedback for {request.company_profile.name}")
        
        # Generate AI feedback
        ai_feedback = ai_feedback_generator.generate_comprehensive_feedback(
            request.assessment_results,
            request.company_profile.dict()
        )
        
        # Convert to response format
        result = {
            "feedback_id": str(uuid.uuid4()),
            "generation_date": datetime.utcnow().isoformat(),
            "overall_assessment": ai_feedback.overall_assessment,
            "key_strengths": ai_feedback.key_strengths,
            "critical_gaps": ai_feedback.critical_gaps,
            "industry_comparison": ai_feedback.industry_comparison,
            "next_steps": ai_feedback.next_steps,
            "improvement_roadmap": ai_feedback.improvement_roadmap,
            "recommendations": [{
                "priority": rec.priority,
                "category": rec.category,
                "title": rec.title,
                "description": rec.description,
                "implementation_steps": rec.implementation_steps,
                "estimated_effort": rec.estimated_effort,
                "timeframe": rec.timeframe,
                "framework_references": rec.framework_references,
                "risk_impact": rec.risk_impact,
                "confidence_score": rec.confidence_score
            } for rec in ai_feedback.recommendations],
            "company_profile": request.company_profile.dict()
        }
        
        logger.info(f"AI feedback generated successfully for {request.company_profile.name}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating AI feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI feedback: {str(e)}")

def _get_risk_level(score: float) -> tuple[str, str]:
    """Determine risk level and color based on score"""
    if score >= 80:
        return "Low Risk", "#22c55e"
    elif score >= 65:
        return "Medium Risk", "#f59e0b"
    elif score >= 45:
        return "High Risk", "#ef4444"
    else:
        return "Critical Risk", "#dc2626"