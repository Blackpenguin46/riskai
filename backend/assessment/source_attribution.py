#!/usr/bin/env python3
"""
Source Attribution System
Links AI recommendations to authoritative cybersecurity frameworks and standards
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class FrameworkType(Enum):
    NIST_CSF = "NIST Cybersecurity Framework"
    ISO_27001 = "ISO 27001"
    FAIR = "Factor Analysis of Information Risk"
    COBIT = "COBIT 2019"
    GDPR = "General Data Protection Regulation"
    HIPAA = "Health Insurance Portability and Accountability Act"
    PCI_DSS = "Payment Card Industry Data Security Standard"
    SOX = "Sarbanes-Oxley Act"
    NIST_800_53 = "NIST SP 800-53"
    CIS_CONTROLS = "CIS Critical Security Controls"

@dataclass
class FrameworkReference:
    """Reference to a specific framework control or requirement"""
    framework: FrameworkType
    control_id: str
    control_title: str
    description: str
    section: Optional[str] = None
    subsection: Optional[str] = None
    page_number: Optional[int] = None
    url: Optional[str] = None
    relevance_score: float = 0.0

@dataclass
class SourceAttribution:
    """Complete source attribution for a recommendation"""
    recommendation_id: str
    primary_sources: List[FrameworkReference]
    supporting_sources: List[FrameworkReference]
    confidence_score: float
    reliability_score: float
    coverage_score: float  # How well sources cover the recommendation
    last_updated: datetime

class SourceAttributor:
    """Main class for attributing recommendations to authoritative sources"""
    
    def __init__(self):
        self.framework_mappings = self._load_framework_mappings()
        self.keyword_patterns = self._load_keyword_patterns()
        
    def _load_framework_mappings(self) -> Dict[str, List[FrameworkReference]]:
        """Load predefined mappings between topics and framework controls"""
        return {
            # Governance and Risk Management
            "governance": [
                FrameworkReference(
                    framework=FrameworkType.NIST_CSF,
                    control_id="ID.GV-1",
                    control_title="Organizational cybersecurity policy is established and communicated",
                    description="The organization's cybersecurity policy establishes the overall cybersecurity strategy",
                    section="Identify",
                    subsection="Governance",
                    relevance_score=0.95
                ),
                FrameworkReference(
                    framework=FrameworkType.ISO_27001,
                    control_id="A.5.1.1",
                    control_title="Information security policies",
                    description="A set of policies for information security shall be defined",
                    section="A.5",
                    subsection="Information security policies",
                    relevance_score=0.90
                ),
                FrameworkReference(
                    framework=FrameworkType.COBIT,
                    control_id="EDM03.01",
                    control_title="Evaluate risk management",
                    description="Continually examine and make judgments on the effect of risk on enterprise objectives",
                    section="EDM03",
                    relevance_score=0.85
                )
            ],
            
            # Access Control
            "access_control": [
                FrameworkReference(
                    framework=FrameworkType.NIST_CSF,
                    control_id="PR.AC-1",
                    control_title="Identities and credentials are issued, managed, verified, revoked, and audited",
                    description="Identity management processes and procedures are established",
                    section="Protect",
                    subsection="Access Control",
                    relevance_score=0.95
                ),
                FrameworkReference(
                    framework=FrameworkType.ISO_27001,
                    control_id="A.9.1.1",
                    control_title="Access control policy",
                    description="An access control policy shall be established, documented and reviewed",
                    section="A.9",
                    subsection="Access control",
                    relevance_score=0.90
                ),
                FrameworkReference(
                    framework=FrameworkType.CIS_CONTROLS,
                    control_id="CIS-5",
                    control_title="Account Management",
                    description="Use processes and tools to assign and manage authorization to credentials",
                    section="Basic Controls",
                    relevance_score=0.88
                )
            ],
            
            # Data Protection
            "data_protection": [
                FrameworkReference(
                    framework=FrameworkType.NIST_CSF,
                    control_id="PR.DS-1",
                    control_title="Data-at-rest is protected",
                    description="Data at rest is protected through appropriate mechanisms",
                    section="Protect",
                    subsection="Data Security",
                    relevance_score=0.95
                ),
                FrameworkReference(
                    framework=FrameworkType.GDPR,
                    control_id="Art.32",
                    control_title="Security of processing",
                    description="Appropriate technical and organisational measures to ensure security",
                    section="Chapter IV",
                    relevance_score=0.92
                ),
                FrameworkReference(
                    framework=FrameworkType.ISO_27001,
                    control_id="A.10.1.1",
                    control_title="Cryptographic policy",
                    description="A policy on the use of cryptographic controls shall be developed",
                    section="A.10",
                    subsection="Cryptography",
                    relevance_score=0.85
                )
            ],
            
            # Incident Response
            "incident_response": [
                FrameworkReference(
                    framework=FrameworkType.NIST_CSF,
                    control_id="RS.RP-1",
                    control_title="Response plan is executed during or after an incident",
                    description="Response processes and procedures are executed and maintained",
                    section="Respond",
                    subsection="Response Planning",
                    relevance_score=0.95
                ),
                FrameworkReference(
                    framework=FrameworkType.ISO_27001,
                    control_id="A.16.1.1",
                    control_title="Responsibilities and procedures",
                    description="Management responsibilities and procedures shall be established",
                    section="A.16",
                    subsection="Information security incident management",
                    relevance_score=0.90
                )
            ],
            
            # Security Monitoring
            "security_monitoring": [
                FrameworkReference(
                    framework=FrameworkType.NIST_CSF,
                    control_id="DE.CM-1",
                    control_title="The network is monitored to detect potential cybersecurity events",
                    description="Network monitoring is performed to identify cybersecurity events",
                    section="Detect",
                    subsection="Security Continuous Monitoring",
                    relevance_score=0.95
                ),
                FrameworkReference(
                    framework=FrameworkType.CIS_CONTROLS,
                    control_id="CIS-6",
                    control_title="Maintenance, Monitoring and Analysis of Audit Logs",
                    description="Collect, alert, and analyze audit logs of events",
                    section="Basic Controls",
                    relevance_score=0.88
                )
            ],
            
            # Emerging Technologies
            "emerging_tech": [
                FrameworkReference(
                    framework=FrameworkType.NIST_CSF,
                    control_id="ID.RA-1",
                    control_title="Asset vulnerabilities are identified and documented",
                    description="Vulnerabilities in assets are identified, documented, and addressed",
                    section="Identify",
                    subsection="Risk Assessment",
                    relevance_score=0.80
                ),
                FrameworkReference(
                    framework=FrameworkType.ISO_27001,
                    control_id="A.12.6.1",
                    control_title="Management of technical vulnerabilities",
                    description="Information about technical vulnerabilities shall be obtained",
                    section="A.12",
                    subsection="Operations security",
                    relevance_score=0.75
                )
            ]
        }
    
    def _load_keyword_patterns(self) -> Dict[str, List[str]]:
        """Load keyword patterns for matching recommendations to frameworks"""
        return {
            "governance": [
                "policy", "governance", "strategy", "executive", "board", "oversight",
                "risk management", "compliance", "framework", "standards"
            ],
            "access_control": [
                "access", "authentication", "authorization", "identity", "credential",
                "multi-factor", "MFA", "privilege", "least privilege", "role-based"
            ],
            "data_protection": [
                "encryption", "data protection", "privacy", "confidentiality",
                "data classification", "backup", "recovery", "retention"
            ],
            "incident_response": [
                "incident", "response", "forensics", "containment", "recovery",
                "business continuity", "disaster recovery", "emergency"
            ],
            "security_monitoring": [
                "monitoring", "detection", "SIEM", "logging", "alerting",
                "threat detection", "anomaly", "surveillance"
            ],
            "emerging_tech": [
                "AI", "artificial intelligence", "machine learning", "IoT",
                "cloud", "blockchain", "automation", "emerging technology"
            ]
        }
    
    def attribute_recommendation(self, recommendation_text: str, 
                               section_id: Optional[str] = None,
                               assessment_context: Optional[Dict[str, Any]] = None) -> SourceAttribution:
        """
        Attribute a recommendation to authoritative sources
        
        Args:
            recommendation_text: The recommendation to attribute
            section_id: Optional section ID for context
            assessment_context: Optional assessment context for better attribution
            
        Returns:
            SourceAttribution with linked framework references
        """
        recommendation_id = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Find relevant frameworks based on content analysis
        primary_sources = self._find_primary_sources(recommendation_text, section_id)
        supporting_sources = self._find_supporting_sources(recommendation_text, primary_sources)
        
        # Calculate confidence scores
        confidence_score = self._calculate_confidence_score(recommendation_text, primary_sources)
        reliability_score = self._calculate_reliability_score(primary_sources + supporting_sources)
        coverage_score = self._calculate_coverage_score(recommendation_text, primary_sources + supporting_sources)
        
        return SourceAttribution(
            recommendation_id=recommendation_id,
            primary_sources=primary_sources,
            supporting_sources=supporting_sources,
            confidence_score=confidence_score,
            reliability_score=reliability_score,
            coverage_score=coverage_score,
            last_updated=datetime.utcnow()
        )
    
    def _find_primary_sources(self, recommendation_text: str, 
                            section_id: Optional[str] = None) -> List[FrameworkReference]:
        """Find primary framework sources for a recommendation"""
        primary_sources = []
        
        # Start with section-based mapping if available
        if section_id and section_id in self.framework_mappings:
            section_sources = self.framework_mappings[section_id]
            # Filter based on text relevance
            for source in section_sources:
                if self._calculate_text_relevance(recommendation_text, source) > 0.6:
                    primary_sources.append(source)
        
        # Add keyword-based matching
        for category, keywords in self.keyword_patterns.items():
            if category in self.framework_mappings:
                keyword_matches = sum(1 for keyword in keywords 
                                    if keyword.lower() in recommendation_text.lower())
                if keyword_matches >= 2:  # Require at least 2 keyword matches
                    category_sources = self.framework_mappings[category]
                    for source in category_sources:
                        if source not in primary_sources:
                            relevance = self._calculate_text_relevance(recommendation_text, source)
                            if relevance > 0.5:
                                source.relevance_score = relevance
                                primary_sources.append(source)
        
        # Sort by relevance and return top sources
        primary_sources.sort(key=lambda x: x.relevance_score, reverse=True)
        return primary_sources[:3]  # Return top 3 primary sources
    
    def _find_supporting_sources(self, recommendation_text: str, 
                               primary_sources: List[FrameworkReference]) -> List[FrameworkReference]:
        """Find supporting framework sources"""
        supporting_sources = []
        primary_frameworks = {source.framework for source in primary_sources}
        
        # Look for additional sources from different frameworks
        for category, sources in self.framework_mappings.items():
            for source in sources:
                if (source.framework not in primary_frameworks and 
                    source not in primary_sources):
                    relevance = self._calculate_text_relevance(recommendation_text, source)
                    if relevance > 0.3:  # Lower threshold for supporting sources
                        source.relevance_score = relevance
                        supporting_sources.append(source)
        
        # Sort and return top supporting sources
        supporting_sources.sort(key=lambda x: x.relevance_score, reverse=True)
        return supporting_sources[:5]  # Return top 5 supporting sources
    
    def _calculate_text_relevance(self, recommendation_text: str, 
                                source: FrameworkReference) -> float:
        """Calculate relevance between recommendation text and framework source"""
        text_lower = recommendation_text.lower()
        
        # Check for direct matches in control title and description
        title_words = source.control_title.lower().split()
        desc_words = source.description.lower().split()
        
        title_matches = sum(1 for word in title_words if word in text_lower)
        desc_matches = sum(1 for word in desc_words if word in text_lower)
        
        # Calculate relevance score
        title_relevance = title_matches / len(title_words) if title_words else 0
        desc_relevance = desc_matches / len(desc_words) if desc_words else 0
        
        # Weighted combination
        relevance = (title_relevance * 0.7) + (desc_relevance * 0.3)
        
        return min(relevance, 1.0)
    
    def _calculate_confidence_score(self, recommendation_text: str, 
                                  primary_sources: List[FrameworkReference]) -> float:
        """Calculate confidence score for the attribution"""
        if not primary_sources:
            return 0.0
        
        # Base confidence on number and quality of primary sources
        source_quality = sum(source.relevance_score for source in primary_sources) / len(primary_sources)
        source_count_factor = min(len(primary_sources) / 3.0, 1.0)  # Optimal is 3 sources
        
        # Text length factor (longer recommendations are harder to attribute accurately)
        text_length_factor = max(0.5, 1.0 - (len(recommendation_text) / 1000.0))
        
        confidence = source_quality * source_count_factor * text_length_factor
        return min(confidence, 0.95)  # Cap at 95%
    
    def _calculate_reliability_score(self, all_sources: List[FrameworkReference]) -> float:
        """Calculate reliability score based on source authority"""
        if not all_sources:
            return 0.0
        
        # Framework reliability weights
        framework_weights = {
            FrameworkType.NIST_CSF: 1.0,
            FrameworkType.ISO_27001: 0.95,
            FrameworkType.NIST_800_53: 0.95,
            FrameworkType.CIS_CONTROLS: 0.90,
            FrameworkType.COBIT: 0.85,
            FrameworkType.GDPR: 0.90,
            FrameworkType.HIPAA: 0.85,
            FrameworkType.PCI_DSS: 0.85,
            FrameworkType.SOX: 0.80,
            FrameworkType.FAIR: 0.75
        }
        
        total_weight = sum(framework_weights.get(source.framework, 0.5) 
                          for source in all_sources)
        return min(total_weight / len(all_sources), 1.0)
    
    def _calculate_coverage_score(self, recommendation_text: str, 
                                all_sources: List[FrameworkReference]) -> float:
        """Calculate how well sources cover the recommendation"""
        if not all_sources:
            return 0.0
        
        # Simple coverage based on text overlap
        text_words = set(recommendation_text.lower().split())
        covered_words = set()
        
        for source in all_sources:
            source_words = set((source.control_title + " " + source.description).lower().split())
            covered_words.update(text_words.intersection(source_words))
        
        coverage = len(covered_words) / len(text_words) if text_words else 0
        return min(coverage, 1.0)
    
    def get_framework_details(self, framework: FrameworkType) -> Dict[str, Any]:
        """Get detailed information about a framework"""
        framework_details = {
            FrameworkType.NIST_CSF: {
                "name": "NIST Cybersecurity Framework",
                "version": "1.1",
                "publisher": "National Institute of Standards and Technology",
                "url": "https://www.nist.gov/cyberframework",
                "description": "A voluntary framework for improving cybersecurity risk management",
                "authority_level": "High",
                "scope": "Comprehensive cybersecurity framework"
            },
            FrameworkType.ISO_27001: {
                "name": "ISO/IEC 27001",
                "version": "2013",
                "publisher": "International Organization for Standardization",
                "url": "https://www.iso.org/isoiec-27001-information-security.html",
                "description": "International standard for information security management systems",
                "authority_level": "High",
                "scope": "Information security management"
            },
            FrameworkType.CIS_CONTROLS: {
                "name": "CIS Critical Security Controls",
                "version": "8.0",
                "publisher": "Center for Internet Security",
                "url": "https://www.cisecurity.org/controls/",
                "description": "Prioritized set of actions for cyber defense",
                "authority_level": "High",
                "scope": "Tactical security controls"
            }
            # Add more framework details as needed
        }
        
        return framework_details.get(framework, {
            "name": framework.value,
            "description": "Cybersecurity framework or standard",
            "authority_level": "Medium"
        })
    
    def validate_attribution(self, attribution: SourceAttribution) -> Dict[str, Any]:
        """Validate the quality of a source attribution"""
        validation_results = {
            "is_valid": True,
            "confidence_level": "High",
            "issues": [],
            "recommendations": []
        }
        
        # Check confidence thresholds
        if attribution.confidence_score < 0.5:
            validation_results["issues"].append("Low confidence score")
            validation_results["confidence_level"] = "Low"
        elif attribution.confidence_score < 0.7:
            validation_results["confidence_level"] = "Medium"
        
        # Check source coverage
        if attribution.coverage_score < 0.3:
            validation_results["issues"].append("Poor source coverage")
            validation_results["recommendations"].append("Consider additional framework sources")
        
        # Check source diversity
        frameworks = {source.framework for source in attribution.primary_sources + attribution.supporting_sources}
        if len(frameworks) < 2:
            validation_results["recommendations"].append("Consider sources from multiple frameworks")
        
        # Overall validation
        if len(validation_results["issues"]) > 2:
            validation_results["is_valid"] = False
        
        return validation_results

# Global instance
source_attributor = SourceAttributor()