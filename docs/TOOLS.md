# VoxPilot AI — Safe Tool Registry & Boundaries

## 1. Tool System Architecture
VoxPilot AI features a centralized `ToolRegistry`:
- **Strict Parameter Validation**: Validates tool inputs using JSON Schema definitions.
- **AST Safe Calculator**: Evaluates mathematical expressions using Python's `ast` module safely without `eval()`.
- **Execution Timeouts**: Enforces execution timeout boundaries (e.g. 3.0 seconds) to prevent long-running calls from blocking voice response pipelines.
- **Permission Boundaries**: Tools define permission scoping (`public`, `user`, `admin`). No arbitrary shell execution is permitted.

## 2. Builtin Tools
- `calculator`: Safe math expression evaluation.
- `weather_search`: Location weather condition lookup.
- `crm_customer_lookup`: Customer profile lookup.
- `task_creator`: System action item creation.
