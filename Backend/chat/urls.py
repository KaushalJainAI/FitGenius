from django.urls import path

from .views import HelpChatView


urlpatterns = [
    path('', HelpChatView.as_view(), name='help-chat'),
]
