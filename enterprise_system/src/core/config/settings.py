"""
Centralized Configuration Management.
All system settings are defined here.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class LLMConfig:
    """Configuration for Language Model"""
    model_name: str = 'gpt-oss:120b-cloud'
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout: int = 120


@dataclass
class VectorStoreConfig:
    """Configuration for Vector Database"""
    persist_directory: str = r'c:\Users\sumit\rag app\chroma_db'
    collection_name: str = 'study_documents'
    chunk_size: int = 700
    chunk_overlap: int = 100
    similarity_top_k: int = 5


@dataclass
class SystemConfig:
    """Master configuration object"""
    llm: LLMConfig
    vector_store: VectorStoreConfig
    documents_folder: str = './documents'
    enable_logging: bool = True
    log_level: str = 'INFO'
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            llm=LLMConfig(
                model_name=os.getenv('LLM_MODEL', 'gpt-oss:120b-cloud'),
                temperature=float(os.getenv('LLM_TEMPERATURE', '0.0'))
            ),
            vector_store=VectorStoreConfig(
                persist_directory=os.getenv('VECTOR_DB_PATH', r'c:\Users\sumit\rag app\chroma_db'),
                chunk_size=int(os.getenv('CHUNK_SIZE', '700'))
            ),
            documents_folder=os.getenv('DOCUMENTS_FOLDER', './documents')
        )


# Global configuration instance
config = SystemConfig.from_env()
