from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import DailyCheckIn, HealthProfile

from .services import build_profile_context, call_nvidia_chat, retrieve_chat_context


class HelpChatSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    document_text = serializers.CharField(required=False, allow_blank=True, max_length=30000)


class HelpChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HelpChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data['message'].strip()
        document_text = serializer.validated_data.get('document_text', '').strip()

        profile = HealthProfile.objects.filter(user=request.user).first()
        latest_checkin = DailyCheckIn.objects.filter(user=request.user).order_by('-date', '-created_at').first()

        profile_context = build_profile_context(profile, latest_checkin)
        snippets = retrieve_chat_context(message, profile_context, document_text)
        answer = call_nvidia_chat(message, profile_context, snippets)

        return Response(
            {
                'answer': answer,
                'sources': [
                    {
                        'type': source.get('topic', 'document'),
                        'label': source.get('source', f'Source {index + 1}'),
                        'text': source.get('chunk_text', ''),
                        'url': source.get('url', ''),
                    }
                    for index, snippet in enumerate(snippets)
                    for source in [snippet]
                ],
                'used_profile': profile is not None,
                'used_latest_checkin': latest_checkin is not None,
            },
            status=status.HTTP_200_OK,
        )
