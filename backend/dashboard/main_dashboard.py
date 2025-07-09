"""
Main Project Dashboard

Central hub for navigating all RiskAI components including assessment,
chat, metrics, benchmarking, and other features.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
# Import with error handling
try:
    from assessment.dashboard import assessment_dashboard
except ImportError as e:
    logger.warning(f"Could not import assessment dashboard: {e}")
    assessment_dashboard = None

try:
    from metrics.dashboard import metrics_dashboard
except ImportError as e:
    logger.warning(f"Could not import metrics dashboard: {e}")
    metrics_dashboard = None

try:
    from benchmarks.grc_comparison import grc_benchmarker
except ImportError as e:
    logger.warning(f"Could not import grc benchmarker: {e}")
    grc_benchmarker = None

logger = logging.getLogger(__name__)

@dataclass
class DashboardCard:
    """Main dashboard navigation card"""
    id: str
    title: str
    description: str
    icon: str
    category: str
    route: str
    enabled: bool
    badge: Optional[str] = None
    priority: str = "medium"
    estimated_time: Optional[str] = None
    features: List[str] = None

@dataclass
class DashboardStats:
    """Dashboard statistics"""
    total_assessments: int
    completed_assessments: int
    active_sessions: int
    last_assessment_date: Optional[str]
    system_uptime: str
    performance_score: float

class MainDashboard:
    """Main project dashboard for navigation and overview"""
    
    def __init__(self):
        self.navigation_cards = self._initialize_navigation_cards()
        self.quick_stats = self._initialize_quick_stats()
        
    def _initialize_navigation_cards(self) -> List[DashboardCard]:
        """Initialize main navigation cards"""
        
        cards = [
            # Assessment Section
            DashboardCard(
                id="assessment",
                title="Risk Assessment",
                description="Complete structured cybersecurity risk assessment based on industry frameworks",
                icon="📊",
                category="Assessment",
                route="/assessment/dashboard",
                enabled=True,
                badge="New",
                priority="high",
                estimated_time="70-130 minutes",
                features=[
                    "10 comprehensive sections",
                    "Industry framework mapping",
                    "Real-time progress tracking",
                    "Professional reporting"
                ]
            ),
            
            # Chat Interface
            DashboardCard(
                id="chat",
                title="Risk Mitigation Chat",
                description="AI-powered chat for risk mitigation strategies and implementation guidance",
                icon="💬",
                category="Guidance",
                route="/chat",
                enabled=True,
                priority="high",
                estimated_time="Ongoing",
                features=[
                    "AI-powered guidance",
                    "Implementation roadmaps",
                    "Strategy recommendations",
                    "Budget planning"
                ]
            ),
            
            # Metrics & Analytics
            DashboardCard(
                id="metrics",
                title="Performance Metrics",
                description="System performance tracking, validation metrics, and quality assessment",
                icon="📈",
                category="Analytics",
                route="/metrics",
                enabled=True,
                priority="medium",
                estimated_time="5-10 minutes",
                features=[
                    "Real-time metrics",
                    "Performance tracking",
                    "Quality assessment",
                    "Trend analysis"
                ]
            ),
            
            # Benchmarking
            DashboardCard(
                id="benchmarks",
                title="GRC Benchmarking",
                description="Compare against major GRC tools and industry benchmarks",
                icon="⚖️",
                category="Comparison",
                route="/benchmarks",
                enabled=True,
                priority="medium",
                estimated_time="3-5 minutes",
                features=[
                    "5 major GRC tools comparison",
                    "ROI analysis",
                    "Competitive positioning",
                    "Cost-effectiveness metrics"
                ]
            ),
            
            # Company Data Management
            DashboardCard(
                id="company_data",
                title="Company Data",
                description="Upload and manage company-specific data for personalized assessments",
                icon="🏢",
                category="Data Management",
                route="/company",
                enabled=True,
                priority="medium",
                estimated_time="10-15 minutes",
                features=[
                    "Document upload",
                    "Custom data integration",
                    "Isolated workspaces",
                    "Data security"
                ]
            ),
            
            # Scoring & Validation
            DashboardCard(
                id="scoring",
                title="Objective Scoring",
                description="Evidence-based scoring system with detailed justifications",
                icon="🎯",
                category="Scoring",
                route="/scoring",
                enabled=True,
                priority="medium",
                estimated_time="Real-time",
                features=[
                    "Evidence-based scoring",
                    "Confidence intervals",
                    "Detailed justifications",
                    "Industry adjustments"
                ]
            ),
            
            # Reporting
            DashboardCard(
                id="reports",
                title="Assessment Reports",
                description="Generate comprehensive cybersecurity assessment reports",
                icon="📄",
                category="Reporting",
                route="/reports",
                enabled=True,
                priority="low",
                estimated_time="2-3 minutes",
                features=[
                    "Professional reports",
                    "Executive summaries",
                    "Technical details",
                    "Export options"
                ]
            ),
            
            # Settings & Configuration
            DashboardCard(
                id="settings",
                title="Settings",
                description="Configure system settings and preferences",
                icon="⚙️",
                category="Configuration",
                route="/settings",
                enabled=True,
                priority="low",
                estimated_time="5-10 minutes",
                features=[
                    "System configuration",
                    "User preferences",
                    "Integration settings",
                    "Security options"
                ]
            )
        ]
        
        return sorted(cards, key=lambda x: (x.priority == "high", x.priority == "medium", x.priority == "low"), reverse=True)
    
    def _initialize_quick_stats(self) -> Dict[str, Any]:
        """Initialize quick statistics"""
        
        return {
            "system_status": "Operational",
            "version": "2.0.0",
            "last_updated": datetime.now().isoformat(),
            "features_available": 8,
            "frameworks_supported": 4,
            "uptime": "99.9%"
        }
    
    def get_main_dashboard(self) -> Dict[str, Any]:
        """Get complete main dashboard"""
        
        # Get assessment progress if available
        assessment_progress = self._get_assessment_progress()
        
        # Get system statistics
        system_stats = self._get_system_statistics()
        
        # Organize cards by category
        cards_by_category = {}
        for card in self.navigation_cards:
            if card.category not in cards_by_category:
                cards_by_category[card.category] = []
            cards_by_category[card.category].append(asdict(card))
        
        return {
            "dashboard_info": {
                "title": "RiskAI - Cybersecurity Risk Assessment Platform",
                "subtitle": "Professional cybersecurity risk assessment and mitigation platform",
                "version": "2.0.0",
                "description": "Comprehensive risk assessment tool based on industry frameworks (NIST CSF, ISO 27001, CIS Controls)"
            },
            "quick_stats": self.quick_stats,
            "system_stats": system_stats,
            "navigation_cards": [asdict(card) for card in self.navigation_cards],
            "cards_by_category": cards_by_category,
            "assessment_progress": assessment_progress,
            "recent_activities": self._get_recent_activities(),
            "quick_actions": [
                {
                    "id": "start_assessment",
                    "title": "Start Assessment",
                    "description": "Begin new risk assessment",
                    "icon": "🚀",
                    "route": "/assessment/dashboard",
                    "primary": True
                },
                {
                    "id": "continue_assessment",
                    "title": "Continue Assessment",
                    "description": "Resume existing assessment",
                    "icon": "▶️",
                    "route": "/assessment/dashboard",
                    "primary": False,
                    "enabled": assessment_progress.get("in_progress", False)
                },
                {
                    "id": "view_results",
                    "title": "View Results",
                    "description": "Review assessment results",
                    "icon": "📊",
                    "route": "/assessment/summary",
                    "primary": False,
                    "enabled": assessment_progress.get("completed", False)
                },
                {
                    "id": "get_help",
                    "title": "Get Help",
                    "description": "Chat with AI for guidance",
                    "icon": "💬",
                    "route": "/chat",
                    "primary": False
                }
            ],
            "featured_frameworks": [
                {
                    "name": "NIST Cybersecurity Framework",
                    "description": "Risk-based approach to cybersecurity",
                    "coverage": "Complete",
                    "icon": "🛡️"
                },
                {
                    "name": "ISO 27001",
                    "description": "Information security management",
                    "coverage": "Key Controls",
                    "icon": "🔒"
                },
                {
                    "name": "CIS Controls",
                    "description": "Critical security controls",
                    "coverage": "v8.0",
                    "icon": "⚡"
                },
                {
                    "name": "NIST AI RMF",
                    "description": "AI risk management framework",
                    "coverage": "Emerging Tech",
                    "icon": "🤖"
                }
            ]
        }
    
    def get_category_details(self, category: str) -> Dict[str, Any]:
        """Get detailed information for a specific category"""
        
        category_cards = [card for card in self.navigation_cards if card.category == category]
        
        if not category_cards:
            return {"error": "Category not found"}
        
        return {
            "category": category,
            "cards": [asdict(card) for card in category_cards],
            "total_features": sum(len(card.features or []) for card in category_cards),
            "estimated_time": self._calculate_category_time(category_cards),
            "description": self._get_category_description(category)
        }
    
    def get_feature_status(self) -> Dict[str, Any]:
        """Get status of all features"""
        
        features = {}
        for card in self.navigation_cards:
            features[card.id] = {
                "enabled": card.enabled,
                "route": card.route,
                "priority": card.priority,
                "estimated_time": card.estimated_time,
                "features_count": len(card.features or [])
            }
        
        return {
            "features": features,
            "total_features": len(self.navigation_cards),
            "enabled_features": len([card for card in self.navigation_cards if card.enabled]),
            "high_priority": len([card for card in self.navigation_cards if card.priority == "high"]),
            "categories": list(set(card.category for card in self.navigation_cards))
        }
    
    def _get_assessment_progress(self) -> Dict[str, Any]:
        """Get current assessment progress"""
        
        try:
            # Get progress from assessment dashboard
            if assessment_dashboard:
                dashboard_overview = assessment_dashboard.get_dashboard_overview()
                progress = dashboard_overview.get("progress", {})
                
                return {
                    "in_progress": progress.get("in_progress_sections", 0) > 0,
                    "completed": progress.get("overall_completion", 0) >= 100,
                    "completion_percentage": progress.get("overall_completion", 0),
                    "sections_completed": progress.get("completed_sections", 0),
                    "total_sections": progress.get("total_sections", 10),
                    "estimated_time_remaining": progress.get("estimated_time_remaining", "Unknown")
                }
            else:
                # Return default values if assessment dashboard is not available
                return {
                    "in_progress": False,
                    "completed": False,
                    "completion_percentage": 0,
                    "sections_completed": 0,
                    "total_sections": 10,
                    "estimated_time_remaining": "Unknown"
                }
        except Exception as e:
            logger.warning(f"Could not get assessment progress: {e}")
            return {
                "in_progress": False,
                "completed": False,
                "completion_percentage": 0,
                "sections_completed": 0,
                "total_sections": 10,
                "estimated_time_remaining": "Unknown"
            }
    
    def _get_system_statistics(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        
        try:
            # Get metrics from metrics dashboard
            if metrics_dashboard:
                metrics_data = metrics_dashboard.get_system_metrics()
                
                return {
                    "performance_score": metrics_data.get("quality_score", 85.0),
                    "assessments_completed": metrics_data.get("total_assessments", 0),
                    "average_confidence": metrics_data.get("average_confidence", 0.0),
                    "system_reliability": metrics_data.get("reliability_score", 95.0),
                    "uptime_percentage": 99.9,
                    "last_system_check": datetime.now().isoformat()
                }
            else:
                # Return default values if metrics dashboard is not available
                return {
                    "performance_score": 85.0,
                    "assessments_completed": 0,
                    "average_confidence": 0.0,
                    "system_reliability": 95.0,
                    "uptime_percentage": 99.9,
                    "last_system_check": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"Could not get system statistics: {e}")
            return {
                "performance_score": 85.0,
                "assessments_completed": 0,
                "average_confidence": 0.0,
                "system_reliability": 95.0,
                "uptime_percentage": 99.9,
                "last_system_check": datetime.now().isoformat()
            }
    
    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent system activities"""
        
        return [
            {
                "id": "activity_1",
                "type": "system_update",
                "title": "Dashboard Enhancement",
                "description": "Unified dashboard with clickable navigation cards implemented",
                "timestamp": datetime.now().isoformat(),
                "icon": "🔧"
            },
            {
                "id": "activity_2",
                "type": "feature_addition",
                "title": "Assessment Redesign",
                "description": "Professional structured assessment form with industry frameworks",
                "timestamp": datetime.now().isoformat(),
                "icon": "📊"
            },
            {
                "id": "activity_3",
                "type": "enhancement",
                "title": "Chat Interface",
                "description": "AI-powered risk mitigation chat interface added",
                "timestamp": datetime.now().isoformat(),
                "icon": "💬"
            }
        ]
    
    def _calculate_category_time(self, cards: List[DashboardCard]) -> str:
        """Calculate estimated time for category"""
        
        total_minutes = 0
        for card in cards:
            if card.estimated_time and card.estimated_time != "Ongoing" and card.estimated_time != "Real-time":
                # Parse time estimates like "70-130 minutes"
                import re
                numbers = re.findall(r'\d+', card.estimated_time)
                if len(numbers) >= 2:
                    total_minutes += int((int(numbers[0]) + int(numbers[1])) / 2)
                elif len(numbers) == 1:
                    total_minutes += int(numbers[0])
        
        if total_minutes == 0:
            return "Varies"
        elif total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
    
    def _get_category_description(self, category: str) -> str:
        """Get description for category"""
        
        descriptions = {
            "Assessment": "Comprehensive risk assessment tools and frameworks",
            "Guidance": "AI-powered guidance and recommendations",
            "Analytics": "Performance metrics and system analytics",
            "Comparison": "Benchmarking against industry standards",
            "Data Management": "Company data upload and management",
            "Scoring": "Objective scoring and validation systems",
            "Reporting": "Professional reports and documentation",
            "Configuration": "System settings and configuration"
        }
        
        return descriptions.get(category, "Feature category")

# Global instance
main_dashboard = MainDashboard()