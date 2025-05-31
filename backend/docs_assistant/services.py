# docs_assistant/services.py
import requests
import ollama
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from django.conf import settings
import PyPDF2
import docx
import markdown
import html2text
from typing import List, Dict, Tuple
import re
import os

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        self.collection = self.chroma_client.get_or_create_collection("documentation")
        
    def process_url(self, url: str) -> str:
        """Extract text content from a URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Try to find main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            raise Exception(f"Error processing URL: {str(e)}")
    
    def process_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._process_docx(file_path)
            elif file_extension == '.md':
                return self._process_markdown(file_path)
            elif file_extension in ['.txt', '.py', '.js', '.html', '.css', '.json']:
                return self._process_text_file(file_path)
            else:
                raise Exception(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    def _process_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _process_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def _process_markdown(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        html = markdown.markdown(md_content)
        return html2text.html2text(html)
    
    def _process_text_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at sentence boundary
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            
            break_point = max(last_period, last_newline)
            if break_point > start + chunk_size // 2:
                end = start + break_point + 1
            
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    def store_chunks(self, document_id: str, chunks: List[str], metadata: Dict = None):
        """Store document chunks in vector database"""
        if not chunks:
            return
            
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": i, **(metadata or {})} 
                    for i in range(len(chunks))]
        
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        self.collection = self.chroma_client.get_or_create_collection("documentation")
        self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve most relevant document chunks for a query"""
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        relevant_chunks = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                relevant_chunks.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0
                })
        
        return relevant_chunks
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> Tuple[str, List[str]]:
        """Generate response using Ollama with retrieved context"""
        
        # Prepare context from retrieved chunks
        context = "\n\n".join([
            f"Source {i+1}: {chunk['content']}" 
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Create prompt
        prompt = f"""You are a helpful code documentation assistant. Use the following documentation context to answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {query}

Answer: Provide a detailed and helpful answer based on the documentation context above. Include code examples when relevant."""

        try:
            # Generate response using Ollama
            response = self.ollama_client.generate(
                model=settings.OLLAMA_MODEL,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 1000
                }
            )
            
            answer = response['response']
            sources = [chunk['metadata'].get('document_id', 'unknown') for chunk in context_chunks]
            
            return answer, sources
            
        except Exception as e:
            return f"Error generating response: {str(e)}", []
    
    def chat(self, query: str) -> Dict:
        """Main chat function that combines retrieval and generation"""
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(query)
        
        # Generate response
        answer, sources = self.generate_response(query, relevant_chunks)
        
        return {
            'answer': answer,
            'sources': sources,
            'relevant_chunks': relevant_chunks
        }