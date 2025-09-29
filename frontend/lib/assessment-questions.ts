// Comprehensive 120-Question Assessment Bank
// Aligned with SEET paper's holistic approach to emerging technology risk management

export interface Question {
  id: string;
  text: string;
  type: 'boolean' | 'select' | 'multiselect' | 'scale' | 'text';
  options?: string[];
  min?: number;
  max?: number;
  weight: number; // Individual question weight within section
  category?: string; // Sub-category for detailed analysis
}

export interface AssessmentSection {
  id: string;
  name: string;
  description: string;
  weight: number; // Section weight as percentage of overall score
  questions: Question[];
}

// Section weights aligned with SEET paper's holistic risk management approach
// Total: 100% distributed across strategic, technical, and operational dimensions
export const SECTION_WEIGHTS = {
  governance: 20,           // Strategic foundation
  asset_management: 8,      // Technical visibility
  data_protection: 12,      // Technical security
  access_control: 12,       // Technical security
  security_monitoring: 10,  // Technical detection
  incident_response: 10,    // Operational resilience
  business_continuity: 8,   // Operational resilience
  security_awareness: 6,    // Operational culture
  compliance: 4,            // Regulatory alignment
  emerging_tech: 4,         // Innovation risk (SEET focus)
  third_party: 4,           // Extended ecosystem
  risk_management: 2        // Process maturity
};

// Risk level categories with mathematical thresholds
export const RISK_LEVELS = {
  CRITICAL: { min: 0, max: 40, label: 'Critical Risk', color: '#dc2626' },
  HIGH: { min: 41, max: 60, label: 'High Risk', color: '#ea580c' },
  MEDIUM: { min: 61, max: 80, label: 'Medium Risk', color: '#ca8a04' },
  LOW: { min: 81, max: 100, label: 'Low Risk', color: '#16a34a' }
};

