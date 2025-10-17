from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from document_service import DocumentService
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class UrlRequest(BaseModel):
    document_id: str
    url: str
    tenant_id: str

class DocumentRequest(BaseModel):
    document_id: str
    data_list: list
    tenant_id: str

class WebsiteRequest(BaseModel):
    url: str
    tenant_id: str

class QuestionRequest(BaseModel):
    tenant_id: str
    question: str

class MemoryRequest(BaseModel):
    tenant_id: str


@app.post('/load_document')
async def load_document(request: DocumentRequest):
    document_id = request.document_id
    data_list = request.data_list
    tenant_id = request.tenant_id

    if not document_id or not data_list or not tenant_id:
        raise HTTPException(status_code=400, detail="document_id, tenant_id and data_list are required")

    DocumentService.load_document(document_id, data_list, tenant_id)
    return {"message": "document loaded successfully"}


@app.post('/load_url')
async def load_url(request: UrlRequest):
    document_id = request.document_id
    url = request.url
    tenant_id = request.tenant_id

    if not document_id or not url or not tenant_id:
        raise HTTPException(status_code=400, detail="document_id, tenant_id and url are required")

    DocumentService.load_url(document_id, url, tenant_id)
    return {"message": "url loaded successfully"}

@app.post('/load_website')
async def load_website(request: WebsiteRequest):
    url = request.url
    tenant_id = request.tenant_id

    if not url or not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id and url are required")

    DocumentService.load_website(url, tenant_id)
    return {"message": "Website loaded successfully"}


@app.post('/ask_question')
async def ask_question(request: QuestionRequest):
    question = request.question
    tenant_id = request.tenant_id   

    if not question or not tenant_id:
        raise HTTPException(status_code=400, detail="question and tenant_id is required")

    answer = DocumentService.get_answer(question, tenant_id)
    return answer

@app.post('/ask_question_stream')
async def ask_question_stream(request: QuestionRequest):
    question = request.question
    tenant_id = request.tenant_id   

    if not question or not tenant_id:
        raise HTTPException(status_code=400, detail="question and tenant_id is required")

    def generate_response():
        try:
            for chunk in DocumentService.get_answer_stream(question, tenant_id):
                if chunk['is_last']:
                    # Last chunk - send complete response data
                    complete_response = chunk['complete_response']
                    serialized_response = {
                        'query': question,
                        'result': complete_response['result'],
                        'source_documents': [
                            {'metadata': document.metadata}
                            for document in complete_response['source_documents']
                        ]
                    }
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk['token'], 'complete': True, 'answer': serialized_response})}\n\n"
                else:
                    # Send individual token
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk['token'], 'complete': False})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post('/clear_memory')
async def clear_memory(request: MemoryRequest):
    tenant_id = request.tenant_id
    DocumentService.clear_memory(tenant_id)
    return {"message": "Memory cleared successfully"}


@app.get('/history/{tenant_id}')
async def get_history(tenant_id: str):
    if tenant_id not in DocumentService.memories:
        raise HTTPException(status_code=404, detail="Tenant ID not found")
    return DocumentService.memories[tenant_id].chat_memory.messages

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

