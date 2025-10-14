# Document QA Chatbot - CHATMINDS

Welcome to the Document QA Chatbot, a revolutionary AI-driven solution that transforms the way you interact with your documents. Seamlessly integrate, query, and manage your documents with our intuitive chat interface, powered by state-of-the-art language models.

## Key Features

### Effortless Document Integration
- **Multiple Formats Supported**: Easily upload documents in HTML, PDF, or DOCX formats directly from URLs.
- **Automatic Content Extraction**: Our service intelligently extracts and processes text from various document formats, ensuring accurate and comprehensive data capture.

### Advanced Query Capabilities
- **AI-Powered Answers**: Leverage OpenAI's GPT-3.5-turbo to get precise and context-aware answers to your questions about the document content.
- **Contextual Memory**: Our chatbot retains the context of your conversation, providing coherent and relevant responses even as your queries evolve.

### Robust Memory Management
- **Tenant-Specific Memory**: Each user's interactions are isolated, ensuring personalized and secure experiences.
- **Auto-Clear Mechanism**: Memory is automatically cleared after a set period, maintaining optimal performance and data privacy.

## Get Started

### Prerequisites

- Python 3.7 or higher
- An OpenAI API key
- Necessary Python libraries (FastAPI, Streamlit, LangChain, OpenAI, Requests, BeautifulSoup4, Uvicorn)

### Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/yourusername/document-qa-chatbot.git
    cd document-qa-chatbot
    ```

2. **Create and Activate a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:

    Create a `.env` file in the project root and add your OpenAI API key:

    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    ```

### Running the Application

1. **Start the FastAPI Server**:

    ```bash
    uvicorn main:app --reload
    ```

2. **Launch the Streamlit Interface**:

    ```bash
    streamlit run app.py
    ```

3. **Access the Interface**:

    Open your browser and navigate to `http://localhost:8501`.

### Accessing FastAPI Swagger Documentation

FastAPI provides an interactive API documentation interface using Swagger UI. To access it:

1. Ensure the FastAPI server is running.
2. Open your browser and navigate to `http://localhost:8000/docs`.

This interactive documentation allows you to test the API endpoints and explore the capabilities of the backend services.

## Usage

### Load a Document

1. Enter the document ID, URL, and tenant ID in the Streamlit interface.
2. Click the "Load Document" button.
3. A balloon will appear to confirm successful loading.

### Ask a Question

1. Enter your question and tenant ID in the Streamlit interface.
2. Click the "Ask Question" button or press Enter.
3. The chatbot will stream the answer, providing an interactive experience similar to ChatGPT.

### Clear Memory

1. Enter the tenant ID in the Streamlit interface.
2. Click the "Clear Memory" button to reset the conversation context.

## Contribution

We welcome contributions to enhance the functionality and performance of the Document QA Chatbot. Please fork the repository and submit pull requests for review.

## License

This project is licensed under the MIT License.

## Contact

For inquiries or support, please contact [oshoupadhyayindia@gmail.com].

---

Empower your document interactions with the Document QA Chatbot. Say goodbye to manual searches and hello to intelligent, conversational document querying!