export const ASSESSMENT_SECTIONS: AssessmentSection[] = [
  {
    id: 'governance',
    name: 'Governance & Risk Management',
    description: 'Strategic cybersecurity governance, leadership, and risk management processes',
    weight: SECTION_WEIGHTS.governance,
    questions: [
      {
        id: 'gov_001',
        text: 'Does your organization have a formal information security governance framework?',
        type: 'boolean',
        weight: 10,
        category: 'framework'
      },
      {
        id: 'gov_002',
        text: 'How often is your security strategy reviewed and updated?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never'],
        weight: 8,
        category: 'strategy'
      },
      {
        id: 'gov_003',
        text: 'Does your organization have a dedicated Chief Information Security Officer (CISO) or equivalent?',
        type: 'boolean',
        weight: 9,
        category: 'leadership'
      },
      {
        id: 'gov_004',
        text: 'How would you rate executive leadership support for cybersecurity initiatives?',
        type: 'scale',
        min: 1,
        max: 5,
        weight: 10,
        category: 'leadership'
      },
      {
        id: 'gov_005',
        text: 'Does your organization have a formal risk management process?',
        type: 'boolean',
        weight: 10,
        category: 'risk_process'
      },
      {
        id: 'gov_006',
        text: 'How often does your organization conduct formal risk assessments?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never'],
        weight: 9,
        category: 'risk_process'
      },
      {
        id: 'gov_007',
        text: 'Which risk assessment methodologies does your organization use?',
        type: 'multiselect',
        options: ['NIST RMF', 'ISO 31000', 'FAIR', 'OCTAVE', 'Internal methodology', 'None'],
        weight: 8,
        category: 'methodology'
      },
      {
        id: 'gov_008',
        text: 'Does your organization maintain a formal risk register?',
        type: 'boolean',
        weight: 7,
        category: 'documentation'
      },
      {
        id: 'gov_009',
        text: 'How often is the risk register reviewed and updated?',
        type: 'select',
        options: ['Weekly', 'Monthly', 'Quarterly', 'Annually', 'Never', 'No risk register'],
        weight: 6,
        category: 'documentation'
      },
      {
        id: 'gov_010',
        text: 'Does your organization have a security steering committee with executive representation?',
        type: 'boolean',
        weight: 8,
        category: 'governance'
      }
    ]
  },
  {
    id: 'asset_management',
    name: 'Asset Management',
    description: 'IT asset inventory, classification, and lifecycle management',
    weight: SECTION_WEIGHTS.asset_management,
    questions: [
      {
        id: 'asset_001',
        text: 'Does your organization maintain a comprehensive IT asset inventory?',
        type: 'boolean',
        weight: 12,
        category: 'inventory'
      },
      {
        id: 'asset_002',
        text: 'What percentage of your IT assets are included in your inventory?',
        type: 'select',
        options: ['0-25%', '26-50%', '51-75%', '76-90%', '91-100%', 'Unknown'],
        weight: 11,
        category: 'coverage'
      },
      {
        id: 'asset_003',
        text: 'How often is your IT asset inventory updated?',
        type: 'select',
        options: ['Real-time/Automated', 'Daily', 'Weekly', 'Monthly', 'Quarterly or less frequently', 'Never'],
        weight: 10,
        category: 'maintenance'
      },
      {
        id: 'asset_004',
        text: 'Does your organization use automated tools for asset discovery and inventory?',
        type: 'boolean',
        weight: 10,
        category: 'automation'
      },
      {
        id: 'asset_005',
        text: 'Does your organization maintain a software inventory including licenses?',
        type: 'boolean',
        weight: 9,
        category: 'software'
      },
      {
        id: 'asset_006',
        text: 'Does your organization have a formal process for asset lifecycle management?',
        type: 'boolean',
        weight: 9,
        category: 'lifecycle'
      },
      {
        id: 'asset_007',
        text: 'Does your organization classify assets based on criticality or sensitivity?',
        type: 'boolean',
        weight: 11,
        category: 'classification'
      },
      {
        id: 'asset_008',
        text: 'Does your organization track cloud-based assets in your inventory?',
        type: 'boolean',
        weight: 10,
        category: 'cloud'
      },
      {
        id: 'asset_009',
        text: 'Does your organization track IoT devices in your inventory?',
        type: 'boolean',
        weight: 9,
        category: 'iot'
      },
      {
        id: 'asset_010',
        text: 'Does your organization have a process to identify and manage shadow IT?',
        type: 'boolean',
        weight: 9,
        category: 'shadow_it'
      }
    ]
  },
  {
    id: 'data_protection',
    name: 'Data Protection',
    description: 'Data classification, encryption, privacy, and protection controls',
    weight: SECTION_WEIGHTS.data_protection,
    questions: [
      {
        id: 'data_001',
        text: 'Does your organization have a formal data classification policy?',
        type: 'boolean',
        weight: 11,
        category: 'classification'
      },
      {
        id: 'data_002',
        text: 'What percentage of your organization\'s data is classified according to sensitivity?',
        type: 'select',
        options: ['0-25%', '26-50%', '51-75%', '76-90%', '91-100%', 'Unknown'],
        weight: 10,
        category: 'classification'
      },
      {
        id: 'data_003',
        text: 'Which data protection technologies does your organization use?',
        type: 'multiselect',
        options: ['Encryption at rest', 'Encryption in transit', 'DLP solutions', 'Rights management', 'Data masking', 'Tokenization', 'None'],
        weight: 12,
        category: 'technology'
      },
      {
        id: 'data_004',
        text: 'Does your organization encrypt sensitive data at rest using industry-standard algorithms?',
        type: 'boolean',
        weight: 11,
        category: 'encryption'
      },
      {
        id: 'data_005',
        text: 'Does your organization encrypt sensitive data in transit using TLS 1.2 or higher?',
        type: 'boolean',
        weight: 11,
        category: 'encryption'
      },
      {
        id: 'data_006',
        text: 'Does your organization use Data Loss Prevention (DLP) solutions?',
        type: 'boolean',
        weight: 9,
        category: 'dlp'
      },
      {
        id: 'data_007',
        text: 'Does your organization have a formal data retention policy?',
        type: 'boolean',
        weight: 8,
        category: 'retention'
      },
      {
        id: 'data_008',
        text: 'Does your organization have a formal data disposal policy with secure deletion procedures?',
        type: 'boolean',
        weight: 8,
        category: 'disposal'
      },
      {
        id: 'data_009',
        text: 'Does your organization conduct regular data protection impact assessments (DPIAs)?',
        type: 'boolean',
        weight: 9,
        category: 'privacy'
      },
      {
        id: 'data_010',
        text: 'Does your organization have a comprehensive data breach response plan?',
        type: 'boolean',
        weight: 11,
        category: 'breach_response'
      }
    ]
  },
  {
    id: 'access_control',
    name: 'Access Control',
    description: 'Identity management, authentication, authorization, and privileged access',
    weight: SECTION_WEIGHTS.access_control,
    questions: [
      {
        id: 'access_001',
        text: 'Does your organization enforce the principle of least privilege?',
        type: 'boolean',
        weight: 12,
        category: 'least_privilege'
      },
      {
        id: 'access_002',
        text: 'Does your organization use role-based access control (RBAC)?',
        type: 'boolean',
        weight: 10,
        category: 'rbac'
      },
      {
        id: 'access_003',
        text: 'Does your organization require multi-factor authentication (MFA)?',
        type: 'boolean',
        weight: 12,
        category: 'mfa'
      },
      {
        id: 'access_004',
        text: 'For which systems is MFA required?',
        type: 'multiselect',
        options: ['All systems', 'Critical systems only', 'Remote access', 'Admin accounts', 'Cloud services', 'None'],
        weight: 11,
        category: 'mfa'
      },
      {
        id: 'access_005',
        text: 'Does your organization have a formal process for access provisioning with approval workflows?',
        type: 'boolean',
        weight: 9,
        category: 'provisioning'
      },
      {
        id: 'access_006',
        text: 'Does your organization have a formal process for timely access deprovisioning?',
        type: 'boolean',
        weight: 10,
        category: 'deprovisioning'
      },
      {
        id: 'access_007',
        text: 'How often does your organization review user access rights?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never'],
        weight: 10,
        category: 'review'
      },
      {
        id: 'access_008',
        text: 'Does your organization use privileged access management (PAM) solutions?',
        type: 'boolean',
        weight: 11,
        category: 'pam'
      },
      {
        id: 'access_009',
        text: 'Does your organization enforce strong password policies and complexity requirements?',
        type: 'boolean',
        weight: 8,
        category: 'passwords'
      },
      {
        id: 'access_010',
        text: 'Does your organization use single sign-on (SSO) with centralized identity management?',
        type: 'boolean',
        weight: 7,
        category: 'sso'
      }
    ]
  },
  {
    id: 'security_monitoring',
    name: 'Security Monitoring & Detection',
    description: 'Security operations, monitoring, threat detection, and incident identification',
    weight: SECTION_WEIGHTS.security_monitoring,
    questions: [
      {
        id: 'monitor_001',
        text: 'Does your organization use a Security Information and Event Management (SIEM) system?',
        type: 'boolean',
        weight: 12,
        category: 'siem'
      },
      {
        id: 'monitor_002',
        text: 'Does your organization have 24/7 security monitoring capabilities?',
        type: 'boolean',
        weight: 11,
        category: 'monitoring'
      },
      {
        id: 'monitor_003',
        text: 'Does your organization use automated threat detection and response tools?',
        type: 'boolean',
        weight: 11,
        category: 'automation'
      },
      {
        id: 'monitor_004',
        text: 'Which security monitoring capabilities does your organization have?',
        type: 'multiselect',
        options: ['Log collection', 'Event correlation', 'Anomaly detection', 'User behavior analytics', 'Network traffic analysis', 'Endpoint detection and response', 'None'],
        weight: 12,
        category: 'capabilities'
      },
      {
        id: 'monitor_005',
        text: 'Does your organization have defined security alerts and thresholds with documented playbooks?',
        type: 'boolean',
        weight: 10,
        category: 'alerting'
      },
      {
        id: 'monitor_006',
        text: 'How are security alerts triaged in your organization?',
        type: 'select',
        options: ['Automated with human review', 'Manual process', 'Outsourced to MSSP', 'No formal process', 'No alert triaging'],
        weight: 10,
        category: 'triage'
      },
      {
        id: 'monitor_007',
        text: 'Does your organization use threat intelligence feeds to enhance detection?',
        type: 'boolean',
        weight: 9,
        category: 'threat_intel'
      },
      {
        id: 'monitor_008',
        text: 'Does your organization monitor cloud environments with specialized tools?',
        type: 'boolean',
        weight: 9,
        category: 'cloud_monitoring'
      },
      {
        id: 'monitor_009',
        text: 'Does your organization have a security operations center (SOC)?',
        type: 'boolean',
        weight: 8,
        category: 'soc'
      },
      {
        id: 'monitor_010',
        text: 'Does your organization use deception technologies (honeypots, canaries) for threat detection?',
        type: 'boolean',
        weight: 8,
        category: 'deception'
      }
    ]
  },
  {
    id: 'incident_response',
    name: 'Incident Response',
    description: 'Incident response planning, execution, and post-incident activities',
    weight: SECTION_WEIGHTS.incident_response,
    questions: [
      {
        id: 'ir_001',
        text: 'Does your organization have a formal, documented incident response plan?',
        type: 'boolean',
        weight: 12,
        category: 'planning'
      },
      {
        id: 'ir_002',
        text: 'How often is your incident response plan tested through exercises?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never', 'No plan'],
        weight: 11,
        category: 'testing'
      },
      {
        id: 'ir_003',
        text: 'Does your organization conduct tabletop exercises for incident response?',
        type: 'boolean',
        weight: 10,
        category: 'exercises'
      },
      {
        id: 'ir_004',
        text: 'Does your organization have a dedicated incident response team with defined roles?',
        type: 'boolean',
        weight: 11,
        category: 'team'
      },
      {
        id: 'ir_005',
        text: 'Does your organization have predefined incident response playbooks for different incident types?',
        type: 'boolean',
        weight: 10,
        category: 'playbooks'
      },
      {
        id: 'ir_006',
        text: 'Does your organization use automated incident response tools (SOAR)?',
        type: 'boolean',
        weight: 9,
        category: 'automation'
      },
      {
        id: 'ir_007',
        text: 'Does your organization have a process for incident classification and prioritization?',
        type: 'boolean',
        weight: 10,
        category: 'classification'
      },
      {
        id: 'ir_008',
        text: 'Does your organization conduct post-incident reviews and lessons learned sessions?',
        type: 'boolean',
        weight: 11,
        category: 'lessons_learned'
      },
      {
        id: 'ir_009',
        text: 'Does your organization have a formal process for evidence collection and preservation?',
        type: 'boolean',
        weight: 8,
        category: 'forensics'
      },
      {
        id: 'ir_010',
        text: 'Does your organization have a communication plan for security incidents including external stakeholders?',
        type: 'boolean',
        weight: 8,
        category: 'communication'
      }
    ]
  },
  {
    id: 'business_continuity',
    name: 'Business Continuity & Disaster Recovery',
    description: 'Business continuity planning, disaster recovery, and resilience',
    weight: SECTION_WEIGHTS.business_continuity,
    questions: [
      {
        id: 'bc_001',
        text: 'Does your organization have a formal business continuity plan?',
        type: 'boolean',
        weight: 12,
        category: 'planning'
      },
      {
        id: 'bc_002',
        text: 'Does your organization have a formal disaster recovery plan?',
        type: 'boolean',
        weight: 12,
        category: 'disaster_recovery'
      },
      {
        id: 'bc_003',
        text: 'How often are your BC/DR plans tested?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never', 'No plans'],
        weight: 11,
        category: 'testing'
      },
      {
        id: 'bc_004',
        text: 'Has your organization conducted a comprehensive business impact analysis?',
        type: 'boolean',
        weight: 10,
        category: 'bia'
      },
      {
        id: 'bc_005',
        text: 'Does your organization have defined recovery time objectives (RTOs) for critical systems?',
        type: 'boolean',
        weight: 10,
        category: 'rto'
      },
      {
        id: 'bc_006',
        text: 'Does your organization have defined recovery point objectives (RPOs) for critical data?',
        type: 'boolean',
        weight: 10,
        category: 'rpo'
      },
      {
        id: 'bc_007',
        text: 'How often does your organization perform data backups?',
        type: 'select',
        options: ['Real-time/Continuous', 'Daily', 'Weekly', 'Monthly', 'Less frequently', 'No regular backups'],
        weight: 11,
        category: 'backups'
      },
      {
        id: 'bc_008',
        text: 'Does your organization regularly test data restoration procedures?',
        type: 'boolean',
        weight: 10,
        category: 'restoration'
      },
      {
        id: 'bc_009',
        text: 'Does your organization have an alternate processing site or cloud-based DR?',
        type: 'boolean',
        weight: 9,
        category: 'alternate_site'
      },
      {
        id: 'bc_010',
        text: 'Does your organization have a crisis management team with defined communication protocols?',
        type: 'boolean',
        weight: 5,
        category: 'crisis_management'
      }
    ]
  },
  {
    id: 'security_awareness',
    name: 'Security Awareness & Training',
    description: 'Security awareness programs, training, and culture development',
    weight: SECTION_WEIGHTS.security_awareness,
    questions: [
      {
        id: 'aware_001',
        text: 'Does your organization have a formal security awareness program?',
        type: 'boolean',
        weight: 12,
        category: 'program'
      },
      {
        id: 'aware_002',
        text: 'How often does your organization conduct security awareness training?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never', 'No program'],
        weight: 11,
        category: 'frequency'
      },
      {
        id: 'aware_003',
        text: 'Does your organization conduct phishing simulation exercises?',
        type: 'boolean',
        weight: 11,
        category: 'phishing'
      },
      {
        id: 'aware_004',
        text: 'How often does your organization conduct phishing simulations?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never', 'No simulations'],
        weight: 10,
        category: 'phishing'
      },
      {
        id: 'aware_005',
        text: 'Does your organization provide role-based security training?',
        type: 'boolean',
        weight: 10,
        category: 'role_based'
      },
      {
        id: 'aware_006',
        text: 'Does your organization measure the effectiveness of security awareness training?',
        type: 'boolean',
        weight: 11,
        category: 'measurement'
      },
      {
        id: 'aware_007',
        text: 'Does your organization have a security awareness portal or resource center?',
        type: 'boolean',
        weight: 8,
        category: 'resources'
      },
      {
        id: 'aware_008',
        text: 'Does your organization provide security training for developers (secure coding)?',
        type: 'boolean',
        weight: 9,
        category: 'developers'
      },
      {
        id: 'aware_009',
        text: 'Does your organization provide security training for executives?',
        type: 'boolean',
        weight: 9,
        category: 'executives'
      },
      {
        id: 'aware_010',
        text: 'Does your organization have a security champion program?',
        type: 'boolean',
        weight: 9,
        category: 'champions'
      }
    ]
  },
  {
    id: 'compliance',
    name: 'Regulatory Compliance',
    description: 'Regulatory compliance, standards adherence, and audit management',
    weight: SECTION_WEIGHTS.compliance,
    questions: [
      {
        id: 'comp_001',
        text: 'Which regulatory frameworks apply to your organization?',
        type: 'multiselect',
        options: ['GDPR', 'HIPAA', 'PCI DSS', 'SOX', 'CCPA/CPRA', 'GLBA', 'FISMA', 'NIST 800-53', 'ISO 27001', 'None'],
        weight: 12,
        category: 'frameworks'
      },
      {
        id: 'comp_002',
        text: 'Does your organization have a formal compliance program with dedicated resources?',
        type: 'boolean',
        weight: 11,
        category: 'program'
      },
      {
        id: 'comp_003',
        text: 'How often does your organization conduct compliance assessments?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never', 'No assessments'],
        weight: 10,
        category: 'assessments'
      },
      {
        id: 'comp_004',
        text: 'Does your organization use a GRC (Governance, Risk, and Compliance) tool?',
        type: 'boolean',
        weight: 9,
        category: 'tools'
      },
      {
        id: 'comp_005',
        text: 'Does your organization maintain a compliance requirements register?',
        type: 'boolean',
        weight: 10,
        category: 'documentation'
      },
      {
        id: 'comp_006',
        text: 'Does your organization map controls to multiple regulatory frameworks?',
        type: 'boolean',
        weight: 10,
        category: 'mapping'
      },
      {
        id: 'comp_007',
        text: 'Does your organization undergo external compliance audits?',
        type: 'boolean',
        weight: 11,
        category: 'audits'
      },
      {
        id: 'comp_008',
        text: 'Does your organization have a process for tracking and implementing regulatory changes?',
        type: 'boolean',
        weight: 10,
        category: 'change_management'
      },
      {
        id: 'comp_009',
        text: 'Does your organization have a process for managing compliance findings and remediation?',
        type: 'boolean',
        weight: 11,
        category: 'remediation'
      },
      {
        id: 'comp_010',
        text: 'Does your organization have regular compliance reporting to executive leadership?',
        type: 'boolean',
        weight: 6,
        category: 'reporting'
      }
    ]
  },
  {
    id: 'emerging_tech',
    name: 'Emerging Technologies Risk Management',
    description: 'Risk management for AI, IoT, blockchain, quantum computing, and other emerging technologies (SEET focus)',
    weight: SECTION_WEIGHTS.emerging_tech,
    questions: [
      {
        id: 'tech_001',
        text: 'Which emerging technologies is your organization currently using or planning to use?',
        type: 'multiselect',
        options: ['Artificial Intelligence/ML', 'IoT', 'Blockchain', 'Cloud Computing', 'Edge Computing', 'Quantum Computing', '5G', 'None'],
        weight: 12,
        category: 'adoption'
      },
      {
        id: 'tech_002',
        text: 'Does your organization have a formal process for evaluating security risks of new technologies?',
        type: 'boolean',
        weight: 12,
        category: 'risk_evaluation'
      },
      {
        id: 'tech_003',
        text: 'Does your organization have security standards for AI/ML systems including bias detection?',
        type: 'boolean',
        weight: 11,
        category: 'ai_security'
      },
      {
        id: 'tech_004',
        text: 'Does your organization have security standards for IoT devices including device management?',
        type: 'boolean',
        weight: 10,
        category: 'iot_security'
      },
      {
        id: 'tech_005',
        text: 'Does your organization have security standards for blockchain implementations?',
        type: 'boolean',
        weight: 9,
        category: 'blockchain_security'
      },
      {
        id: 'tech_006',
        text: 'Does your organization have a comprehensive cloud security strategy?',
        type: 'boolean',
        weight: 11,
        category: 'cloud_security'
      },
      {
        id: 'tech_007',
        text: 'Does your organization use cloud security posture management (CSPM) tools?',
        type: 'boolean',
        weight: 10,
        category: 'cloud_tools'
      },
      {
        id: 'tech_008',
        text: 'Does your organization have a strategy for quantum-resistant cryptography?',
        type: 'boolean',
        weight: 9,
        category: 'quantum_crypto'
      },
      {
        id: 'tech_009',
        text: 'Does your organization have a formal process for evaluating AI ethics and bias?',
        type: 'boolean',
        weight: 10,
        category: 'ai_ethics'
      },
      {
        id: 'tech_010',
        text: 'Does your organization have governance frameworks for emerging technology adoption?',
        type: 'boolean',
        weight: 6,
        category: 'governance'
      }
    ]
  },
  {
    id: 'third_party',
    name: 'Third-Party Risk Management',
    description: 'Vendor risk management, supply chain security, and third-party governance',
    weight: SECTION_WEIGHTS.third_party,
    questions: [
      {
        id: 'third_001',
        text: 'Does your organization have a formal third-party risk management program?',
        type: 'boolean',
        weight: 12,
        category: 'program'
      },
      {
        id: 'third_002',
        text: 'Does your organization conduct security assessments of third parties before engagement?',
        type: 'boolean',
        weight: 11,
        category: 'assessment'
      },
      {
        id: 'third_003',
        text: 'How often does your organization reassess third-party security?',
        type: 'select',
        options: ['Monthly', 'Quarterly', 'Annually', 'Every 2+ years', 'Never', 'No assessments'],
        weight: 10,
        category: 'reassessment'
      },
      {
        id: 'third_004',
        text: 'Does your organization classify third parties based on risk levels?',
        type: 'boolean',
        weight: 10,
        category: 'classification'
      },
      {
        id: 'third_005',
        text: 'Does your organization include security requirements in third-party contracts?',
        type: 'boolean',
        weight: 11,
        category: 'contracts'
      },
      {
        id: 'third_006',
        text: 'Does your organization have right-to-audit clauses in third-party contracts?',
        type: 'boolean',
        weight: 9,
        category: 'audit_rights'
      },
      {
        id: 'third_007',
        text: 'Does your organization review third-party SOC 2 reports or equivalent certifications?',
        type: 'boolean',
        weight: 10,
        category: 'certifications'
      },
      {
        id: 'third_008',
        text: 'Does your organization have a process for managing fourth-party (sub-vendor) risk?',
        type: 'boolean',
        weight: 9,
        category: 'fourth_party'
      },
      {
        id: 'third_009',
        text: 'Does your organization have a process for managing third-party security incidents?',
        type: 'boolean',
        weight: 10,
        category: 'incident_management'
      },
      {
        id: 'third_010',
        text: 'Does your organization have a formal process for third-party offboarding and data return?',
        type: 'boolean',
        weight: 8,
        category: 'offboarding'
      }
    ]
  },
  {
    id: 'risk_management',
    name: 'Risk Management Process',
    description: 'Risk identification, assessment, treatment, and monitoring processes',
    weight: SECTION_WEIGHTS.risk_management,
    questions: [
      {
        id: 'risk_001',
        text: 'Does your organization have a formal risk management policy approved by senior management?',
        type: 'boolean',
        weight: 12,
        category: 'policy'
      },
      {
        id: 'risk_002',
        text: 'Does your organization use quantitative risk assessment methods?',
        type: 'boolean',
        weight: 11,
        category: 'quantitative'
      },
      {
        id: 'risk_003',
        text: 'Does your organization have defined risk appetite and tolerance statements?',
        type: 'boolean',
        weight: 11,
        category: 'appetite'
      },
      {
        id: 'risk_004',
        text: 'Does your organization have a process for continuous risk monitoring?',
        type: 'boolean',
        weight: 11,
        category: 'monitoring'
      },
      {
        id: 'risk_005',
        text: 'Does your organization have a formal risk treatment plan for identified risks?',
        type: 'boolean',
        weight: 10,
        category: 'treatment'
      },
      {
        id: 'risk_006',
        text: 'Does your organization regularly report risk metrics to the board or senior management?',
        type: 'boolean',
        weight: 10,
        category: 'reporting'
      },
      {
        id: 'risk_007',
        text: 'Does your organization have a process for risk escalation and exception handling?',
        type: 'boolean',
        weight: 9,
        category: 'escalation'
      },
      {
        id: 'risk_008',
        text: 'Does your organization integrate risk management with business planning processes?',
        type: 'boolean',
        weight: 9,
        category: 'integration'
      },
      {
        id: 'risk_009',
        text: 'Does your organization have key risk indicators (KRIs) with defined thresholds?',
        type: 'boolean',
        weight: 8,
        category: 'kris'
      },
      {
        id: 'risk_010',
        text: 'Does your organization conduct scenario-based risk analysis for emerging threats?',
        type: 'boolean',
        weight: 9,
        category: 'scenarios'
      }
    ]
  }
];

