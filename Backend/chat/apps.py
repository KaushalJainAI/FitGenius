from django.apps import AppConfig
import logging


logger = logging.getLogger('chat')


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        try:
            from .services import preload_chat_rag_encoder

            preload_chat_rag_encoder()
        except Exception as exc:
            logger.warning("Failed to preload chat RAG encoder on startup: %s", exc)
