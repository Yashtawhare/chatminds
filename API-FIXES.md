# API Structure and Fixes Summary

## ✅ **Fixed API Call Issues**

### **Original Problems:**
1. ❌ Hardcoded `localhost:8000` URLs in UI
2. ❌ Missing `/api/` prefix for backend calls
3. ❌ Incorrect response handling in chatbot widget
4. ❌ Inconsistent API endpoints

### **Fixed Issues:**

#### **1. Load Documents Page (`ui/templates/load_documents.html`)**
- ✅ Changed `http://localhost:8000/load_document` → `/api/load_document`
- ✅ Changed `http://localhost:8000/load_url` → `/api/load_url`  
- ✅ Changed `http://localhost:8000/load_website` → `/api/load_website`

#### **2. Chatbot Widget (`widget/ask-ai-chatbot.html`)**
- ✅ Changed from GET with query params to POST with JSON body
- ✅ Updated API endpoint to `/api/ask_question`
- ✅ Fixed response handling to use `data.result` field
- ✅ Removed streaming response handling (backend returns JSON)

#### **3. Main UI Chat Interface (`ui/templates/tenant_data.html`)**
- ✅ Added proper chat interface with AI question-answering
- ✅ Uses `/api/ask_question` endpoint correctly
- ✅ Handles responses properly with error handling

#### **4. Widget Initialization (`widget/chatbot-init.js`)**
- ✅ Changed from `http://localhost:8080/` to `/widget/` for relative paths

---

## 🌐 **Correct API Structure**

### **Frontend (Flask UI) Routes:**
```
http://your-domain/                    → Main app
http://your-domain/login               → Login page
http://your-domain/register            → Registration
http://your-domain/tenant_data/{id}    → Tenant dashboard
http://your-domain/load_documents/{id} → Document upload
http://your-domain/documents/{id}      → Get documents (internal)
http://your-domain/add_document/{id}   → Upload files (internal)
```

### **Backend (FastAPI) Routes via `/api/` prefix:**
```
http://your-domain/api/load_document   → Load document for processing
http://your-domain/api/load_url        → Load URL for processing  
http://your-domain/api/load_website    → Load website for processing
http://your-domain/api/ask_question    → Ask AI questions
http://your-domain/api/clear_memory    → Clear conversation memory
http://your-domain/api/history/{id}    → Get chat history
http://your-domain/api/docs            → API documentation
```

### **Widget Routes:**
```
http://your-domain/widget/             → Chatbot widget files
http://your-domain/widget/ask-ai-chatbot.html → Main widget
http://your-domain/widget/chatbot-init.js     → Widget initialization
```

---

## 📋 **API Request/Response Examples**

### **1. Ask Question**
**Request:**
```javascript
POST /api/ask_question
Content-Type: application/json

{
  "tenant_id": "your-tenant-id",
  "question": "What is this document about?"
}
```

**Response:**
```json
{
  "query": "What is this document about?",
  "result": "This document is about...",
  "source_documents": [
    {
      "metadata": {...}
    }
  ]
}
```

### **2. Load Document**
**Request:**
```javascript
POST /api/load_document
Content-Type: application/json

{
  "document_id": "doc-uuid",
  "tenant_id": "tenant-uuid", 
  "data_list": [
    {
      "name": "file.pdf",
      "type": "application/pdf",
      "size": 1024
    }
  ]
}
```

**Response:**
```json
{
  "message": "document loaded successfully"
}
```

### **3. Load URL**
**Request:**
```javascript
POST /api/load_url
Content-Type: application/json

{
  "document_id": "doc-uuid",
  "tenant_id": "tenant-uuid",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "message": "url loaded successfully"
}
```

---

## 🔧 **Nginx Configuration**

The nginx configuration correctly routes:
- Frontend requests directly to Flask (port 5000)
- `/api/*` requests to FastAPI backend (port 8000) 
- `/widget/*` requests to static widget files

**Key nginx routing:**
```nginx
# API endpoints - proxy to backend (removes /api prefix)
location /api/ {
    rewrite ^/api/(.*)$ /$1 break;
    proxy_pass http://backend;
}

# Widget files - serve static files
location /widget/ {
    alias /usr/share/nginx/html/widget/;
}

# Main app - proxy to frontend
location / {
    proxy_pass http://frontend;
}
```

---

## ✅ **All API Calls Now Work Correctly**

1. **Document Upload Flow:**
   - UI uploads files to Flask → Flask saves files → Flask calls `/api/load_document` → Backend processes

2. **URL/Website Loading:**
   - UI sends URL to `/api/load_url` or `/api/load_website` → Backend processes directly

3. **Chat/Questions:**
   - UI/Widget sends questions to `/api/ask_question` → Backend returns AI response

4. **Production Deployment:**
   - All hardcoded localhost URLs removed
   - Uses relative paths that work in production
   - Proper nginx routing configured

The API structure is now consistent and production-ready! 🎉