"""
Company-Specific Data Management Module

Allows companies to upload and integrate their own data (policies, controls, 
assessments) to customize the risk assessment model.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json
import shutil
from pathlib import Path
import hashlib
import re
from enum import Enum

# RAG pipeline imports for custom data processing
try:
    from rag_pipeline.loader import load_documents, chunk_documents
    from rag_pipeline.embedder import get_embedder
    from rag_pipeline.store import store_embeddings
except ImportError:
    # Fallback for testing
    def load_documents(path): return []
    def chunk_documents(docs): return docs
    def get_embedder(): return None
    def store_embeddings(chunks, embedder, persist_dir): return None

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types of documents for AI parsing"""
    POLICY = "policy"
    CONTROL = "control"
    ASSESSMENT = "assessment"
    BENCHMARK = "benchmark"
    PROCEDURE = "procedure"
    STANDARD = "standard"

class ParsedContent(Enum):
    """Types of content extracted from documents"""
    SECURITY_CONTROLS = "security_controls"
    COMPLIANCE_REQUIREMENTS = "compliance_requirements"
    RISK_ASSESSMENTS = "risk_assessments"
    POLICIES = "policies"
    PROCEDURES = "procedures"
    METRICS = "metrics"

@dataclass
class DocumentParsingResult:
    """Result of AI document parsing"""
    document_id: str
    document_name: str
    document_type: DocumentType
    extracted_content: Dict[str, Any]
    confidence_scores: Dict[str, float]
    key_entities: List[Dict[str, Any]]
    security_topics: List[str]
    compliance_frameworks: List[str]
    risk_indicators: List[Dict[str, Any]]
    parsing_timestamp: datetime
    
