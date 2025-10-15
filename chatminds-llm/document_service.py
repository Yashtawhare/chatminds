import os
import requests
from urllib.parse import urlparse
import bs4
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from openai import OpenAI
from threading import Timer
from dotenv import load_dotenv
import chromadb
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import uuid

# Load environment variables from .env file
load_dotenv()

persist_directory = './data'
key = os.environ["OPENAI_API_KEY"]
embeddings = OpenAIEmbeddings()

class DocumentService:  
    memories = {} 
    clear_memory_timers = {}  # Tenant-wise clear_memory_timer

    @staticmethod
    def clear_memory(tenant_id):
        if tenant_id in DocumentService.memories:
            DocumentService.memories[tenant_id] = ConversationBufferMemory()
        if tenant_id in DocumentService.clear_memory_timers:
            DocumentService.clear_memory_timers[tenant_id] = None

    @staticmethod
    def load_url(document_id, url, tenant_id):
        document = []
        download_directory = "./docs"
        tenant_directory = os.path.join(persist_directory, tenant_id)
        if not os.path.exists(tenant_directory):
            os.makedirs(tenant_directory)
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        # find content-type of the url
        response = requests.head(url)
        content_type = response.headers.get('content-type')

        # if content-type is text/html, extract the text from the html
        if 'text/html' in content_type:
            response = requests.get(url)
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            # fine tune the text
            text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
            document_name = document_id + '.txt'
            file_path = os.path.join(download_directory, document_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            loader = TextLoader(os.path.join(download_directory, document_name))
            document.extend(loader.load())

        elif 'application/pdf' in content_type:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                parsed_url = urlparse(url)
                file_name = os.path.basename(parsed_url.path)
                if not file_name:
                    file_name = 'document.pdf'
                file_path = os.path.join(download_directory, file_name)
                with open(file_path, 'wb') as downloaded_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        downloaded_file.write(chunk)
            loader = PyPDFLoader(file_path)
            document.extend(loader.load())

        elif 'application/msword' in content_type or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                parsed_url = urlparse(url)
                file_name = os.path.basename(parsed_url.path)
                if not file_name:
                    file_name = 'document.docx'
                file_path = os.path.join(download_directory, file_name)
                with open(file_path, 'wb') as downloaded_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        downloaded_file.write(chunk)
            loader = Docx2txtLoader(file_path)
            document.extend(loader.load())

        # Split the document into chunks
        document_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        document_chunks = document_splitter.split_documents(document)

        # Assign metadata to the chunks
        for i, chunk in enumerate(document_chunks):
            chunk.metadata['document_id'] = document_id
            chunk.metadata['chunk_id'] = i
            chunk.metadata['tenant_id'] = tenant_id

        vectordb = Chroma.from_documents(document_chunks, embedding=embeddings,
                                                        persist_directory=tenant_directory)
        vectordb.persist()


    @staticmethod
    def load_website(base_url, tenant_id):
        if tenant_id in DocumentService.memories:
            DocumentService.memories[tenant_id] = ConversationBufferMemory()
        if tenant_id in DocumentService.clear_memory_timers:
            DocumentService.clear_memory_timers[tenant_id] = None

        # Make a request to the base URL
        response = requests.get(base_url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the 'a' tags (links) in the HTML
        links = soup.find_all('a')

        # Extract the 'href' attribute from each link, make it absolute, and add it to a list if it's not a social media URL or mailto link
        urls = []
        for link in links:
            url = link.get('href')
            if url:
                absolute_url = urljoin(base_url, url)
                if not any(social_url in absolute_url for social_url in ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com']) and not absolute_url.startswith('mailto:'):
                    urls.append(absolute_url)
        
        # remove duplicates
        urls = list(set(urls))

        for url in urls:
            document_id = str(uuid.uuid4())
            DocumentService.load_url(document_id, url, tenant_id)

    @staticmethod
    def load_document(document_id, data_list, tenant_id):
        document = []
        # Get the current directory
        current_directory = os.path.dirname(__file__)
        # Navigate up one directory level
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        # Update this path to correctly point to the frontend data directory
        download_directory = os.path.join(parent_directory, "chatminds-ui","data", tenant_id, "docs", "raw")
        tenant_directory = os.path.join(persist_directory, tenant_id)

        if not os.path.exists(tenant_directory):
            os.makedirs(tenant_directory)

        for data in data_list:
            file_name = data['name']
            file_type = data['type']
            file_size = data['size']
            file_path = os.path.join(download_directory, document_id + '.' + file_name.split(".")[-1]) 

            if not os.path.exists(file_path):
                # handle file not found exception
                raise FileNotFoundError(f"File {file_name} not found")
            
            if 'text/plain' in file_type:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                loader = TextLoader(file_path)
                document.extend(loader.load())

            elif 'application/pdf' in file_type:
                loader = PyPDFLoader(file_path)
                document.extend(loader.load())

            elif 'application/msword' in file_type or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in file_type:
                loader = Docx2txtLoader(file_path)
                document.extend(loader.load())

        # Split the document into chunks
        document_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        document_chunks = document_splitter.split_documents(document)

        # Assign metadata to the chunks
        for i, chunk in enumerate(document_chunks):
            chunk.metadata['document_id'] = document_id
            chunk.metadata['chunk_id'] = i
            chunk.metadata['tenant_id'] = tenant_id

        vectordb = Chroma.from_documents(document_chunks, embedding=embeddings, persist_directory=tenant_directory)
        vectordb.persist()



    @staticmethod
    def get_answer(question, tenant_id):
        if tenant_id not in DocumentService.memories:
            DocumentService.memories[tenant_id] = ConversationBufferMemory()
        DocumentService.memories[tenant_id].chat_memory.add_user_message(question)
        tenant_directory = os.path.join(persist_directory, tenant_id)

        vectordb = Chroma(persist_directory=tenant_directory, embedding_function=embeddings)

        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')

        pdf_qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
        # history = str(DocumentService.memories[tenant_id].chat_memory.messages)
        # client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        # refined_question = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "Refine New Question for me. Give only question. Focus previous question first if not clear then focus on earlier questions.Do not hallucinate."},
        #         {"role": "user", "content": history}
        #     ]
        # )
        llm_response = pdf_qa.invoke(question)

        serialized_response = {
            'query': question,
            'result': llm_response['result'],
            'source_documents': [
                {
                    'metadata': document.metadata
                }
                for document in llm_response['source_documents']
            ]
        }

        DocumentService.memories[tenant_id].chat_memory.add_ai_message(serialized_response['result'])

        print(DocumentService.memories[tenant_id].chat_memory.messages)

        # Schedule memory clearing after 5 minutes
        if tenant_id not in DocumentService.clear_memory_timers or DocumentService.clear_memory_timers[tenant_id] is None:
            DocumentService.clear_memory_timers[tenant_id] = Timer(300.0, DocumentService.clear_memory, args=[tenant_id])  # ToDo: Change to 12 hours
            DocumentService.clear_memory_timers[tenant_id].start()

        return serialized_response
