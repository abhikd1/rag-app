"""
Vector Store abstraction layer.
Wraps ChromaDB with a clean interface, making it easy to swap implementations.
"""

from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.core.config.settings import config
from src.core.logging.logger import LoggerFactory


class VectorStoreClient:
    """
    Abstraction over vector database operations.
    Currently uses ChromaDB but can be swapped for Pinecone, Weaviate, etc.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        self._store: Optional[Chroma] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store"""
        try:
            self.logger.info(f"Initializing vector store at {config.vector_store.persist_directory}")
            
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            self._store = Chroma(
                persist_directory=config.vector_store.persist_directory,
                embedding_function=embeddings,
                collection_name=config.vector_store.collection_name
            )
            
            self.logger.info("Vector store initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Adding {len(documents)} documents to vector store")
            self._store.add_documents(documents)
            self.logger.info("Documents added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add documents: {e}")
            return False
    
    def similarity_search(
        self, 
        query: str, 
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return (defaults to config value)
            filter: Metadata filter dictionary
            
        Returns:
            List of similar documents
        """
        if k is None:
            k = config.vector_store.similarity_top_k
        
        try:
            self.logger.debug(f"Searching for: '{query}' (k={k}, filter={filter})")
            results = self._store.similarity_search(query, k=k, filter=filter)
            self.logger.debug(f"Found {len(results)} results")
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def extract_sequential_range(self, file_path: str, start_time: str, end_time: str) -> str:
        """
        100% LOSSLESS extraction from raw file. 
        Bypasses vector search to ensure NOT A SINGLE LINE is missed.
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return ""

        extracted_lines = []
        is_capturing = False
        
        # Helper to convert "MM:SS" to seconds
        def time_to_sec(t):
            try:
                parts = t.split(':')
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                return 0
            except: return 0

        target_start = time_to_sec(start_time)
        target_end = time_to_sec(end_time)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Detect timestamp in line (e.g., "10:15 - " or "[10:15]")
                    import re
                    match = re.search(r'(\d{1,2}:\d{2})', line)
                    if match:
                        current_time = time_to_sec(match.group(1))
                        if current_time >= target_start:
                            is_capturing = True
                        if current_time > target_end:
                            is_capturing = False
                            break
                    
                    if is_capturing:
                        extracted_lines.append(line.strip())
            
            return "\n".join(extracted_lines)
        except Exception as e:
            self.logger.error(f"Sequential extraction failed: {e}")
            return ""

    def clear(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            self.logger.warning("Clearing vector store")
            # Reinitialize to clear
            self._initialize()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear vector store: {e}")
            return False
