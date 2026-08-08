# VoxPilot AI — Security Audit & Controls Specification

## 1. Security Architecture Summary
VoxPilot AI enforces defense-in-depth security controls across prompt evaluation, tool execution boundaries, secret storage, and API access.

| Threat Category | Mitigation Strategy | Implementation |
| :--- | :--- | :--- |
| **Arbitrary Code Execution** | AST Math Evaluation | Evaluates mathematical expressions using Python `ast` syntax nodes. No `eval()` or shell invocations. |
| **Tool Execution Abuse** | Risk Classifier & Permissions | Tools categorized into `LOW`, `MEDIUM`, `HIGH`, `BLOCKED`. High/Medium side-effects require human confirmation. |
| **System Shell Command Injection** | Permanent Blacklisting | `system_shell` and arbitrary command tools are permanently BLOCKED at permission guard boundary. |
| **Prompt Injection Attacks** | Untrusted Output Sanitization | System prompts enforce context isolation; LLM outputs treated as untrusted data before processing. |
| **Secret & Key Exposure** | Environment Variables & Log Scrubbing | Secrets loaded exclusively via `.env` / Pydantic Settings. `JSONFormatter` scrubs sensitive headers. |
| **Session State Isolation** | Correlation Session IDs | WebSocket sessions and conversation state strictly scoped to session correlation IDs. |

## 2. Risk Classification Matrix
- **LOW Risk** (`calculator`, `weather_search`, `knowledge_search`): Executes automatically.
- **MEDIUM Risk** (`calendar_scheduler`, `task_creator`, `crm_customer_lookup`): Requires pending user confirmation.
- **HIGH Risk** (`send_email`, `execute_payment`): Requires explicit user confirmation modal.
- **BLOCKED** (`system_shell`): Forbidden by policy.
