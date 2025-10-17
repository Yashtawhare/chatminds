# Dynamic Storage Usage Implementation

## Problem
The ChatMinds application displayed a static "Storage Used: 2.4 GB" value in the tenant dashboard, regardless of actual storage consumption.

## Solution
Implemented a dynamic storage calculation system that:

1. **Calculates real-time storage usage** for each tenant
2. **Updates automatically** when documents are added/removed
3. **Formats values appropriately** (B, KB, MB, GB, TB)
4. **Handles edge cases** gracefully

## Changes Made

### 1. Backend Implementation (`app.py`)

#### New API Endpoint
```python
@app.route('/storage/<tenant_id>', methods=['GET'])
def get_storage_usage(tenant_id):
    """Calculate and return storage usage for a tenant"""
```

**Features:**
- Walks through the entire tenant directory structure
- Calculates total bytes and file count
- Formats size in human-readable format (B, KB, MB, GB, TB)
- Handles file access errors gracefully
- Returns JSON with total_bytes, formatted_size, and file_count

#### Implementation Details
- Uses `os.walk()` to traverse all subdirectories
- Handles both raw and clean document folders
- Error handling for inaccessible files
- Logarithmic size formatting algorithm

### 2. Frontend Implementation (`tenant_data.html`)

#### Template Changes
```html
<!-- Before (Static) -->
<p class="text-2xl font-bold text-gray-900">2.4 GB</p>

<!-- After (Dynamic) -->
<p class="text-2xl font-bold text-gray-900" x-text="storageUsed">Loading...</p>
```

#### JavaScript Enhancement
```javascript
// Added storage usage property
storageUsed: 'Loading...',

// Added storage fetching function
async fetchStorageUsage() {
    const response = await fetch('/storage/{{ tenant.tenant_id }}');
    const storageData = await response.json();
    this.storageUsed = storageData.formatted_size;
},

// Enhanced deletion to refresh storage
await this.fetchStorageUsage(); // After document deletion
```

### 3. Upload Integration (`load_documents.html`)

#### Auto-refresh on Return
- Modified redirect URLs to include `?refresh=true` parameter
- Added automatic refresh when returning from uploads
- Ensures storage usage updates immediately after new uploads

## Features

### 🔄 Real-time Updates
- Storage updates when documents are uploaded
- Storage updates when documents are deleted
- Automatic refresh when returning from upload page

### 📊 Accurate Calculations
- Includes all files in tenant directory (raw + clean)
- Handles nested directory structures
- Accounts for different file types and sizes

### 🎨 User Experience
- Shows "Loading..." initially
- Gracefully handles errors with "Error" fallback
- Maintains consistent UI design

### 🛡️ Error Handling
- Handles missing directories (shows "0 B")
- Skips inaccessible files without crashing
- Returns safe defaults on calculation errors

## Testing

Created `test_storage_functionality.py` to verify:
- Manual storage calculation matches API results
- File discovery works correctly
- Size formatting is accurate

**Test Results:**
- ✅ Found 4 files totaling 156,995 bytes (153.32 KB)
- ✅ Much more accurate than hardcoded "2.4 GB"
- ✅ Realistic values for actual document storage

## Benefits

1. **Accuracy**: Shows real storage consumption
2. **Transparency**: Users see actual space usage
3. **Real-time**: Updates immediately with changes
4. **Scalable**: Works with any number of documents
5. **Maintainable**: Clean separation of concerns

## Future Enhancements

Potential improvements:
- Cache storage calculations for performance
- Add storage quotas and limits
- Include storage analytics/history
- Add storage optimization suggestions
- Implement storage alerts/notifications

## Usage

The dynamic storage feature is now active. Users will see:
- Real storage values instead of static "2.4 GB"
- Immediate updates when uploading/deleting documents
- Proper size formatting (B, KB, MB, GB, TB)
- "Loading..." states during calculation