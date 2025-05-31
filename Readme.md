# 📘 DocuMind

**DocuMind** is an intelligent web application that helps developers generate and understand documentation for their codebases using AI. It features a **React frontend** and a **Django backend**, and leverages **LLM-powered agents** and **RAG (Retrieval-Augmented Generation)** techniques to answer natural language questions about uploaded source code and technical documents.

---

## 🔧 Tech Stack

- **Frontend:** React, TailwindCSS, Axios, React Router
- **Backend:** Django, Django REST Framework, LangChain, Chroma (vector DB), AutoGen (agent orchestration)
- **LLM Provider:** [Ollama](https://ollama.com/) running [Meta’s LLaMA 2](https://ai.meta.com/llama/)
- **Embeddings & Retrieval:** LangChain + Chroma DB
- **Authentication:** DRF Token Authentication

---

## 🚀 Features

- 📂 Upload source code or documentation files
- 💬 Ask natural language questions about your code
- 🔍 Retrieve contextually relevant document chunks using vector search
- 🤖 Use agent-based reasoning for enhanced responses (via LangChain or AutoGen)
- 🌐 Clean, interactive frontend interface with live Q&A experience
- ✅ Works fully offline with local LLM models

---

## 🏁 Getting Started

### ✅ Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama installed and running
- `pip`, `virtualenv`, `npm`

---

### 🔨 Backend Setup (Django)

1. Clone the repo:

   ```bash
   # backend 
   git clone https://github.com/yourusername/documind.git
   cd documind/backend
   ```
2. Create VENV and install dependencies
   
   ```bash
   # create venv optionally 
   python3 -m venv [name_of_venv]
   ./[name_of_venv]/Scripts/activate
   pip install -r requirements.txt
   ```
3. Run server 
   ```shell
   python manage.py runserver (to run server locally )
   ```

### 🔨 Frontend Setup (React.JS)

   ```bash 
   # frontend
   cd documind/frontend 
   npm install 
   npm run start
   ``` 

