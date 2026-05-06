import sys
import types
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from . import services


class ChatRetrievalConfigurationTests(SimpleTestCase):
    def setUp(self):
        services.ChatEmbeddingService.model = None
        services.ChatEmbeddingService.model_name = None
        services.ChatEmbeddingService.load_attempted = False

    @override_settings(CHAT_ALLOW_WEB_SEARCH=False)
    def test_retrieve_chat_context_does_not_search_web_by_default(self):
        with patch("chat.services.retrieve_knowledge_chunks", return_value=[]), \
                patch("chat.services.retrieve_document_snippets", return_value=[]), \
                patch("chat.services.search_official_sources") as search:

            chunks = services.retrieve_chat_context(
                "protein advice",
                "Health profile: not completed.",
            )

        self.assertEqual(chunks, [])
        search.assert_not_called()

    @override_settings(CHAT_ALLOW_WEB_SEARCH=True)
    def test_retrieve_chat_context_can_search_web_when_enabled(self):
        with patch("chat.services.retrieve_knowledge_chunks", return_value=[]), \
                patch("chat.services.retrieve_document_snippets", return_value=[]), \
                patch("chat.services.search_official_sources", return_value=[{
                    "source": "WHO",
                    "organization": "WHO",
                    "topic": "diet",
                    "chunk_text": "Protein and whole foods support healthy eating.",
                }]) as search:

            chunks = services.retrieve_chat_context(
                "protein advice",
                "Health profile: not completed.",
            )

        self.assertTrue(chunks)
        search.assert_called_once()

    @override_settings(
        CHAT_ALLOW_EMBEDDING_DOWNLOAD=False,
        CHAT_EMBEDDING_MODEL="fake/model",
        CHAT_EMBEDDING_CACHE_DIR=None,
        CHAT_EMBEDDING_DEVICE="",
    )
    def test_embedding_service_does_not_download_model_by_default(self):
        calls = []

        class FakeSentenceTransformer:
            def __init__(self, model_name, **kwargs):
                calls.append(kwargs)
                if kwargs.get("local_files_only"):
                    raise RuntimeError("not cached")

        fake_module = types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer)

        with patch.dict(sys.modules, {"sentence_transformers": fake_module}):
            model = services.ChatEmbeddingService.load()

        self.assertIsNone(model)
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0]["local_files_only"])
