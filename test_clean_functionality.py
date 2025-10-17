#!/usr/bin/env python3
"""
Simple test script to check if the clean folder functionality is working
"""
import os
import sys
import shutil

def test_clean_folder_creation():
    """Test if we can create the clean folder structure"""
    
    print("🔍 Testing Clean Folder Functionality")
    print("=" * 50)
    
    # Test data
    test_tenant_id = "e63b06cf-163d-4fc5-98f8-c40ae8cae89a"
    base_data_dir = "./data" if not os.path.exists("/app/shared_data") else "/app/shared_data"
    
    # Create directory paths
    tenant_dir = os.path.join(base_data_dir, test_tenant_id)
    docs_dir = os.path.join(tenant_dir, "docs")
    raw_dir = os.path.join(docs_dir, "raw")
    clean_dir = os.path.join(docs_dir, "clean")
    
    print(f"📁 Base directory: {base_data_dir}")
    print(f"🏢 Tenant directory: {tenant_dir}")
    print(f"📄 Raw directory: {raw_dir}")
    print(f"✨ Clean directory: {clean_dir}")
    print()
    
    # Check if directories exist
    print("📋 Directory Status:")
    print(f"   Tenant dir exists: {os.path.exists(tenant_dir)}")
    print(f"   Docs dir exists: {os.path.exists(docs_dir)}")
    print(f"   Raw dir exists: {os.path.exists(raw_dir)}")
    print(f"   Clean dir exists: {os.path.exists(clean_dir)}")
    print()
    
    # Create clean directory if it doesn't exist
    if not os.path.exists(clean_dir):
        print("🔧 Creating clean directory...")
        os.makedirs(clean_dir, exist_ok=True)
        print(f"✅ Created: {clean_dir}")
    else:
        print("✅ Clean directory already exists")
    
    # List files in each directory
    if os.path.exists(raw_dir):
        raw_files = os.listdir(raw_dir)
        print(f"📁 Raw files ({len(raw_files)}):")
        for file in raw_files:
            print(f"   📄 {file}")
    else:
        print("📁 Raw directory not found")
    
    if os.path.exists(clean_dir):
        clean_files = os.listdir(clean_dir)
        print(f"✨ Clean files ({len(clean_files)}):")
        for file in clean_files:
            print(f"   📄 {file}")
    else:
        print("✨ Clean directory not found")
    
    print()
    
    # Test creating a sample cleaned file
    sample_content = """# Sample Cleaned Document

This is a test of the document cleaning functionality.

Key features:
• Removes excessive whitespace
• Normalizes line breaks
• Cleans up formatting issues
• Preserves important content structure

Document statistics:
- Character count: 220
- Word count: 36
- Line count: 12
- Paragraph count: 3
"""
    
    sample_file_path = os.path.join(clean_dir, "test_document_cleaned.txt")
    print(f"📝 Creating sample cleaned file: {sample_file_path}")
    
    try:
        with open(sample_file_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print("✅ Sample file created successfully")
        
        # Verify file was created
        if os.path.exists(sample_file_path):
            file_size = os.path.getsize(sample_file_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Read back and show first few lines
            with open(sample_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"📖 Content preview (first 3 lines):")
                for i, line in enumerate(lines[:3]):
                    print(f"   {i+1}: {line}")
        
    except Exception as e:
        print(f"❌ Error creating sample file: {e}")
    
    print()
    print("🎉 Clean folder functionality test completed!")
    return True

if __name__ == "__main__":
    test_clean_folder_creation()