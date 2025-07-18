"""
Risk Mitigation Chat Interface

Provides an AI-powered chat interface for discussing risk mitigation strategies,
governance recommendations, and implementation guidance after assessment completion.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Chat message structure"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None

@dataclass
class ChatSession:
    """Chat session structure"""
    session_id: str
    assessment_id: str
    risk_score: float
    high_risk_areas: List[str]
    messages: List[ChatMessage]
    created_at: datetime
    last_activity: datetime

class RiskMitigationChatBot:
    """AI-powered chat bot for risk mitigation guidance"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ChatSession] = {}
        self.conversation_templates = self._initialize_conversation_templates()
        self.mitigation_strategies = self._initialize_mitigation_strategies()
        
    def _initialize_conversation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize conversation templates for different scenarios"""
        
        return {
            "welcome": {
                "message": "Hello! I'm here to help you develop risk mitigation strategies based on your assessment results. Your overall risk score is {risk_score}/100, with key areas needing attention: {high_risk_areas}. What would you like to focus on first?",
                "suggestions": [
                    "Show me the most critical risks to address",
                    "Help me create an implementation roadmap",
                    "Explain specific mitigation strategies",
                    "Provide governance recommendations"
                ]
            },
            "high_risk_focus": {
                "message": "Based on your assessment, the highest risk areas are: {high_risk_areas}. Let's develop a prioritized action plan. Which area would you like to address first?",
                "suggestions": [
                    "Start with the highest risk area",
                    "Focus on quick wins first",
                    "Address regulatory compliance issues",
                    "Implement foundational controls"
                ]
            },
            "implementation_roadmap": {
                "message": "I'll help you create a phased implementation roadmap. Based on your current maturity level and resources, here's a suggested approach:",
                "suggestions": [
                    "30-day quick wins",
                    "90-day foundational improvements",
                    "1-year strategic initiatives",
                    "Budget and resource planning"
                ]
            },
            "governance_recommendations": {
                "message": "For effective cybersecurity governance, I recommend focusing on these key areas based on your assessment:",
                "suggestions": [
                    "Board-level oversight",
                    "Policy development",
                    "Risk management processes",
                    "Compliance frameworks"
                ]
            }
        }
    
    def _initialize_mitigation_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mitigation strategies database"""
        
        return {
            "governance": {
                "strategies": [
                    {
                        "name": "Establish Cybersecurity Governance Committee",
                        "description": "Create a cross-functional committee with executive sponsorship",
                        "framework": "NIST CSF ID.GV-2",
                        "implementation": [
                            "Define committee charter and responsibilities",
                            "Select committee members from key business units",
                            "Establish meeting cadence and reporting structure",
                            "Define decision-making authority"
                        ],
                        "timeline": "30-60 days",
                        "cost": "Low",
                        "impact": "High"
                    },
                    {
                        "name": "Develop Cybersecurity Policy Framework",
                        "description": "Create comprehensive cybersecurity policies aligned with business objectives",
                        "framework": "ISO 27001 A.5.1.1",
                        "implementation": [
                            "Conduct policy gap analysis",
                            "Develop policy templates",
                            "Engage stakeholders for review",
                            "Implement policy management system"
                        ],
                        "timeline": "90-120 days",
                        "cost": "Medium",
                        "impact": "High"
                    }
                ]
            },
            "access_control": {
                "strategies": [
                    {
                        "name": "Implement Multi-Factor Authentication",
                        "description": "Deploy MFA across all systems and applications",
                        "framework": "NIST CSF PR.AC-1",
                        "implementation": [
                            "Conduct MFA readiness assessment",
                            "Select appropriate MFA solution",
                            "Pilot with high-risk users",
                            "Roll out to all users with training"
                        ],
                        "timeline": "60-90 days",
                        "cost": "Medium",
                        "impact": "High"
                    },
                    {
                        "name": "Deploy Privileged Access Management",
                        "description": "Implement PAM solution for privileged account management",
                        "framework": "NIST CSF PR.AC-4",
                        "implementation": [
                            "Inventory privileged accounts",
                            "Select PAM solution",
                            "Configure vault and workflows",
                            "Onboard privileged users"
                        ],
                        "timeline": "120-180 days",
                        "cost": "High",
                        "impact": "High"
                    }
                ]
            },
            "monitoring": {
                "strategies": [
                    {
                        "name": "Implement Security Information and Event Management (SIEM)",
                        "description": "Deploy SIEM for centralized security monitoring",
                        "framework": "NIST CSF DE.AE-2",
                        "implementation": [
                            "Define use cases and requirements",
                            "Select SIEM solution",
                            "Configure log sources and correlation rules",
                            "Train security operations team"
                        ],
                        "timeline": "180-240 days",
                        "cost": "High",
                        "impact": "High"
                    },
                    {
                        "name": "Deploy Endpoint Detection and Response (EDR)",
                        "description": "Implement EDR for endpoint threat detection",
                        "framework": "NIST CSF DE.CM-1",
                        "implementation": [
                            "Evaluate EDR solutions",
                            "Pilot on subset of endpoints",
                            "Configure detection rules",
                            "Deploy to all endpoints"
                        ],
                        "timeline": "90-120 days",
                        "cost": "Medium",
                        "impact": "High"
                    }
                ]
            },
            "incident_response": {
                "strategies": [
                    {
                        "name": "Develop Incident Response Plan",
                        "description": "Create comprehensive incident response procedures",
                        "framework": "NIST CSF RS.RP-1",
                        "implementation": [
                            "Define incident categories and severity levels",
                            "Create response procedures and playbooks",
                            "Establish communication protocols",
                            "Test plan with tabletop exercises"
                        ],
                        "timeline": "60-90 days",
                        "cost": "Low",
                        "impact": "High"
                    },
                    {
                        "name": "Establish Security Operations Center (SOC)",
                        "description": "Create dedicated SOC for continuous monitoring",
                        "framework": "NIST CSF RS.RP-1",
                        "implementation": [
                            "Define SOC requirements and staffing",
                            "Select monitoring tools and technologies",
                            "Develop SOC procedures and workflows",
                            "Train SOC analysts"
                        ],
                        "timeline": "180-270 days",
                        "cost": "Very High",
                        "impact": "Very High"
                    }
                ]
            },
            "data_protection": {
                "strategies": [
                    {
                        "name": "Implement Data Loss Prevention (DLP)",
                        "description": "Deploy DLP solution to prevent data exfiltration",
                        "framework": "NIST CSF PR.DS-3",
                        "implementation": [
                            "Classify data and define protection requirements",
                            "Select DLP solution",
                            "Configure policies and rules",
                            "Monitor and tune DLP system"
                        ],
                        "timeline": "120-180 days",
                        "cost": "Medium",
                        "impact": "Medium"
                    },
                    {
                        "name": "Implement Data Encryption",
                        "description": "Deploy encryption for data at rest and in transit",
                        "framework": "NIST CSF PR.DS-1",
                        "implementation": [
                            "Conduct data encryption assessment",
                            "Select encryption solutions",
                            "Implement encryption policies",
                            "Monitor encryption compliance"
                        ],
                        "timeline": "90-150 days",
                        "cost": "Medium",
                        "impact": "High"
                    }
                ]
            }
        }
    
    def start_chat_session(self, assessment_id: str, assessment_results: Dict[str, Any]) -> str:
        """Start a new chat session based on assessment results"""
        
        session_id = f"chat_{assessment_id}_{int(datetime.now().timestamp())}"
        
        # Extract key information from assessment
        risk_score = assessment_results.get('overall_weighted_score', 0)
        risk_table = assessment_results.get('risk_table', [])
        
        # Identify high-risk areas (score < 6)
        high_risk_areas = [
            row['category'] for row in risk_table 
            if row.get('score', 10) < 6
        ][:3]  # Top 3 high-risk areas
        
        # Create welcome message
        welcome_template = self.conversation_templates['welcome']
        welcome_message = welcome_template['message'].format(
            risk_score=risk_score,
            high_risk_areas=", ".join(high_risk_areas) if high_risk_areas else "None identified"
        )
        
        # Create session
        session = ChatSession(
            session_id=session_id,
            assessment_id=assessment_id,
            risk_score=risk_score,
            high_risk_areas=high_risk_areas,
            messages=[
                ChatMessage(
                    id=f"msg_{session_id}_1",
                    role="assistant",
                    content=welcome_message,
                    timestamp=datetime.now(),
                    context={"suggestions": welcome_template['suggestions']}
                )
            ],
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        return session_id
    
    def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process user message and generate AI response"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Add user message to session
        user_msg = ChatMessage(
            id=f"msg_{session_id}_{len(session.messages) + 1}",
            role="user",
            content=user_message,
            timestamp=datetime.now()
        )
        session.messages.append(user_msg)
        
        # Generate AI response
        ai_response = self._generate_ai_response(session, user_message)
        
        # Add AI response to session
        ai_msg = ChatMessage(
            id=f"msg_{session_id}_{len(session.messages) + 1}",
            role="assistant",
            content=ai_response["content"],
            timestamp=datetime.now(),
            context=ai_response.get("context", {})
        )
        session.messages.append(ai_msg)
        
        # Update session activity
        session.last_activity = datetime.now()
        
        return {
            "message": ai_response["content"],
            "suggestions": ai_response.get("context", {}).get("suggestions", []),
            "strategies": ai_response.get("strategies", []),
            "session_id": session_id
        }
    
    def _generate_ai_response(self, session: ChatSession, user_message: str) -> Dict[str, Any]:
        """Generate AI response based on user message and session context"""
        
        user_message_lower = user_message.lower()
        
        # Intent detection
        if any(keyword in user_message_lower for keyword in ["critical", "highest", "priority", "urgent"]):
            return self._handle_critical_risks(session)
        
        elif any(keyword in user_message_lower for keyword in ["roadmap", "plan", "implementation", "timeline"]):
            return self._handle_implementation_roadmap(session)
        
        elif any(keyword in user_message_lower for keyword in ["governance", "policy", "board", "management"]):
            return self._handle_governance_recommendations(session)
        
        elif any(keyword in user_message_lower for keyword in ["strategy", "mitigation", "control", "solution"]):
            return self._handle_mitigation_strategies(session, user_message)
        
        elif any(keyword in user_message_lower for keyword in ["cost", "budget", "resource", "staff"]):
            return self._handle_resource_planning(session)
        
        elif any(keyword in user_message_lower for keyword in ["compliance", "regulation", "audit", "framework"]):
            return self._handle_compliance_guidance(session)
        
        else:
            # Default response with suggestions
            return {
                "content": "I can help you with various aspects of risk mitigation. What would you like to focus on?",
                "context": {
                    "suggestions": [
                        "Show me critical risks to address",
                        "Create implementation roadmap",
                        "Governance recommendations",
                        "Compliance guidance",
                        "Budget and resource planning"
                    ]
                }
            }
    
    def _handle_critical_risks(self, session: ChatSession) -> Dict[str, Any]:
        """Handle critical risk discussion"""
        
        if not session.high_risk_areas:
            return {
                "content": "Great news! Based on your assessment, you don't have any critical risk areas. Your overall score of {:.1f}/100 indicates a solid security posture. Let's focus on continuous improvement and optimization.".format(session.risk_score),
                "context": {
                    "suggestions": [
                        "Optimize existing controls",
                        "Implement advanced security measures",
                        "Develop security metrics",
                        "Plan for emerging threats"
                    ]
                }
            }
        
        primary_risk = session.high_risk_areas[0]
        strategies = self._get_strategies_for_area(primary_risk)
        
        response = f"Your most critical risk area is **{primary_risk}**. Here are immediate actions you should take:\n\n"
        
        for i, strategy in enumerate(strategies[:2], 1):
            response += f"{i}. **{strategy['name']}** ({strategy['timeline']})\n"
            response += f"   - {strategy['description']}\n"
            response += f"   - Framework: {strategy['framework']}\n"
            response += f"   - Cost: {strategy['cost']}, Impact: {strategy['impact']}\n\n"
        
        return {
            "content": response,
            "context": {
                "suggestions": [
                    f"Tell me more about {primary_risk}",
                    "Show implementation steps",
                    "What about the other risk areas?",
                    "Create a detailed action plan"
                ]
            },
            "strategies": strategies[:2]
        }
    
    def _handle_implementation_roadmap(self, session: ChatSession) -> Dict[str, Any]:
        """Handle implementation roadmap discussion"""
        
        response = f"Based on your risk score of {session.risk_score:.1f}/100, here's a phased implementation roadmap:\n\n"
        
        # Phase 1: Quick wins (30 days)
        response += "**Phase 1: Quick Wins (30 days)**\n"
        quick_wins = self._get_quick_wins(session.high_risk_areas)
        for win in quick_wins:
            response += f"- {win}\n"
        response += "\n"
        
        # Phase 2: Foundational improvements (90 days)
        response += "**Phase 2: Foundational Improvements (90 days)**\n"
        foundational = self._get_foundational_improvements(session.high_risk_areas)
        for improvement in foundational:
            response += f"- {improvement}\n"
        response += "\n"
        
        # Phase 3: Strategic initiatives (1 year)
        response += "**Phase 3: Strategic Initiatives (1 year)**\n"
        strategic = self._get_strategic_initiatives(session.high_risk_areas)
        for initiative in strategic:
            response += f"- {initiative}\n"
        
        return {
            "content": response,
            "context": {
                "suggestions": [
                    "Focus on Phase 1 quick wins",
                    "Estimate budget requirements",
                    "Identify resource needs",
                    "Create detailed project plans"
                ]
            }
        }
    
    def _handle_governance_recommendations(self, session: ChatSession) -> Dict[str, Any]:
        """Handle governance recommendations"""
        
        governance_strategies = self.mitigation_strategies.get('governance', {}).get('strategies', [])
        
        response = "For effective cybersecurity governance, I recommend focusing on these key areas:\n\n"
        
        for i, strategy in enumerate(governance_strategies, 1):
            response += f"{i}. **{strategy['name']}**\n"
            response += f"   - {strategy['description']}\n"
            response += f"   - Timeline: {strategy['timeline']}\n"
            response += f"   - Framework: {strategy['framework']}\n\n"
        
        response += "Would you like me to elaborate on any of these recommendations or help you prioritize them based on your current situation?"
        
        return {
            "content": response,
            "context": {
                "suggestions": [
                    "Help me prioritize governance initiatives",
                    "Show implementation steps",
                    "Board presentation materials",
                    "Policy development guidance"
                ]
            },
            "strategies": governance_strategies
        }
    
    def _handle_mitigation_strategies(self, session: ChatSession, user_message: str) -> Dict[str, Any]:
        """Handle specific mitigation strategy requests"""
        
        # Try to identify specific area from user message
        area = None
        for risk_area in session.high_risk_areas:
            if risk_area.lower() in user_message.lower():
                area = risk_area
                break
        
        if not area and session.high_risk_areas:
            area = session.high_risk_areas[0]  # Default to highest risk
        
        if area:
            strategies = self._get_strategies_for_area(area)
            response = f"Here are specific mitigation strategies for **{area}**:\n\n"
            
            for i, strategy in enumerate(strategies, 1):
                response += f"{i}. **{strategy['name']}**\n"
                response += f"   - {strategy['description']}\n"
                response += f"   - Timeline: {strategy['timeline']}\n"
                response += f"   - Cost: {strategy['cost']}, Impact: {strategy['impact']}\n\n"
            
            return {
                "content": response,
                "context": {
                    "suggestions": [
                        f"Show implementation steps for {area}",
                        "Compare different strategies",
                        "Estimate costs and resources",
                        "Create implementation plan"
                    ]
                },
                "strategies": strategies
            }
        
        return {
            "content": "I can provide mitigation strategies for various security areas. Which area would you like to focus on?",
            "context": {
                "suggestions": session.high_risk_areas[:4] if session.high_risk_areas else [
                    "Access Control",
                    "Data Protection", 
                    "Incident Response",
                    "Security Monitoring"
                ]
            }
        }
    
    def _handle_resource_planning(self, session: ChatSession) -> Dict[str, Any]:
        """Handle resource and budget planning"""
        
        response = "Based on your risk profile, here's a resource planning guide:\n\n"
        
        # Budget estimates
        response += "**Budget Estimates by Category:**\n"
        budget_categories = {
            "Quick Wins (30 days)": "$10,000 - $50,000",
            "Foundational Improvements (90 days)": "$50,000 - $200,000",
            "Strategic Initiatives (1 year)": "$200,000 - $500,000"
        }
        
        for category, budget in budget_categories.items():
            response += f"- {category}: {budget}\n"
        
        response += "\n**Staffing Recommendations:**\n"
        response += "- Security Lead/Manager: 1 FTE\n"
        response += "- Security Analyst: 1-2 FTE\n"
        response += "- Compliance Specialist: 0.5-1 FTE\n"
        response += "- IT Support: 0.5 FTE\n"
        
        response += "\n**External Resources:**\n"
        response += "- Security consulting: $50,000 - $100,000\n"
        response += "- Penetration testing: $25,000 - $50,000\n"
        response += "- Compliance audit: $15,000 - $30,000\n"
        
        return {
            "content": response,
            "context": {
                "suggestions": [
                    "Detailed budget breakdown",
                    "ROI analysis",
                    "Vendor recommendations",
                    "Staffing roadmap"
                ]
            }
        }
    
    def _handle_compliance_guidance(self, session: ChatSession) -> Dict[str, Any]:
        """Handle compliance and regulatory guidance"""
        
        response = "Here's compliance guidance based on common regulatory frameworks:\n\n"
        
        compliance_areas = {
            "NIST Cybersecurity Framework": [
                "Implement risk management process",
                "Establish governance structure",
                "Deploy protective controls",
                "Implement detection capabilities",
                "Develop response procedures"
            ],
            "ISO 27001": [
                "Conduct risk assessment",
                "Implement information security management system",
                "Establish security controls",
                "Monitor and review processes",
                "Continuous improvement"
            ],
            "SOC 2": [
                "Document security policies",
                "Implement access controls",
                "Monitor system activities",
                "Incident response procedures",
                "Regular security reviews"
            ]
        }
        
        for framework, requirements in compliance_areas.items():
            response += f"**{framework}:**\n"
            for req in requirements:
                response += f"- {req}\n"
            response += "\n"
        
        return {
            "content": response,
            "context": {
                "suggestions": [
                    "Framework-specific guidance",
                    "Compliance gap analysis",
                    "Audit preparation",
                    "Documentation templates"
                ]
            }
        }
    
    def _get_strategies_for_area(self, area: str) -> List[Dict[str, Any]]:
        """Get mitigation strategies for specific area"""
        
        # Map risk areas to strategy categories
        area_mapping = {
            "Access Management": "access_control",
            "Data Sensitivity": "data_protection",
            "Incident Response": "incident_response",
            "Security Monitoring": "monitoring",
            "Governance": "governance"
        }
        
        # Find matching category
        category = None
        for risk_area, strategy_category in area_mapping.items():
            if risk_area.lower() in area.lower():
                category = strategy_category
                break
        
        if category and category in self.mitigation_strategies:
            return self.mitigation_strategies[category]["strategies"]
        
        # Default to governance strategies
        return self.mitigation_strategies["governance"]["strategies"]
    
    def _get_quick_wins(self, high_risk_areas: List[str]) -> List[str]:
        """Get quick win recommendations"""
        
        quick_wins = [
            "Enable multi-factor authentication for all accounts",
            "Conduct security awareness training",
            "Update and patch all systems",
            "Implement basic access controls",
            "Create incident response contact list"
        ]
        
        return quick_wins[:3]
    
    def _get_foundational_improvements(self, high_risk_areas: List[str]) -> List[str]:
        """Get foundational improvement recommendations"""
        
        foundational = [
            "Implement comprehensive logging and monitoring",
            "Deploy endpoint detection and response (EDR)",
            "Create formal security policies and procedures",
            "Establish vulnerability management program",
            "Implement data loss prevention (DLP)"
        ]
        
        return foundational[:3]
    
    def _get_strategic_initiatives(self, high_risk_areas: List[str]) -> List[str]:
        """Get strategic initiative recommendations"""
        
        strategic = [
            "Implement Security Information and Event Management (SIEM)",
            "Establish Security Operations Center (SOC)",
            "Deploy advanced threat detection capabilities",
            "Implement zero-trust architecture",
            "Develop security automation and orchestration"
        ]
        
        return strategic[:3]
    
    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get chat session history"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "assessment_id": session.assessment_id,
            "risk_score": session.risk_score,
            "high_risk_areas": session.high_risk_areas,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "context": msg.context
                }
                for msg in session.messages
            ],
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }

# Global instance
risk_mitigation_chat = RiskMitigationChatBot()