# RAG Chat Subsystem

## Overview
The RAG chat subsystem is the app's only LLM-backed feature. It lets authenticated users ask fitness, nutrition, recovery, and plan-related questions. Answers are grounded with profile/check-in context, local safety rules, retrieved guidance snippets, and optional uploaded text.

## Core Architecture
- **Framework**: Django REST Framework.
- **LLM Provider**: NVIDIA/OpenAI-compatible chat completion API, configured through `NVIDIA_API_URL` and `NVIDIA_LLM_MODEL`.
- **Persistent Conversations**: Conversations and messages are stored server-side with `ChatConversation` and `ChatMessage`, allowing users to switch between previous chats.
- **RAG Retrieval**: The backend retrieves local safety rules, official health guidance chunks, optional uploaded text snippets, and official-source search results.
- **Retrieval Mode**: If the optional embedding model is available, semantic retrieval is used. Otherwise the chat falls back to keyword scoring and built-in safety/source snippets.

## Key Features

### 1. Chat Endpoints
- **One-shot Endpoint**: `POST /api/chat/`
- **Conversation Endpoints**:
  - `GET /api/chat/conversations/`
  - `POST /api/chat/conversations/`
  - `GET /api/chat/conversations/<id>/`
  - `POST /api/chat/conversations/<id>/message/`
- **Configuration**: Controlled securely via `.env` variables (`NVIDIA_API_KEY`, `NVIDIA_API_URL`, `NVIDIA_LLM_MODEL`).
- **Prompt Scope**: The backend tells the model to answer only as a fitness/nutrition support assistant, use retrieved context where possible, and avoid diagnosis, medication advice, or unsafe extreme plans.

### 2. Medical Safety Gate
- Chat calls `recommendations.safety.assess_medical_safety` before the LLM.
- Emergency or clinician-review prompts bypass the model and return deterministic safety guidance.
- Caution cases append a safety note after generation.
- Safety metadata is stored in the assistant message metadata and returned in the API response.

See [`medical_safety.md`](medical_safety.md) for the full policy.

### 3. Profile-Aware Responses
- The backend loads the user's latest `HealthProfile` and latest `DailyCheckIn`.
- This allows the chat answer to consider profile and readiness data. For example, if a user asks "Can I substitute the squats today?", the backend can include the user's knee injury status and available equipment in context.

### 4. Frontend Chat Interface
- **Component**: `HelpChat.tsx`
- **UX**: Implemented as an embeddable chat panel/page component.
- **Conversation Controls**: The embedded widget includes a compact conversation selector and a `New Chat` button.
- **Formatting**: Assistant answers render compact paragraphs, bullets, bold labels, and source cards instead of raw markdown/citation syntax.

## Future Enhancements
- Add automated red-flag chat tests for chest pain, kidney disease, eating disorder language, diabetes medication questions, and injury escalation.
- Add clinician-reviewed source packs for special populations and chronic conditions.
