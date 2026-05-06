from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatConversationViewSet, HelpChatView, send_message

router = DefaultRouter()
router.register(r'conversations', ChatConversationViewSet, basename='chat-conversations')

urlpatterns = [
    path('', HelpChatView.as_view(), name='help-chat'),
    path('', include(router.urls)),
    path('conversations/<uuid:conversation_id>/message/', send_message, name='chat-send-message'),
]
