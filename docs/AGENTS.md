# VoxPilot AI — Multi-Agent Architecture

## 1. Intent Router Agent
The `VoiceRouterAgent` acts as the primary intent classifier dispatching incoming user turns to specialized domain agents:
- **KnowledgeAgent**: RAG specialist handling product documentation and policies.
- **TaskAgent**: Execution specialist handling math, weather lookups, and task creation.
- **SupportAgent**: CRM specialist handling customer profiles and account support.
- **GeneralAgent**: Conversational agent handling general dialogue.

## 2. Safe Tool Execution Boundaries
Each specialized agent maintains strict tool allowances. Tools are registered in `ToolRegistry` with JSON schema validation, execution timeouts (e.g. 3.0s), permission levels, and exception capture.
