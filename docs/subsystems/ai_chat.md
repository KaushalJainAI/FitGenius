# AI Chat Subsystem

## Overview
The AI Chat subsystem provides an interactive, conversational layer to the FitGenius AI application. It allows users to ask ad-hoc questions about their fitness journey, nutrition, or exercises, receiving instant context-aware advice.

## Core Architecture
- **Framework**: Django REST Framework.
- **LLM Provider**: NVIDIA API integration utilizing the `meta/llama-3.1-70b-instruct` model.
- **Stateless Design**: For maximum performance and minimal database bloat, chat sessions are currently handled statelessly by the backend. The frontend manages the conversation history array and passes it back to the LLM for context.

## Key Features

### 1. Integration with NVIDIA LLM
- **Endpoint**: `POST /api/chat/`
- **Configuration**: Controlled securely via `.env` variables (`NVIDIA_API_KEY`, `NVIDIA_API_URL`, `NVIDIA_LLM_MODEL`).
- **Prompt Engineering**: The backend injects a strict system prompt compelling the LLM to behave strictly as a fitness and nutrition coach. It explicitly prevents the LLM from providing medical diagnoses or advice outside of the fitness domain.

### 2. Context-Aware Responses
- The frontend securely passes the user's latest `HealthProfile` and active `Recommendation` context into the chat session upon initialization.
- This allows the AI to provide hyper-personalized answers. For example, if a user asks "Can I substitute the squats today?", the LLM already knows the user's knee injury status and available equipment from their profile.

### 3. Frontend Chat Interface
- **Component**: `HelpChat.tsx`
- **UX**: Implemented as a collapsible, floating UI widget accessible from anywhere within the authenticated application. It features a modern chat-bubble design with typing indicators and graceful error handling.

## Future Enhancements
- **Retrieval-Augmented Generation (RAG)**: Future iterations aim to integrate vector database searches against verified fitness literature (like local PDFs or articles) to further ground the LLM's responses.
- **Persistent History**: Migrating the conversation array storage from the React frontend to a Django `ChatMessage` model to allow users to review past advice across different devices.
