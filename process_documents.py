#!/usr/bin/env python3
"""
Simple document processor to demonstrate the clean folder functionality
without requiring all the LangChain dependencies
"""
import os
import re
import shutil
from typing import Dict, Any

def clean_text(text: str) -> str:
    """
    Clean and preprocess text content.
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

def get_document_stats(content: str) -> Dict[str, Any]:
    """
    Get basic statistics about the document content.
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

def process_existing_documents():
    """
    Process existing documents and create cleaned versions
    """
    print("🔍 Processing Existing Documents")
    print("=" * 40)
    
    # Find all tenants
    data_dir = "./chatminds/data"
    if not os.path.exists(data_dir):
        print("❌ Data directory not found")
        return
    
    for tenant_id in os.listdir(data_dir):
        tenant_path = os.path.join(data_dir, tenant_id)
        if not os.path.isdir(tenant_path):
            continue
            
        print(f"\n🏢 Processing tenant: {tenant_id}")
        
        docs_dir = os.path.join(tenant_path, "docs")
        raw_dir = os.path.join(docs_dir, "raw")
        clean_dir = os.path.join(docs_dir, "clean")
        
        # Create clean directory if it doesn't exist
        if not os.path.exists(clean_dir):
            os.makedirs(clean_dir, exist_ok=True)
            print(f"✅ Created clean directory: {clean_dir}")
        
        # Process files in raw directory
        if os.path.exists(raw_dir):
            raw_files = os.listdir(raw_dir)
            print(f"📁 Found {len(raw_files)} raw files")
            
            for file_name in raw_files:
                file_path = os.path.join(raw_dir, file_name)
                if os.path.isfile(file_path):
                    process_file(file_path, clean_dir, file_name)
        else:
            print("📁 No raw directory found")

def process_file(file_path: str, clean_dir: str, file_name: str):
    """
    Process a single file and create cleaned version
    """
    print(f"📄 Processing: {file_name}")
    
    # Extract document ID and extension
    base_name = os.path.splitext(file_name)[0]
    extension = os.path.splitext(file_name)[1].lower()
    
    # Create cleaned file path
    clean_file_name = f"{base_name}_cleaned.txt"
    clean_file_path = os.path.join(clean_dir, clean_file_name)
    
    try:
        # For this demo, we'll create a placeholder cleaned file
        # In a real implementation, you would extract text from PDF/DOC files
        if extension == '.pdf':
            content = create_pdf_placeholder_content(file_name)
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = clean_text(content)
        elif extension in ['.doc', '.docx']:
            content = create_doc_placeholder_content(file_name)
        else:
            content = f"Unsupported file type: {extension}"
        
        # Save cleaned content
        with open(clean_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Get and display stats
        stats = get_document_stats(content)
        print(f"   ✅ Created: {clean_file_name}")
        print(f"   📊 Stats: {stats['word_count']} words, {stats['character_count']} chars")
        
    except Exception as e:
        print(f"   ❌ Error processing {file_name}: {e}")

def create_pdf_placeholder_content(file_name: str) -> str:
    """
    Create placeholder content for PDF files (since we don't have PDF processing libraries)
    """
    return f"""# Cleaned Content from {file_name}

This is a placeholder for the cleaned content that would be extracted from the PDF file.

In a full implementation, this would contain:
• Extracted text from the PDF
• Cleaned formatting
• Removed headers/footers
• Normalized whitespace
• Structured content

## Document Processing Steps Applied:
1. Text extraction from PDF
2. Whitespace normalization
3. Header/footer removal
4. Bullet point standardization
5. URL and email cleaning (optional)

## Content Quality Improvements:
• Consistent line breaks
• Standardized bullet points
• Removed duplicate spaces
• Clean paragraph structure

This cleaned version would be used for:
- Better text chunking
- Improved vector embeddings
- Enhanced search relevance
- More accurate AI responses

File: {file_name}
Status: Processed and cleaned
Timestamp: {__import__('datetime').datetime.now().isoformat()}
"""

def create_doc_placeholder_content(file_name: str) -> str:
    """
    Create placeholder content for DOC/DOCX files
    """
    return f"""# Cleaned Content from {file_name}

This is a placeholder for the cleaned content that would be extracted from the Word document.

The document cleaning process would include:
• Text extraction from Word format
• Style and formatting removal
• Table content preservation
• List structure normalization

## Enhanced Processing Features:
- Smart paragraph detection
- Header hierarchy preservation
- Table data extraction
- Image caption processing

File: {file_name}
Status: Processed and cleaned
Timestamp: {__import__('datetime').datetime.now().isoformat()}
"""

if __name__ == "__main__":
    process_existing_documents()
    print("\n🎉 Document processing completed!")
    print("\nTo see the results:")
    print("1. Check the 'clean' folders in your tenant directories")
    print("2. Compare original files in 'raw' with cleaned versions in 'clean'")
    print("3. Use the web interface to view both raw and cleaned documents")