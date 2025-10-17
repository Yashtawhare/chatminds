import os
import re
import tempfile
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.schema import Document
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Document processor that cleans and preprocesses documents before vectorization.
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and preprocess text content.
        
        Args:
            text (str): Raw text content
            
        Returns:
            str: Cleaned text content
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize line breaks
        text = re.sub(r'\n+', '\n', text)  # Multiple newlines to single
        text = re.sub(r'\r+', '', text)    # Remove carriage returns
        text = re.sub(r'\t+', ' ', text)   # Tabs to single space
        text = re.sub(r' +', ' ', text)    # Multiple spaces to single
        
        # Remove page headers/footers patterns (common in PDFs)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
        
        # Remove extra punctuation patterns
        text = re.sub(r'\.{3,}', '...', text)  # Multiple dots to ellipsis
        text = re.sub(r'-{2,}', '--', text)    # Multiple dashes to double dash
        
        # Remove URLs (optional - you might want to keep them)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                     '', text)
        
        # Remove email addresses (optional)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Clean up bullet points and list markers
        text = re.sub(r'^[\s]*[•·▪▫‣⁃]\s*', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*[*-]\s*', '• ', text, flags=re.MULTILINE)
        
        # Remove excessive line breaks after cleaning
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_and_clean_content(file_path: str, file_type: str) -> str:
        """
        Extract and clean content from a file.
        
        Args:
            file_path (str): Path to the file
            file_type (str): MIME type of the file
            
        Returns:
            str: Cleaned text content
        """
        try:
            content = ""
            
            if 'text/plain' in file_type:
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
                content = "\n".join([doc.page_content for doc in documents])
                
            elif 'application/pdf' in file_type:
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                content = "\n".join([doc.page_content for doc in documents])
                
            elif 'application/msword' in file_type or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in file_type:
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                content = "\n".join([doc.page_content for doc in documents])
            
            # Clean the extracted content
            cleaned_content = DocumentProcessor.clean_text(content)
            
            logger.info(f"Successfully extracted and cleaned content from {file_path}")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise e
    
    @staticmethod
    def save_cleaned_content(content: str, clean_file_path: str) -> None:
        """
        Save cleaned content to a text file.
        
        Args:
            content (str): Cleaned text content
            clean_file_path (str): Path where to save the cleaned content
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(clean_file_path), exist_ok=True)
            
            # Save cleaned content as UTF-8 text file
            with open(clean_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved cleaned content to {clean_file_path}")
            
        except Exception as e:
            logger.error(f"Error saving cleaned content to {clean_file_path}: {str(e)}")
            raise e
    
    @staticmethod
    def create_documents_from_cleaned_content(content: str, document_id: str, tenant_id: str, 
                                            original_file_name: str = None) -> List[Document]:
        """
        Create LangChain Document objects from cleaned content.
        
        Args:
            content (str): Cleaned text content
            document_id (str): Unique document identifier
            tenant_id (str): Tenant identifier
            original_file_name (str): Original file name
            
        Returns:
            List[Document]: List of Document objects
        """
        try:
            # Create a single document with metadata
            metadata = {
                'document_id': document_id,
                'tenant_id': tenant_id,
                'source': 'cleaned_document',
                'original_file_name': original_file_name or 'unknown'
            }
            
            document = Document(
                page_content=content,
                metadata=metadata
            )
            
            logger.info(f"Created document object for {document_id}")
            return [document]
            
        except Exception as e:
            logger.error(f"Error creating documents from cleaned content: {str(e)}")
            raise e
    
    @staticmethod
    def process_document(raw_file_path: str, clean_file_path: str, file_type: str, 
                        document_id: str, tenant_id: str, original_file_name: str = None) -> List[Document]:
        """
        Full document processing pipeline: extract, clean, save, and create Document objects.
        
        Args:
            raw_file_path (str): Path to the raw file
            clean_file_path (str): Path where to save the cleaned content
            file_type (str): MIME type of the file
            document_id (str): Unique document identifier
            tenant_id (str): Tenant identifier
            original_file_name (str): Original file name
            
        Returns:
            List[Document]: List of processed Document objects
        """
        try:
            # Extract and clean content
            cleaned_content = DocumentProcessor.extract_and_clean_content(raw_file_path, file_type)
            
            # Save cleaned content
            DocumentProcessor.save_cleaned_content(cleaned_content, clean_file_path)
            
            # Create Document objects
            documents = DocumentProcessor.create_documents_from_cleaned_content(
                cleaned_content, document_id, tenant_id, original_file_name
            )
            
            logger.info(f"Successfully processed document {document_id}")
            return documents
            
        except Exception as e:
            logger.error(f"Error in document processing pipeline: {str(e)}")
            raise e
    
    @staticmethod
    def get_document_stats(content: str) -> Dict[str, Any]:
        """
        Get basic statistics about the document content.
        
        Args:
            content (str): Document content
            
        Returns:
            Dict[str, Any]: Document statistics
        """
        if not content:
            return {
                'character_count': 0,
                'word_count': 0,
                'line_count': 0,
                'paragraph_count': 0
            }
        
        return {
            'character_count': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()])
        }