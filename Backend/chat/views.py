from uuid import UUID

from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import DailyCheckIn, HealthProfile
from recommendations.safety import assess_medical_safety, guard_chat_response

from .models import ChatConversation, ChatMessage
from .serializers import ChatConversationListSerializer, ChatConversationSerializer, ChatMessageSerializer
from .services import build_profile_context, call_nvidia_chat, retrieve_chat_context


class HelpChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    document_text = serializers.CharField(required=False, allow_blank=True, max_length=30000)


class ChatConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    pagination_class = None

    def get_queryset(self):
        queryset = ChatConversation.objects.filter(user=self.request.user)
        if self.action == 'retrieve':
            return queryset.prefetch_related('messages')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatConversationListSerializer
        return ChatConversationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HelpChatView(APIView):
    """
    Backwards-compatible one-shot endpoint.
    Creates a conversation automatically, stores both messages, and returns
    the same response shape the frontend expects.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        conversation = ChatConversation.objects.create(user=request.user)
        return _handle_chat_message(request, conversation)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id: str):
    try:
        UUID(str(conversation_id))
    except ValueError:
        return Response({'detail': 'Invalid conversation id.'}, status=status.HTTP_400_BAD_REQUEST)

    conversation = get_object_or_404(ChatConversation, id=conversation_id, user=request.user)
    return _handle_chat_message(request, conversation)


def _handle_chat_message(request, conversation):
    serializer = HelpChatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    message = serializer.validated_data['message'].strip()
    document_text = serializer.validated_data.get('document_text', '').strip()

    user_message = ChatMessage.objects.create(
        conversation=conversation,
        role='user',
        content=message,
        message_type='chat',
    )

    if conversation.title == 'New Chat':
        conversation.title = message[:60]
        conversation.save(update_fields=['title', 'updated_at'])

    profile = HealthProfile.objects.filter(user=request.user).first()
    latest_checkin = DailyCheckIn.objects.filter(user=request.user).order_by('-date', '-created_at').first()

    profile_context = build_profile_context(profile, latest_checkin)
    snippets = retrieve_chat_context(message, profile_context, document_text)
    safety_assessment = assess_medical_safety(profile=profile, checkin=latest_checkin, text=f"{message}\n{document_text}")
    if safety_assessment["blocks_plan"]:
        answer = safety_assessment["message"]
    else:
        answer = call_nvidia_chat(message, profile_context, snippets)
        answer = guard_chat_response(message, answer, profile=profile, checkin=latest_checkin)
    sources = _serialize_sources(snippets)
    tool_calls = _tool_calls(profile, latest_checkin, sources)

    assistant_message = ChatMessage.objects.create(
        conversation=conversation,
        role='assistant',
        content=answer,
        message_type='rag',
        metadata={
            'sources': sources,
            'tool_calls': tool_calls,
            'used_profile': profile is not None,
            'used_latest_checkin': latest_checkin is not None,
            'safety_level': safety_assessment["level"],
            'safety_reasons': safety_assessment["reasons"],
        },
    )

    conversation.save(update_fields=['updated_at'])

    return Response(
        {
            'answer': answer,
            'sources': sources,
            'tool_calls': tool_calls,
            'used_profile': profile is not None,
            'used_latest_checkin': latest_checkin is not None,
            'safety': {
                'level': safety_assessment["level"],
                'reasons': safety_assessment["reasons"],
                'blocked': safety_assessment["blocks_plan"],
            },
            'conversation': ChatConversationSerializer(conversation).data,
            'user_message': ChatMessageSerializer(user_message).data,
            'ai_response': ChatMessageSerializer(assistant_message).data,
        },
        status=status.HTTP_200_OK,
    )


def _serialize_sources(snippets):
    return [
        {
            'type': source.get('topic', 'document'),
            'label': source.get('source', f'Source {index + 1}'),
            'text': source.get('chunk_text', ''),
            'url': source.get('url', ''),
            'organization': source.get('organization', ''),
            'subtopic': source.get('subtopic', ''),
            'population': source.get('population', ''),
            'condition': source.get('condition', ''),
        }
        for index, snippet in enumerate(snippets)
        for source in [snippet]
    ]


def _tool_calls(profile, latest_checkin, sources):
    return [
        {
            'name': 'profile_context',
            'status': 'success' if profile else 'empty',
            'detail': 'Loaded user health profile.' if profile else 'No health profile found.',
        },
        {
            'name': 'latest_checkin',
            'status': 'success' if latest_checkin else 'empty',
            'detail': 'Loaded latest daily health status.' if latest_checkin else 'No daily check-in found.',
        },
        {
            'name': 'rag_retrieval',
            'status': 'success' if sources else 'empty',
            'detail': f'Retrieved {len(sources)} context chunks from local KB, safety rules, user document, or official-source search.',
        },
        {
            'name': 'nvidia_llm',
            'status': 'success',
            'detail': 'Generated answer using configured NVIDIA chat model, with fallback text if the model was unavailable.',
        },
    ]
