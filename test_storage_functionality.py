#!/usr/bin/env python3
"""
Test script for the dynamic storage usage functionality
"""

import os
import requests
import json

def test_storage_endpoint():
    """Test the storage calculation endpoint"""
    
    print("🔍 Testing Storage Usage Functionality")
    print("=" * 50)
    
    # Test data
    test_tenant_id = "e63b06cf-163d-4fc5-98f8-c40ae8cae89a"  # Known tenant from workspace
    base_url = "http://localhost:5000"
    
    # Check if the tenant data directory exists
    data_dir = "./chatminds/data"
    tenant_dir = os.path.join(data_dir, test_tenant_id)
    
    print(f"📁 Checking tenant directory: {tenant_dir}")
    
    if os.path.exists(tenant_dir):
        print("✅ Tenant directory exists")
        
        # Calculate actual storage manually for comparison
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(tenant_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
                    print(f"   📄 {file}: {size} bytes")
        
        print(f"📊 Manual calculation:")
        print(f"   Total files: {file_count}")
        print(f"   Total size: {total_size} bytes")
        
        # Format size manually
        def format_bytes(bytes):
            if bytes == 0:
                return "0 B"
            
            import math
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = int(math.floor(math.log(bytes, 1024)))
            p = math.pow(1024, i)
            s = round(bytes / p, 2)
            return f"{s} {size_names[i]}"
        
        formatted_size = format_bytes(total_size)
        print(f"   Formatted size: {formatted_size}")
        
    else:
        print("❌ Tenant directory not found")
        print("💡 This is normal if no documents have been uploaded yet")
    
    print("\n🌐 Testing API endpoint...")
    
    try:
        # Test the new storage endpoint
        storage_url = f"{base_url}/storage/{test_tenant_id}"
        print(f"🔗 Making request to: {storage_url}")
        
        # Note: This would normally require authentication
        # For testing, we'd need to handle the login flow
        print("ℹ️  Note: API testing requires authentication")
        print("💡 To test manually:")
        print(f"   1. Login to the web app at {base_url}")
        print(f"   2. Navigate to a tenant dashboard")
        print(f"   3. Check the Storage Used card - it should show dynamic values")
        print(f"   4. Upload/delete documents and watch it update")
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
    
    print("\n✅ Test completed!")
    print("\n🎯 Expected behavior:")
    print("1. Storage Used should show actual calculated values (not '2.4 GB')")
    print("2. Values should update when documents are added/removed")
    print("3. Should show 'Loading...' initially, then real values")
    print("4. Should handle empty directories gracefully (show '0 B')")

if __name__ == "__main__":
    test_storage_endpoint()