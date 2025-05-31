# docs_assistant/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.list_documents, name='list_documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/<uuid:document_id>/', views.delete_document, name='delete_document'),
    path('chat/', views.chat, name='chat'),
    path('chat/sessions/', views.list_chat_sessions, name='list_chat_sessions'),
    path('chat/sessions/<uuid:session_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('chat/sessions/<uuid:session_id>/', views.delete_chat_session, name='delete_chat_session'),
    path('health/', views.health_check, name='health_check'),
]

