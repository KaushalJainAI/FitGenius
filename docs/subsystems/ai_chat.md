# AI Chat Subsystem

## Overview
The AI Chat subsystem provides an interactive, conversational layer to the FitGenius AI application. It allows users to ask ad-hoc questions about their fitness journey, nutrition, or exercises, receiving instant context-aware advice.

## Core Architecture
- **Framework**: Django REST Framework.
- **LLM Provider**: NVIDIA/OpenAI-compatible chat completion API, configured through `NVIDIA_API_URL` and `NVIDIA_LLM_MODEL`.
- **Persistent Conversations**: Conversations and messages are stored server-side with `ChatConversation` and `ChatMessage`, allowing users to switch between previous chats.
- **RAG Retrieval**: The backend retrieves local safety rules, official health guidance chunks, optional uploaded text snippets, and official-source search results.
- **Local Encoder**: Semantic retrieval uses the Qwen embedding model configured by `CHAT_EMBEDDING_MODEL`. It is cached under `Backend/models/chat_embeddings/` and ignored by git.

## Key Features

### 1. Integration with NVIDIA LLM
- **One-shot Endpoint**: `POST /api/chat/`
- **Conversation Endpoints**:
  - `GET /api/chat/conversations/`
  - `POST /api/chat/conversations/`
  - `GET /api/chat/conversations/<id>/`
  - `POST /api/chat/conversations/<id>/message/`
- **Configuration**: Controlled securely via `.env` variables (`NVIDIA_API_KEY`, `NVIDIA_API_URL`, `NVIDIA_LLM_MODEL`).
- **Prompt Engineering**: The backend injects a strict system prompt compelling the LLM to behave strictly as a fitness and nutrition coach. It explicitly prevents the LLM from providing medical diagnoses or advice outside of the fitness domain.

### 2. Medical Safety Gate
- Chat calls `recommendations.safety.assess_medical_safety` before the LLM.
- Emergency or clinician-review prompts bypass the model and return deterministic safety guidance.
- Caution cases append a safety note after generation.
- Safety metadata is stored in the assistant message metadata and returned in the API response.

See [`medical_safety.md`](medical_safety.md) for the full policy.

### 3. Context-Aware Responses
- The backend loads the user's latest `HealthProfile` and latest `DailyCheckIn`.
- This allows the AI to provide profile-aware answers. For example, if a user asks "Can I substitute the squats today?", the backend can include the user's knee injury status and available equipment in context.

### 4. Frontend Chat Interface
- **Component**: `HelpChat.tsx`
- **UX**: Implemented as a collapsible, floating UI widget accessible from anywhere within the authenticated application.
- **Conversation Controls**: The embedded widget includes a compact conversation selector and a `New Chat` button.
- **Formatting**: Assistant answers render compact paragraphs, bullets, bold labels, and source cards instead of raw markdown/citation syntax.

## Future Enhancements
- Add automated red-flag chat tests for chest pain, kidney disease, eating disorder language, diabetes medication questions, and injury escalation.
- Add clinician-reviewed source packs for special populations and chronic conditions.
