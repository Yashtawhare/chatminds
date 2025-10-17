# Document Clean Folder Functionality

## Overview

The ChatMinds system now includes enhanced document processing with a **clean folder** feature that creates processed and cleaned versions of uploaded documents alongside the original raw files.

## Directory Structure

```
data/
└── {tenant_id}/
    └── docs/
        ├── raw/           # Original uploaded files
        │   ├── document1.pdf
        │   ├── document2.txt
        │   └── document3.docx
        └── clean/         # Cleaned and processed versions
            ├── document1_cleaned.txt
            ├── document2_cleaned.txt
            └── document3_cleaned.txt
```

## Features

### 🧹 Document Cleaning Process

The document processor applies the following cleaning steps:

1. **Text Extraction**: Extracts raw text from various file formats (PDF, DOC, DOCX, TXT)
2. **Whitespace Normalization**: 
   - Converts multiple spaces to single spaces
   - Standardizes line breaks
   - Removes carriage returns and excessive tabs
3. **Content Cleaning**:
   - Removes page headers and footers
   - Standardizes bullet points and list markers
   - Cleans up excessive punctuation
   - Optionally removes URLs and email addresses
4. **Structure Preservation**: Maintains important document structure while removing noise

### 📊 Document Statistics

The system tracks and displays statistics for each processed document:
- Character count
- Word count
- Line count
- Paragraph count

### 🔍 Dual Document Viewing

Users can now view both versions of each document:
- **Raw Document** (📄 blue eye icon): View the original uploaded file
- **Cleaned Document** (📝 green text icon): View the processed and cleaned version

## How to Use

### 1. Upload Documents

When you upload documents through the web interface:
1. Files are saved to the `raw` folder
2. Documents are automatically processed and cleaned
3. Cleaned versions are saved to the `clean` folder

### 2. View Documents

In the tenant dashboard:
- **📄 Blue Eye Icon**: View original document
- **📝 Green Text Icon**: View cleaned document version
- **🗑️ Red Trash Icon**: Delete document (removes both versions)

### 3. Document Processing

The system automatically:
1. Processes uploaded documents in the background
2. Creates cleaned versions for better AI processing
3. Uses cleaned versions for text chunking and vector embeddings
4. Maintains both versions for user access

## Benefits

### For Users
- **Better Document Quality**: Cleaned documents provide cleaner, more readable content
- **Dual Access**: Can view both original and processed versions
- **Enhanced Search**: Cleaned content improves AI search and response quality

### For AI Processing
- **Improved Embeddings**: Cleaner text creates better vector representations
- **Better Chunking**: Normalized content splits more effectively
- **Enhanced Accuracy**: Removed noise leads to more accurate AI responses

## Technical Implementation

### Backend Components

1. **DocumentProcessor** (`document_processor.py`):
   - Handles text extraction and cleaning
   - Provides document statistics
   - Creates standardized cleaned content

2. **DocumentService** (`document_service.py`):
   - Updated to use DocumentProcessor
   - Creates both raw and clean directory structures
   - Processes documents through cleaning pipeline

3. **Flask App** (`app.py`):
   - Creates clean directories during upload
   - Provides endpoints for viewing both document types
   - New route: `/view_cleaned_document/<document_id>/tenant/<tenant_id>`

### Frontend Components

4. **Tenant Dashboard** (`tenant_data.html`):
   - Updated action buttons for dual document viewing
   - Visual indicators for document types
   - Enhanced user experience with tooltips

## Setup and Configuration

### For Existing Installations

1. **Process Existing Documents**:
   ```bash
   cd /path/to/chatminds
   python process_documents.py
   ```

2. **Update Docker Environment**:
   The system automatically detects Docker vs local environments and adjusts paths accordingly.

### For New Installations

The clean folder functionality is automatically enabled for all new document uploads.

## File Naming Convention

- **Raw files**: `{document_id}.{original_extension}`
- **Clean files**: `{document_id}_cleaned.txt`

This ensures easy pairing of raw and cleaned versions while maintaining unique identifiers.

## Environment Compatibility

The system works in both:
- **Docker Environment**: Uses `/app/shared_data` mount point
- **Local Development**: Uses relative `./data` directory

Path detection is automatic based on environment detection.

## Future Enhancements

Planned improvements include:
- Enhanced PDF text extraction with better formatting preservation
- Support for additional file formats (images with OCR, presentations)
- Configurable cleaning rules per tenant
- Document preprocessing analytics and quality metrics
- Batch processing for large document sets

## Troubleshooting

### Common Issues

1. **Clean folder not created**: 
   - Ensure proper permissions on data directory
   - Check if document processing service is running

2. **Cleaned documents not appearing**:
   - Verify DocumentProcessor is properly imported
   - Check for processing errors in logs

3. **View cleaned document returns 404**:
   - Ensure cleaned file exists in clean folder
   - Check file naming convention

### Debug Information

Enable debug mode to see detailed processing information:
- Document processing statistics
- File path resolution
- Error details for failed processing

## API Endpoints

### New Endpoints

- `GET /view_cleaned_document/<document_id>/tenant/<tenant_id>`: View cleaned document
  
### Updated Endpoints

- `POST /add_document/<tenant_id>`: Now creates both raw and clean directories
- Document processing APIs now include cleaning pipeline

---

*This feature enhances the ChatMinds AI document processing pipeline by providing cleaner, more structured content for improved AI interactions while maintaining access to original documents.*