"""
TEP RAG (Retrieval-Augmented Generation) System
Integrates knowledge database with existing fault analysis LLM system
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class TEPKnowledgeRAG:
    """
    RAG system for Tennessee Eastman Process fault analysis
    Integrates PDF knowledge base with existing LLM system
    """
    
    def __init__(self, knowledge_folder: str = "log_materials", db_path: str = "knowledge_db"):
        """
        Initialize RAG system
        
        Args:
            knowledge_folder: Folder containing PDF documents
            db_path: Path for ChromaDB storage
        """
        self.knowledge_folder = Path(knowledge_folder)
        self.db_path = Path(db_path)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection = self.client.get_or_create_collection(
            name="tep_knowledge",
            metadata={"description": "TEP fault analysis knowledge base"}
        )
        
        # Initialize sentence transformer for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Track processed documents
        self.processed_docs = self._load_processed_docs()
        
        logger.info(f"RAG system initialized with {self.collection.count()} documents")
    
    def _load_processed_docs(self) -> Dict[str, str]:
        """Load list of already processed documents with their hashes"""
        processed_file = self.db_path / "processed_docs.json"
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_processed_docs(self):
        """Save list of processed documents"""
        processed_file = self.db_path / "processed_docs.json"
        processed_file.parent.mkdir(parents=True, exist_ok=True)
        with open(processed_file, 'w') as f:
            json.dump(self.processed_docs, f, indent=2)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file for change detection"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from PDF and split into chunks
        
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    
                    if text.strip():  # Only process non-empty pages
                        # Split page into smaller chunks (paragraphs)
                        paragraphs = text.split('\n\n')
                        
                        for para_num, paragraph in enumerate(paragraphs):
                            if len(paragraph.strip()) > 50:  # Filter out very short chunks
                                chunks.append({
                                    'text': paragraph.strip(),
                                    'source': pdf_path.name,
                                    'page': page_num + 1,
                                    'chunk': para_num + 1,
                                    'metadata': {
                                        'file_path': str(pdf_path),
                                        'page_number': page_num + 1,
                                        'chunk_number': para_num + 1,
                                        'processed_date': datetime.now().isoformat()
                                    }
                                })
        
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        
        return chunks
    
    def index_documents(self, force_reindex: bool = False) -> int:
        """
        Index all PDF documents in the knowledge folder
        
        Args:
            force_reindex: If True, reprocess all documents regardless of changes
            
        Returns:
            Number of new documents processed
        """
        if not self.knowledge_folder.exists():
            logger.warning(f"Knowledge folder {self.knowledge_folder} does not exist")
            return 0
        
        pdf_files = list(self.knowledge_folder.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.knowledge_folder}")
            return 0
        
        new_docs_count = 0
        
        for pdf_file in pdf_files:
            file_hash = self._get_file_hash(pdf_file)
            
            # Check if document needs processing
            if not force_reindex and pdf_file.name in self.processed_docs:
                if self.processed_docs[pdf_file.name] == file_hash:
                    logger.debug(f"Skipping {pdf_file.name} - already processed")
                    continue
            
            logger.info(f"Processing {pdf_file.name}...")
            
            # Extract text chunks
            chunks = self.extract_text_from_pdf(pdf_file)
            
            if chunks:
                # Prepare data for ChromaDB
                documents = [chunk['text'] for chunk in chunks]
                metadatas = [chunk['metadata'] for chunk in chunks]
                ids = [f"{pdf_file.stem}_page{chunk['page']}_chunk{chunk['chunk']}" 
                      for chunk in chunks]
                
                # Add to vector database
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # Update processed docs tracking
                self.processed_docs[pdf_file.name] = file_hash
                new_docs_count += 1
                
                logger.info(f"Indexed {len(chunks)} chunks from {pdf_file.name}")
        
        # Save processed docs list
        self._save_processed_docs()
        
        logger.info(f"Indexing complete. Processed {new_docs_count} new documents")
        return new_docs_count
    
    def search_knowledge(self, query: str, n_results: int = 5, 
                        min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant information
        
        Args:
            query: Search query (fault symptoms, process conditions, etc.)
            n_results: Maximum number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of relevant knowledge chunks with metadata
        """
        if self.collection.count() == 0:
            logger.warning("Knowledge base is empty. Run index_documents() first.")
            return []
        
        try:
            # Search vector database
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            knowledge_chunks = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity (ChromaDB uses cosine distance)
                    similarity = 1 - distance
                    
                    if similarity >= min_similarity:
                        knowledge_chunks.append({
                            'text': doc,
                            'source': metadata.get('file_path', 'Unknown'),
                            'page': metadata.get('page_number', 0),
                            'similarity': round(similarity, 3),
                            'metadata': metadata
                        })
            
            logger.info(f"Found {len(knowledge_chunks)} relevant knowledge chunks for query: {query[:50]}...")
            return knowledge_chunks
        
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def enhance_prompt_with_knowledge(self, original_prompt: str, fault_features: List[str], 
                                    fault_data: Dict[str, Any]) -> str:
        """
        Enhance the original fault analysis prompt with relevant knowledge
        
        Args:
            original_prompt: Original LLM prompt
            fault_features: List of top contributing features
            fault_data: Fault analysis data
            
        Returns:
            Enhanced prompt with knowledge context
        """
        # Create search queries based on fault features and data
        search_queries = []
        
        # Query based on fault features
        if fault_features:
            feature_query = f"fault analysis {' '.join(fault_features[:3])}"
            search_queries.append(feature_query)
        
        # Query based on fault type if available
        if 'fault_type' in fault_data:
            fault_type_query = f"fault type {fault_data['fault_type']} troubleshooting"
            search_queries.append(fault_type_query)
        
        # General TEP fault analysis query
        search_queries.append("Tennessee Eastman process fault diagnosis troubleshooting")
        
        # Search knowledge base
        all_knowledge = []
        for query in search_queries:
            knowledge_chunks = self.search_knowledge(query, n_results=3)
            all_knowledge.extend(knowledge_chunks)
        
        # Remove duplicates and sort by similarity
        unique_knowledge = {}
        for chunk in all_knowledge:
            key = f"{chunk['source']}_{chunk['page']}"
            if key not in unique_knowledge or chunk['similarity'] > unique_knowledge[key]['similarity']:
                unique_knowledge[key] = chunk
        
        sorted_knowledge = sorted(unique_knowledge.values(), 
                                key=lambda x: x['similarity'], reverse=True)[:5]
        
        # Build enhanced prompt
        if sorted_knowledge:
            knowledge_section = "\n\n## RELEVANT KNOWLEDGE BASE INFORMATION:\n"
            knowledge_section += "The following information from technical documentation may be relevant to this fault analysis:\n\n"
            
            for i, chunk in enumerate(sorted_knowledge, 1):
                knowledge_section += f"**Source {i}:** {chunk['source']} (Page {chunk['page']}, Similarity: {chunk['similarity']})\n"
                knowledge_section += f"{chunk['text']}\n\n"
            
            knowledge_section += "## ANALYSIS INSTRUCTIONS:\n"
            knowledge_section += "- Consider the above knowledge base information in your analysis\n"
            knowledge_section += "- If relevant information is found, cite the source in your response\n"
            knowledge_section += "- If no relevant information is available in the knowledge base, explicitly state this limitation\n"
            knowledge_section += "- Maintain focus on the statistical fault analysis while incorporating relevant knowledge\n\n"
            
            enhanced_prompt = original_prompt + knowledge_section
        else:
            # No relevant knowledge found
            no_knowledge_section = "\n\n## KNOWLEDGE BASE STATUS:\n"
            no_knowledge_section += "No relevant information was found in the technical knowledge base for this specific fault pattern. "
            no_knowledge_section += "Analysis will be based on TEP process knowledge and statistical fault data only.\n\n"
            
            enhanced_prompt = original_prompt + no_knowledge_section
        
        return enhanced_prompt
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get RAG system status and statistics"""
        return {
            'knowledge_folder': str(self.knowledge_folder),
            'database_path': str(self.db_path),
            'total_documents': self.collection.count(),
            'processed_files': len(self.processed_docs),
            'encoder_model': self.encoder.get_sentence_embedding_dimension(),
            'last_updated': datetime.now().isoformat()
        }
