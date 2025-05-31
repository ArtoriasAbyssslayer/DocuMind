from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DocumentSource, ChatSession, ChatMessage, DocumentChunk
from .services import DocumentProcessor, RAGService
from .serializers import DocumentSourceSerializer, ChatSessionSerializer, ChatMessageSerializer
import os

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upload_document(request):
    """Handle document upload (URL, file, or text)"""
    try:
        source_type = request.data.get('source_type')
        title = request.data.get('title', 'Untitled Document')
        
        document = DocumentSource.objects.create(
            title=title,
            source_type=source_type
        )
        
        processor = DocumentProcessor()
        
        if source_type == 'url':
            url = request.data.get('url')
            if not url:
                return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            document.url = url
            document.save()
            
            # Process URL
            try:
                text_content = processor.process_url(url)
                document.text_content = text_content
                chunks = processor.chunk_text(text_content)
                
                # Store chunks in database
                for i, chunk_content in enumerate(chunks):
                    DocumentChunk.objects.create(
                        document=document,
                        content=chunk_content,
                        chunk_index=i,
                        metadata={'source_url': url}
                    )
                
                # Store in vector database
                processor.store_chunks(
                    str(document.id), 
                    chunks, 
                    {'title': title, 'source_type': 'url', 'url': url}
                )
                
                document.processed = True
                document.processing_status = 'completed'
                
            except Exception as e:
                document.processing_status = 'failed'
                document.error_message = str(e)
                
        elif source_type == 'file':
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            document.file = file
            document.save()
            
            # Process file
            try:
                file_path = document.file.path
                text_content = processor.process_file(file_path)
                document.text_content = text_content
                chunks = processor.chunk_text(text_content)
                
                # Store chunks in database
                for i, chunk_content in enumerate(chunks):
                    DocumentChunk.objects.create(
                        document=document,
                        content=chunk_content,
                        chunk_index=i,
                        metadata={'filename': file.name}
                    )
                
                # Store in vector database
                processor.store_chunks(
                    str(document.id), 
                    chunks, 
                    {'title': title, 'source_type': 'file', 'filename': file.name}
                )
                
                document.processed = True
                document.processing_status = 'completed'
                
            except Exception as e:
                document.processing_status = 'failed'
                document.error_message = str(e)
                
        elif source_type == 'text':
            text_content = request.data.get('text_content')
            if not text_content:
                return Response({'error': 'Text content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            document.text_content = text_content
            
            try:
                chunks = processor.chunk_text(text_content)
                
                # Store chunks in database
                for i, chunk_content in enumerate(chunks):
                    DocumentChunk.objects.create(
                        document=document,
                        content=chunk_content,
                        chunk_index=i,
                        metadata={'source_type': 'text'}
                    )
                
                # Store in vector database
                processor.store_chunks(
                    str(document.id), 
                    chunks, 
                    {'title': title, 'source_type': 'text'}
                )
                
                document.processed = True
                document.processing_status = 'completed'
                
            except Exception as e:
                document.processing_status = 'failed'
                document.error_message = str(e)
        
        document.save()
        serializer = DocumentSourceSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_documents(request):
    """List all uploaded documents"""
    documents = DocumentSource.objects.all().order_by('-created_at')
    serializer = DocumentSourceSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_document(request, document_id):
    """Delete a document and its chunks"""
    try:
        document = get_object_or_404(DocumentSource, id=document_id)
        
        # Delete from vector database
        processor = DocumentProcessor()
        try:
            # Get all chunk IDs for this document
            chunk_ids = [f"{document_id}_{chunk.chunk_index}" for chunk in document.chunks.all()]
            if chunk_ids:
                processor.collection.delete(ids=chunk_ids)
        except:
            pass  # Continue even if vector deletion fails
        
        document.delete()
        return Response({'message': 'Document deleted successfully'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def chat(request):
    """Handle chat queries"""
    try:
        query = request.data.get('query', '').strip()
        session_id = request.data.get('session_id')
        
        if not query:
            return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create chat session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id)
        else:
            session = ChatSession.objects.create(title=query[:50] + '...' if len(query) > 50 else query)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=query
        )
        
        # Generate response using RAG
        rag_service = RAGService()
        result = rag_service.chat(query)
        
        # Save assistant message
        assistant_message = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=result['answer'],
            sources_used=result['sources']
        )
        
        return Response({
            'session_id': str(session.id),
            'answer': result['answer'],
            'sources': result['sources'],
            'relevant_chunks': result['relevant_chunks']
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_chat_sessions(request):
    """List all chat sessions"""
    sessions = ChatSession.objects.all().order_by('-updated_at')
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_chat_messages(request, session_id):
    """Get messages for a specific chat session"""
    session = get_object_or_404(ChatSession, id=session_id)
    messages = session.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_chat_session(request, session_id):
    """Delete a chat session"""
    session = get_object_or_404(ChatSession, id=session_id)
    session.delete()
    return Response({'message': 'Chat session deleted successfully'})

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    try:
        # Check Ollama connection
        rag_service = RAGService()
        ollama_status = "connected"
        try:
            rag_service.ollama_client.list()
        except:
            ollama_status = "disconnected"
        
        return Response({
            'status': 'healthy',
            'ollama_status': ollama_status,
            'documents_count': DocumentSource.objects.count(),
            'chat_sessions_count': ChatSession.objects.count()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)