# VoxPilot AI — Conversation Memory Architecture

## 1. Session Memory Overview
VoxPilot AI manages conversation state using `SessionMemory`:
- **Short-Term Turn Storage**: Stores user messages, assistant replies, tool results, and timestamps.
- **Context Windowing**: Maintains a configurable maximum message count (e.g. 10 messages) to bound LLM context size and prevent token blowup.
- **Automatic Summarization**: Automatically summarizes overflowing turns and appends them to system prompt context.

## 2. Event Audit Trail
Every session maintains an event audit trail (`SessionEvent`) tracking user turns, assistant turns, tool executions, RAG retrievals, and barge-in interruptions.
