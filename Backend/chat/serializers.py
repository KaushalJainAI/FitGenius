from rest_framework import serializers

from .models import ChatConversation, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()
    tool_calls = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'content', 'message_type', 'metadata',
            'sources', 'tool_calls', 'created_at',
        ]
        read_only_fields = fields

    def get_sources(self, obj):
        return obj.metadata.get('sources', [])

    def get_tool_calls(self, obj):
        return obj.metadata.get('tool_calls', [])


class ChatConversationSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatConversation
        fields = [
            'id', 'title', 'intent', 'system_prompt', 'total_tokens_used',
            'created_at', 'updated_at', 'messages',
        ]
        read_only_fields = ['id', 'total_tokens_used', 'created_at', 'updated_at', 'messages']


class ChatConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConversation
        fields = ['id', 'title', 'intent', 'created_at', 'updated_at']
        read_only_fields = fields