class AIDocumentParser:
    """AI-powered document parsing for security content extraction"""
    
    def __init__(self):
        self.security_keywords = {
            "access_control": ["access control", "authentication", "authorization", "MFA", "multi-factor", "IAM", "identity"],
            "data_protection": ["encryption", "data protection", "backup", "recovery", "DLP", "data loss prevention"],
            "network_security": ["firewall", "IDS", "IPS", "network security", "VPN", "segmentation"],
            "incident_response": ["incident response", "SIEM", "SOC", "security operations", "threat detection"],
            "compliance": ["compliance", "audit", "SOX", "PCI", "HIPAA", "GDPR", "SOC 2", "ISO 27001"],
            "risk_management": ["risk assessment", "vulnerability", "threat", "risk management", "security risk"],
            "governance": ["governance", "policy", "procedure", "security program", "CISO", "security officer"]
        }
        
        self.compliance_frameworks = [
            "NIST", "ISO 27001", "SOC 2", "PCI DSS", "HIPAA", "GDPR", "CCPA", 
            "SOX", "COBIT", "COSO", "FISMA", "FedRAMP", "CIS Controls"
        ]
    
    def parse_document(self, file_path: str, document_type: DocumentType) -> DocumentParsingResult:
        """Parse document using AI techniques to extract security-relevant content"""
        
        try:
            document_name = os.path.basename(file_path)
            document_id = self._generate_document_id(file_path)
            
            # Read document content
            content = self._extract_text_from_file(file_path)
            
            # Extract security content using AI patterns
            extracted_content = self._extract_security_content(content, document_type)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(content, extracted_content)
            
            # Extract key entities
            key_entities = self._extract_key_entities(content)
            
            # Identify security topics
            security_topics = self._identify_security_topics(content)
            
            # Detect compliance frameworks
            compliance_frameworks = self._detect_compliance_frameworks(content)
            
            # Identify risk indicators
            risk_indicators = self._identify_risk_indicators(content)
            
            return DocumentParsingResult(
                document_id=document_id,
                document_name=document_name,
                document_type=document_type,
                extracted_content=extracted_content,
                confidence_scores=confidence_scores,
                key_entities=key_entities,
                security_topics=security_topics,
                compliance_frameworks=compliance_frameworks,
                risk_indicators=risk_indicators,
                parsing_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {str(e)}")
            return self._create_error_result(file_path, document_type, str(e))
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_extension == '.pdf':
                # For now, return a placeholder - in production, use PyPDF2 or similar
                return f"PDF content from {file_path} - AI parsing would extract actual text here"
            elif file_extension in ['.doc', '.docx']:
                # For now, return a placeholder - in production, use python-docx
                return f"Word document content from {file_path} - AI parsing would extract actual text here"
            elif file_extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            else:
                return f"Unsupported file format: {file_extension}"
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_security_content(self, content: str, document_type: DocumentType) -> Dict[str, Any]:
        """Extract security-relevant content using AI pattern matching"""
        
        extracted = {
            "controls": [],
            "requirements": [],
            "procedures": [],
            "metrics": [],
            "policies": []
        }
        
        # Extract security controls
        control_patterns = [
            r"(?i)(control\s+\w+[\d\.\-]+.*?)(?=\n\n|\n[A-Z]|$)",
            r"(?i)(security\s+control.*?)(?=\n\n|\n[A-Z]|$)",
            r"(?i)(\w+\.\d+\.\d+.*?)(?=\n\n|\n[A-Z]|$)"
        ]
        
        for pattern in control_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            extracted["controls"].extend(matches[:10])  # Limit to prevent overflow
        
        # Extract requirements
        requirement_patterns = [
            r"(?i)(shall\s+.*?)(?=\n|\.)",
            r"(?i)(must\s+.*?)(?=\n|\.)",
            r"(?i)(required\s+to\s+.*?)(?=\n|\.)"
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, content)
            extracted["requirements"].extend(matches[:15])
        
        # Extract procedures based on document type
        if document_type == DocumentType.PROCEDURE:
            procedure_patterns = [
                r"(?i)(step\s+\d+.*?)(?=\nstep|\n\n|$)",
                r"(?i)(\d+\.\s+.*?)(?=\n\d+\.|\n\n|$)"
            ]
            
            for pattern in procedure_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                extracted["procedures"].extend(matches[:20])
        
        return extracted
    
    def _calculate_confidence_scores(self, content: str, extracted_content: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for extracted content"""
        
        scores = {}
        
        # Base confidence on keyword density and extraction quality
        for category, items in extracted_content.items():
            if items:
                # Calculate based on number of items and content quality
                item_count = len(items)
                content_length = len(content)
                
                # Higher confidence for more structured content
                confidence = min(0.95, 0.3 + (item_count * 0.1) + (content_length / 10000 * 0.1))
                scores[category] = round(confidence, 2)
            else:
                scores[category] = 0.1
        
        return scores
    
    def _extract_key_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract key security entities from content"""
        
        entities = []
        
        # Extract system names
        system_patterns = [
            r"(?i)(system\s+\w+)",
            r"(?i)(\w+\s+system)",
            r"(?i)(application\s+\w+)"
        ]
        
        for pattern in system_patterns:
            matches = re.findall(pattern, content)
            for match in matches[:5]:  # Limit results
                entities.append({
                    "type": "system",
                    "value": match,
                    "confidence": 0.8
                })
        
        # Extract role/responsibility entities
        role_patterns = [
            r"(?i)(CISO|security officer|administrator|analyst)",
            r"(?i)(information security manager)",
            r"(?i)(security team)"
        ]
        
        for pattern in role_patterns:
            matches = re.findall(pattern, content)
            for match in matches[:5]:
                entities.append({
                    "type": "role",
                    "value": match,
                    "confidence": 0.9
                })
        
        return entities
    
    def _identify_security_topics(self, content: str) -> List[str]:
        """Identify security topics covered in the document"""
        
        topics = []
        content_lower = content.lower()
        
        for topic, keywords in self.security_keywords.items():
            keyword_count = sum(content_lower.count(keyword.lower()) for keyword in keywords)
            if keyword_count > 0:
                topics.append(topic)
        
        return topics
    
    def _detect_compliance_frameworks(self, content: str) -> List[str]:
        """Detect compliance frameworks mentioned in the document"""
        
        frameworks = []
        content_lower = content.lower()
        
        for framework in self.compliance_frameworks:
            if framework.lower() in content_lower:
                frameworks.append(framework)
        
        return frameworks
    
    def _identify_risk_indicators(self, content: str) -> List[Dict[str, Any]]:
        """Identify risk indicators in the document"""
        
        risk_indicators = []
        
        # High-risk terms
        high_risk_terms = ["critical", "high risk", "vulnerability", "threat", "breach", "incident"]
        medium_risk_terms = ["medium risk", "concern", "gap", "weakness", "deficiency"]
        
        for term in high_risk_terms:
            if term.lower() in content.lower():
                risk_indicators.append({
                    "term": term,
                    "risk_level": "high",
                    "confidence": 0.8
                })
        
        for term in medium_risk_terms:
            if term.lower() in content.lower():
                risk_indicators.append({
                    "term": term,
                    "risk_level": "medium", 
                    "confidence": 0.7
                })
        
        return risk_indicators[:10]  # Limit results
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(file_path.encode()).hexdigest()[:16]
    
    def _create_error_result(self, file_path: str, document_type: DocumentType, error_msg: str) -> DocumentParsingResult:
        """Create error result for failed parsing"""
        return DocumentParsingResult(
            document_id=self._generate_document_id(file_path),
            document_name=os.path.basename(file_path),
            document_type=document_type,
            extracted_content={"error": error_msg},
            confidence_scores={"error": 0.0},
            key_entities=[],
            security_topics=[],
            compliance_frameworks=[],
            risk_indicators=[],
            parsing_timestamp=datetime.now()
        )

@dataclass
class CompanyDataset:
    """Represents a company's custom dataset"""
    company_id: str
    dataset_id: str
    name: str
    description: str
    data_type: str  # 'policies', 'controls', 'assessments', 'benchmarks'
    file_paths: List[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    processing_status: str  # 'pending', 'processing', 'completed', 'error'

@dataclass
class CompanyBenchmark:
    """Company-specific benchmark data"""
    company_id: str
    industry: str
    category: str
    internal_score: float
    target_score: float
    benchmark_source: str
    confidence_level: float
    last_updated: datetime

class CompanyDataManager:
    """Main class for managing company-specific data"""
    
    def __init__(self, base_data_dir: str = "company_data"):
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(exist_ok=True)
        
        # Company data storage
        self.company_datasets: Dict[str, List[CompanyDataset]] = {}
        self.company_benchmarks: Dict[str, List[CompanyBenchmark]] = {}
        
        # Vector databases per company
        self.company_vector_dbs: Dict[str, Any] = {}
        
        # AI document parser
        self.ai_parser = AIDocumentParser()
        
        # Parsed documents storage
        self.parsed_documents: Dict[str, List[DocumentParsingResult]] = {}
        
        # Data types and their processing methods
        self.supported_data_types = {
            'policies': self._process_policy_documents,
            'controls': self._process_control_documents,
            'assessments': self._process_assessment_documents,
            'benchmarks': self._process_benchmark_data,
            'procedures': self._process_procedure_documents
        }
        
        # Security settings
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = {'.pdf', '.docx', '.txt', '.json', '.csv', '.xlsx'}
        
    def create_company_workspace(self, company_id: str, company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create isolated workspace for company data"""
        try:
            company_dir = self.base_data_dir / company_id
            company_dir.mkdir(exist_ok=True)
            
            # Create subdirectories for different data types
            for data_type in self.supported_data_types.keys():
                (company_dir / data_type).mkdir(exist_ok=True)
            
            # Create vector database directory
            vector_db_dir = company_dir / "vectordb"
            vector_db_dir.mkdir(exist_ok=True)
            
            # Save company profile
            profile_file = company_dir / "profile.json"
            with open(profile_file, 'w') as f:
                json.dump({
                    'company_id': company_id,
                    'profile': company_profile,
                    'created_at': datetime.now().isoformat(),
                    'workspace_version': '1.0'
                }, f, indent=2)
            
            # Initialize company data structures
            self.company_datasets[company_id] = []
            self.company_benchmarks[company_id] = []
            
            logger.info(f"Created workspace for company {company_id}")
            
            return {
                'status': 'success',
                'company_id': company_id,
                'workspace_path': str(company_dir),
                'supported_data_types': list(self.supported_data_types.keys())
            }
            
        except Exception as e:
            logger.error(f"Error creating workspace for {company_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def upload_company_data(self, 
                          company_id: str,
                          data_type: str,
                          files: List[Tuple[str, bytes]],  # (filename, content)
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload and process company-specific data"""
        
        try:
            if data_type not in self.supported_data_types:
                return {'status': 'error', 'message': f'Unsupported data type: {data_type}'}
            
            if company_id not in self.company_datasets:
                return {'status': 'error', 'message': f'Company workspace not found: {company_id}'}
            
            # Validate files
            validation_result = self._validate_files(files)
            if validation_result['status'] != 'success':
                return validation_result
            
            # Create dataset
            dataset_id = str(uuid.uuid4())
            company_dir = self.base_data_dir / company_id / data_type
            dataset_dir = company_dir / dataset_id
            dataset_dir.mkdir(exist_ok=True)
            
            # Save files
            file_paths = []
            for filename, content in files:
                file_path = dataset_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(content)
                file_paths.append(str(file_path))
                
                # Calculate file hash for integrity
                file_hash = hashlib.sha256(content).hexdigest()
                logger.info(f"Saved file {filename} with hash {file_hash[:8]}...")
            
            # Create dataset record
            dataset = CompanyDataset(
                company_id=company_id,
                dataset_id=dataset_id,
                name=metadata.get('name', f'{data_type}_{dataset_id[:8]}') if metadata else f'{data_type}_{dataset_id[:8]}',
                description=metadata.get('description', f'Custom {data_type} data') if metadata else f'Custom {data_type} data',
                data_type=data_type,
                file_paths=file_paths,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=metadata or {},
                processing_status='pending'
            )
            
            # Add to company datasets
            self.company_datasets[company_id].append(dataset)
            
            # Process the data
            processing_result = self._process_dataset(dataset)
            
            # Update processing status
            dataset.processing_status = processing_result['status']
            dataset.updated_at = datetime.now()
            
            return {
                'status': 'success',
                'dataset_id': dataset_id,
                'processing_result': processing_result,
                'files_uploaded': len(files)
            }
            
        except Exception as e:
            logger.error(f"Error uploading data for {company_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def upload_with_ai_parsing(self,
                             company_id: str,
                             files: List[Tuple[str, bytes, str]],  # (filename, content, document_type)
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload and process files with AI-powered document parsing"""
        
        try:
            if company_id not in self.company_datasets:
                return {'status': 'error', 'message': f'Company workspace not found: {company_id}'}
            
            # Validate files
            validation_result = self._validate_files([(f[0], f[1]) for f in files])
            if validation_result['status'] != 'success':
                return validation_result
            
            # Create upload session
            upload_id = str(uuid.uuid4())
            company_dir = self.base_data_dir / company_id / "ai_parsed"
            upload_dir = company_dir / upload_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            parsing_results = []
            processed_files = []
            
            # Process each file with AI parsing
            for filename, content, doc_type_str in files:
                try:
                    # Save file temporarily
                    file_path = upload_dir / filename
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    # Convert document type string to enum
                    try:
                        document_type = DocumentType(doc_type_str.lower())
                    except ValueError:
                        document_type = DocumentType.POLICY  # Default fallback
                    
                    # Parse with AI
                    parsing_result = self.ai_parser.parse_document(str(file_path), document_type)
                    parsing_results.append(parsing_result)
                    
                    processed_files.append({
                        'filename': filename,
                        'document_type': doc_type_str,
                        'parsing_status': 'success',
                        'extracted_topics': parsing_result.security_topics,
                        'compliance_frameworks': parsing_result.compliance_frameworks,
                        'confidence_scores': parsing_result.confidence_scores,
                        'key_entities_count': len(parsing_result.key_entities),
                        'risk_indicators_count': len(parsing_result.risk_indicators)
                    })
                    
                except Exception as e:
                    logger.error(f"Error parsing {filename}: {str(e)}")
                    processed_files.append({
                        'filename': filename,
                        'document_type': doc_type_str,
                        'parsing_status': 'error',
                        'error_message': str(e)
                    })
            
            # Store parsing results
            if company_id not in self.parsed_documents:
                self.parsed_documents[company_id] = []
            self.parsed_documents[company_id].extend(parsing_results)
            
            # Generate insights from parsed content
            insights = self._generate_parsing_insights(parsing_results)
            
            # Create enhanced dataset with AI parsing metadata
            dataset_id = str(uuid.uuid4())
            dataset = CompanyDataset(
                company_id=company_id,
                dataset_id=dataset_id,
                name=f"AI Parsed Documents - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"AI-parsed document collection with {len(files)} files",
                data_type='ai_parsed',
                file_paths=[str(upload_dir / f[0]) for f in files],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={
                    'upload_id': upload_id,
                    'ai_parsing_enabled': True,
                    'parsing_insights': insights,
                    'total_files': len(files),
                    'successful_parses': len([f for f in processed_files if f['parsing_status'] == 'success']),
                    **(metadata or {})
                },
                processing_status='completed'
            )
            
            self.company_datasets[company_id].append(dataset)
            
            return {
                'status': 'success',
                'upload_id': upload_id,
                'dataset_id': dataset_id,
                'processed_files': processed_files,
                'parsing_insights': insights,
                'files_uploaded': len(files),
                'successful_parses': len([f for f in processed_files if f['parsing_status'] == 'success'])
            }
            
        except Exception as e:
            logger.error(f"Error in AI-powered upload for {company_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_parsing_results(self, company_id: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Get AI parsing results for a company"""
        
        try:
            if company_id not in self.parsed_documents:
                return {'status': 'error', 'message': 'No parsed documents found for company'}
            
            results = self.parsed_documents[company_id]
            
            if document_id:
                # Filter for specific document
                results = [r for r in results if r.document_id == document_id]
                if not results:
                    return {'status': 'error', 'message': 'Document not found'}
            
            return {
                'status': 'success',
                'company_id': company_id,
                'total_documents': len(results),
                'parsing_results': [asdict(result) for result in results],
                'summary': self._generate_parsing_summary(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting parsing results: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_parsing_insights(self, parsing_results: List[DocumentParsingResult]) -> Dict[str, Any]:
        """Generate insights from AI parsing results"""
        
        if not parsing_results:
            return {}
        
        # Aggregate security topics
        all_topics = []
        for result in parsing_results:
            all_topics.extend(result.security_topics)
        
        topic_frequency = {}
        for topic in all_topics:
            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        # Aggregate compliance frameworks
        all_frameworks = []
        for result in parsing_results:
            all_frameworks.extend(result.compliance_frameworks)
        
        framework_frequency = {}
        for framework in all_frameworks:
            framework_frequency[framework] = framework_frequency.get(framework, 0) + 1
        
        # Calculate average confidence
        total_confidence = 0
        confidence_count = 0
        for result in parsing_results:
            for score in result.confidence_scores.values():
                if isinstance(score, (int, float)):
                    total_confidence += score
                    confidence_count += 1
        
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
        
        # Count risk indicators
        high_risk_count = 0
        medium_risk_count = 0
        for result in parsing_results:
            for indicator in result.risk_indicators:
                if indicator.get('risk_level') == 'high':
                    high_risk_count += 1
                elif indicator.get('risk_level') == 'medium':
                    medium_risk_count += 1
        
        return {
            'total_documents_parsed': len(parsing_results),
            'average_confidence_score': round(avg_confidence, 2),
            'top_security_topics': sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            'compliance_frameworks_found': sorted(framework_frequency.items(), key=lambda x: x[1], reverse=True),
            'risk_indicators': {
                'high_risk_count': high_risk_count,
                'medium_risk_count': medium_risk_count,
                'total_risk_indicators': high_risk_count + medium_risk_count
            },
            'document_type_distribution': self._get_document_type_distribution(parsing_results),
            'parsing_timestamp': datetime.now().isoformat()
        }
    
    def _generate_parsing_summary(self, parsing_results: List[DocumentParsingResult]) -> Dict[str, Any]:
        """Generate summary of parsing results"""
        
        return {
            'total_documents': len(parsing_results),
            'document_types': list(set(r.document_type.value for r in parsing_results)),
            'unique_security_topics': len(set(topic for r in parsing_results for topic in r.security_topics)),
            'compliance_frameworks_mentioned': len(set(fw for r in parsing_results for fw in r.compliance_frameworks)),
            'total_risk_indicators': sum(len(r.risk_indicators) for r in parsing_results),
            'average_entities_per_doc': round(sum(len(r.key_entities) for r in parsing_results) / len(parsing_results), 1) if parsing_results else 0
        }
    
    def _get_document_type_distribution(self, parsing_results: List[DocumentParsingResult]) -> Dict[str, int]:
        """Get distribution of document types"""
        
        distribution = {}
        for result in parsing_results:
            doc_type = result.document_type.value
            distribution[doc_type] = distribution.get(doc_type, 0) + 1
        
        return distribution
    
    def _validate_files(self, files: List[Tuple[str, bytes]]) -> Dict[str, Any]:
        """Validate uploaded files"""
        
        for filename, content in files:
            # Check file size
            if len(content) > self.max_file_size:
                return {
                    'status': 'error',
                    'message': f'File {filename} exceeds maximum size limit ({self.max_file_size / (1024*1024):.1f}MB)'
                }
            
            # Check file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                return {
                    'status': 'error',
                    'message': f'File {filename} has unsupported extension. Allowed: {self.allowed_extensions}'
                }
            
            # Basic content validation
            if len(content) == 0:
                return {
                    'status': 'error',
                    'message': f'File {filename} is empty'
                }
        
        return {'status': 'success'}
    
    def _process_dataset(self, dataset: CompanyDataset) -> Dict[str, Any]:
        """Process dataset based on its type"""
        
        try:
            processor = self.supported_data_types[dataset.data_type]
            return processor(dataset)
            
        except Exception as e:
            logger.error(f"Error processing dataset {dataset.dataset_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_policy_documents(self, dataset: CompanyDataset) -> Dict[str, Any]:
        """Process company policy documents"""
        
        try:
            # Load and chunk documents
            documents = []
            for file_path in dataset.file_paths:
                if file_path.endswith('.pdf'):
                    docs = load_documents(str(Path(file_path).parent))
                    documents.extend(docs)
            
            if not documents:
                return {'status': 'warning', 'message': 'No processable documents found'}
            
            chunks = chunk_documents(documents)
            
            # Create company-specific vector database
            embedder = get_embedder()
            vector_db_path = self.base_data_dir / dataset.company_id / "vectordb" / f"policies_{dataset.dataset_id}"
            vector_db = store_embeddings(chunks, embedder, persist_dir=str(vector_db_path))
            
            # Store reference to vector database
            db_key = f"{dataset.company_id}_policies"
            self.company_vector_dbs[db_key] = vector_db
            
            return {
                'status': 'completed',
                'documents_processed': len(documents),
                'chunks_created': len(chunks),
                'vector_db_path': str(vector_db_path)
            }
            
        except Exception as e:
            logger.error(f"Error processing policy documents: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_control_documents(self, dataset: CompanyDataset) -> Dict[str, Any]:
        """Process company control documents"""
        
        try:
            # Extract control information from documents
            controls = []
            
            for file_path in dataset.file_paths:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        control_data = json.load(f)
                        if isinstance(control_data, list):
                            controls.extend(control_data)
                        else:
                            controls.append(control_data)
                elif file_path.endswith('.csv'):
                    # Process CSV control data
                    import pandas as pd
                    df = pd.read_csv(file_path)
                    controls.extend(df.to_dict('records'))
            
            # Create company-specific control mapping
            control_mapping = {}
            for control in controls:
                control_id = control.get('id', control.get('control_id', ''))
                if control_id:
                    control_mapping[control_id] = control
            
            # Save control mapping
            mapping_file = self.base_data_dir / dataset.company_id / f"controls_{dataset.dataset_id}.json"
            with open(mapping_file, 'w') as f:
                json.dump(control_mapping, f, indent=2)
            
            return {
                'status': 'completed',
                'controls_processed': len(controls),
                'mapping_file': str(mapping_file)
            }
            
        except Exception as e:
            logger.error(f"Error processing control documents: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_assessment_documents(self, dataset: CompanyDataset) -> Dict[str, Any]:
        """Process historical assessment documents"""
        
        try:
            assessments = []
            
            for file_path in dataset.file_paths:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        assessment_data = json.load(f)
                        assessments.append(assessment_data)
            
            # Extract historical scoring patterns
            scoring_patterns = self._extract_scoring_patterns(assessments)
            
            # Save scoring patterns for custom benchmarking
            patterns_file = self.base_data_dir / dataset.company_id / f"scoring_patterns_{dataset.dataset_id}.json"
            with open(patterns_file, 'w') as f:
                json.dump(scoring_patterns, f, indent=2)
            
            return {
                'status': 'completed',
                'assessments_processed': len(assessments),
                'patterns_extracted': len(scoring_patterns),
                'patterns_file': str(patterns_file)
            }
            
        except Exception as e:
            logger.error(f"Error processing assessment documents: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_benchmark_data(self, dataset: CompanyDataset) -> Dict[str, Any]:
        """Process company benchmark data"""
        
        try:
            benchmarks = []
            
            for file_path in dataset.file_paths:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        benchmark_data = json.load(f)
                        
                        # Convert to CompanyBenchmark objects
                        for item in benchmark_data:
                            benchmark = CompanyBenchmark(
                                company_id=dataset.company_id,
                                industry=item.get('industry', 'unknown'),
                                category=item.get('category', ''),
                                internal_score=float(item.get('internal_score', 0)),
                                target_score=float(item.get('target_score', 0)),
                                benchmark_source=item.get('source', 'internal'),
                                confidence_level=float(item.get('confidence', 0.8)),
                                last_updated=datetime.now()
                            )
                            benchmarks.append(benchmark)
            
            # Add to company benchmarks
            if dataset.company_id not in self.company_benchmarks:
                self.company_benchmarks[dataset.company_id] = []
            
            self.company_benchmarks[dataset.company_id].extend(benchmarks)
            
            return {
                'status': 'completed',
                'benchmarks_processed': len(benchmarks)
            }
            
        except Exception as e:
            logger.error(f"Error processing benchmark data: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_procedure_documents(self, dataset: CompanyDataset) -> Dict[str, Any]:
        """Process company procedure documents"""
        
        try:
            # Similar to policy processing but with procedure-specific handling
            documents = []
            for file_path in dataset.file_paths:
                if file_path.endswith('.pdf'):
                    docs = load_documents(str(Path(file_path).parent))
                    documents.extend(docs)
            
            if not documents:
                return {'status': 'warning', 'message': 'No processable procedure documents found'}
            
            chunks = chunk_documents(documents)
            
            # Create procedure-specific vector database
            embedder = get_embedder()
            vector_db_path = self.base_data_dir / dataset.company_id / "vectordb" / f"procedures_{dataset.dataset_id}"
            vector_db = store_embeddings(chunks, embedder, persist_dir=str(vector_db_path))
            
            # Store reference
            db_key = f"{dataset.company_id}_procedures"
            self.company_vector_dbs[db_key] = vector_db
            
            return {
                'status': 'completed',
                'documents_processed': len(documents),
                'chunks_created': len(chunks),
                'vector_db_path': str(vector_db_path)
            }
            
        except Exception as e:
            logger.error(f"Error processing procedure documents: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _extract_scoring_patterns(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract scoring patterns from historical assessments"""
        
        patterns = {
            'category_averages': {},
            'scoring_trends': {},
            'common_responses': {},
            'risk_correlations': {}
        }
        
        try:
            for assessment in assessments:
                risk_table = assessment.get('risk_table', [])
                
                for row in risk_table:
                    category = row.get('category', row.get('id', ''))
                    score = row.get('score', 0)
                    
                    if category not in patterns['category_averages']:
                        patterns['category_averages'][category] = []
                    
                    patterns['category_averages'][category].append(score)
            
            # Calculate averages
            for category, scores in patterns['category_averages'].items():
                patterns['category_averages'][category] = {
                    'mean': sum(scores) / len(scores),
                    'count': len(scores),
                    'min': min(scores),
                    'max': max(scores)
                }
                
        except Exception as e:
            logger.error(f"Error extracting scoring patterns: {str(e)}")
        
        return patterns
    
    def get_company_context(self, company_id: str, query: str, max_results: int = 3) -> str:
        """Get company-specific context for risk assessment"""
        
        try:
            context_parts = []
            
            # Query company-specific vector databases
            for db_key, vector_db in self.company_vector_dbs.items():
                if db_key.startswith(company_id):
                    docs = vector_db.similarity_search(query, k=max_results)
                    for doc in docs:
                        source = doc.metadata.get('source', 'company_data')
                        context_parts.append(f"Company Data ({source}): {doc.page_content}")
            
            return "\n\n".join(context_parts[:max_results])
            
        except Exception as e:
            logger.error(f"Error getting company context: {str(e)}")
            return ""
    
    def get_company_benchmarks(self, company_id: str) -> List[CompanyBenchmark]:
        """Get company-specific benchmarks"""
        return self.company_benchmarks.get(company_id, [])
    
    def list_company_datasets(self, company_id: str) -> List[Dict[str, Any]]:
        """List all datasets for a company"""
        
        datasets = self.company_datasets.get(company_id, [])
        return [asdict(dataset) for dataset in datasets]
    
    def delete_company_data(self, company_id: str, dataset_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete company data (dataset or entire company workspace)"""
        
        try:
            if dataset_id:
                # Delete specific dataset
                datasets = self.company_datasets.get(company_id, [])
                dataset_to_remove = None
                
                for dataset in datasets:
                    if dataset.dataset_id == dataset_id:
                        dataset_to_remove = dataset
                        break
                
                if dataset_to_remove:
                    # Remove files
                    for file_path in dataset_to_remove.file_paths:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    
                    # Remove from list
                    datasets.remove(dataset_to_remove)
                    
                    return {'status': 'success', 'message': f'Dataset {dataset_id} deleted'}
                else:
                    return {'status': 'error', 'message': f'Dataset {dataset_id} not found'}
            else:
                # Delete entire company workspace
                company_dir = self.base_data_dir / company_id
                if company_dir.exists():
                    shutil.rmtree(company_dir)
                
                # Clean up in-memory data
                self.company_datasets.pop(company_id, None)
                self.company_benchmarks.pop(company_id, None)
                
                # Clean up vector databases
                keys_to_remove = [k for k in self.company_vector_dbs.keys() if k.startswith(company_id)]
                for key in keys_to_remove:
                    self.company_vector_dbs.pop(key, None)
                
                return {'status': 'success', 'message': f'Company workspace {company_id} deleted'}
                
        except Exception as e:
            logger.error(f"Error deleting company data: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Global instance
company_data_manager = CompanyDataManager()