// Validation function to ensure question bank integrity
export function validateQuestionBank(): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check total section weights
  const totalWeight = Object.values(SECTION_WEIGHTS).reduce((sum, weight) => sum + weight, 0);
  if (totalWeight !== 100) {
    errors.push(`Total section weights must equal 100%, got ${totalWeight}%`);
  }
  
  // Check each section has exactly 10 questions
  ASSESSMENT_SECTIONS.forEach(section => {
    if (section.questions.length !== 10) {
      errors.push(`Section ${section.id} must have exactly 10 questions, got ${section.questions.length}`);
    }
    
    // Check question weights sum appropriately within section
    const sectionQuestionWeights = section.questions.reduce((sum, q) => sum + q.weight, 0);
    if (sectionQuestionWeights === 0) {
      errors.push(`Section ${section.id} has no question weights defined`);
    }
  });
  
  // Check total questions = 120
  const totalQuestions = ASSESSMENT_SECTIONS.reduce((sum, section) => sum + section.questions.length, 0);
  if (totalQuestions !== 120) {
    errors.push(`Total questions must equal 120, got ${totalQuestions}`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// Get question by ID across all sections
export function getQuestionById(questionId: string): Question | null {
  for (const section of ASSESSMENT_SECTIONS) {
    const question = section.questions.find(q => q.id === questionId);
    if (question) return question;
  }
  return null;
}

// Get section by ID
export function getSectionById(sectionId: string): AssessmentSection | null {
  return ASSESSMENT_SECTIONS.find(s => s.id === sectionId) || null;
}