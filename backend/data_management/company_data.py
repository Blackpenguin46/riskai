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