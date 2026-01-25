## Resume RAG Chatbot (Recruiter-Friendly)

This project is a **RAG (Retrieval-Augmented Generation) chatbot** that allows recruiters to ask questions and get answers directly from my **resume PDF**.

### What it does
- Loads resume documents (PDF/text)
- Converts text into embeddings
- Stores embeddings in a vector database (**ChromaDB**)
- Retrieves the most relevant chunks for each question
- Uses an LLM (**OpenAI GPT**) to generate grounded answers based on retrieved resume context

### Why this is useful
Unlike a normal chatbot that may hallucinate, this bot answers using **only resume-based context**, making responses accurate, relevant, and recruiter-friendly.

### Example questions
- "What AI projects have you built?"
- "What is your experience with FastAPI and React?"
- "Tell me about your latest role responsibilities."
- "What cloud tools have you worked with?"

### Tech Stack :

**Backend**
- Python
- FastAPI (REST API)
- Uvicorn (ASGI server)

**LLM + RAG**
- OpenAI (GPT models)
- LangChain (RAG orchestration)
- Embeddings (OpenAI Embeddings)

**Vector Database**
- ChromaDB (local vector store + similarity search)

**Tools**
- VS Code
- Git / GitHub CLI

