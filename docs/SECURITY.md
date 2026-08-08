# VoxPilot AI — Security Policy & Boundaries

## 1. Security Architecture
VoxPilot AI enforces strict security controls:
- **No Arbitrary Code Execution**: Tools execute within AST parsers and strictly typed Pydantic parameters. No shell or system `eval()` execution is permitted.
- **Permission Boundaries**: Tools are scoped by permission levels (`public`, `user`, `admin`).
- **Secret Management**: API keys and database credentials are managed exclusively via environment variables (`.env`). Secrets are never logged or returned in responses.
- **Untrusted LLM Output**: LLM responses are sanitized before execution.
