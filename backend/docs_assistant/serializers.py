# docs_assistant/serializers.py
from rest_framework import serializers
from .models import DocumentSource, ChatSession, ChatMessage, DocumentChunk

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['content', 'chunk_index', 'metadata', 'created_at']

class DocumentSourceSerializer(serializers.ModelSerializer):
    chunks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentSource
        fields = [
            'id', 'title', 'source_type', 'url', 'file', 
            'created_at', 'processed', 'processing_status', 
            'error_message', 'chunks_count'
        ]
        read_only_fields = ['id', 'created_at', 'processed', 'processing_status']
    
    def get_chunks_count(self, obj):
        return obj.chunks.count()

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message_type', 'content', 'sources_used', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages_count', 'last_message']
    
    def get_messages_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'created_at': last_message.created_at
            }
        return None