# Chat Knowledge Base

This folder stores committed safety rules for the Help Chat endpoint.

Downloaded official guideline documents and generated chunks live under:

```text
Backend/media/chat_knowledge_base/
```

That media folder is intentionally gitignored.

Suggested build command after Python is available:

```bash
python manage.py build_chat_kb --download
```

The endpoint also includes a small fallback chunk set so it can work before the full KB is built.
