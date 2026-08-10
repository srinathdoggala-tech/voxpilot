"""Built-in safe tools for VoxPilot AI platform."""

import ast
import operator
from voxpilot.tools.registry import SafeTool, tool_registry

# ------------------------------------------------------------------------------
# 1. Calculator Tool (Safe AST Math Evaluation)
# ------------------------------------------------------------------------------
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif hasattr(ast, "Num") and isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        op_type = type(node.op)
        if op_type in _SAFE_OPERATORS:
            return _SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported math operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval_node(node.operand)
        op_type = type(node.op)
        if op_type in _SAFE_OPERATORS:
            return _SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported math operator: {op_type}")
    raise ValueError("Invalid mathematical expression syntax")


async def safe_calculator(expression: str) -> float | int:
    """Safely calculate mathematical expression without using eval()."""
    tree = ast.parse(expression, mode='eval')
    return _safe_eval_node(tree.body)


tool_registry.register(
    SafeTool(
        name="calculator",
        description="Safely evaluate a mathematical expression (e.g. '25 * 4 + 10').",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Mathematical expression string"}
            },
            "required": ["expression"]
        },
        timeout_seconds=2.0
    ),
    safe_calculator
)

# ------------------------------------------------------------------------------
# 2. Weather Search Tool
# ------------------------------------------------------------------------------
async def weather_search(location: str) -> dict:
    """Mock weather service lookup."""
    return {
        "location": location,
        "temperature_celsius": 22.5,
        "condition": "Partly Cloudy",
        "humidity_percent": 60
    }


tool_registry.register(
    SafeTool(
        name="weather_search",
        description="Fetch current weather conditions for a specified location.",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City or location name"}
            },
            "required": ["location"]
        },
        timeout_seconds=2.0
    ),
    weather_search
)

# ------------------------------------------------------------------------------
# 3. CRM Customer Lookup Tool
# ------------------------------------------------------------------------------
async def crm_customer_lookup(customer_id: str) -> dict:
    """Mock CRM customer database lookup."""
    return {
        "customer_id": customer_id,
        "name": "Sarah Jenkins",
        "plan": "Enterprise Voice",
        "support_tier": "VIP Premium",
        "open_tickets": 0
    }


tool_registry.register(
    SafeTool(
        name="crm_customer_lookup",
        description="Retrieve customer profile details from CRM.",
        parameters={
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Unique customer ID code"}
            },
            "required": ["customer_id"]
        },
        timeout_seconds=3.0
    ),
    crm_customer_lookup
)

# ------------------------------------------------------------------------------
# 4. Task Creator Tool
# ------------------------------------------------------------------------------
async def create_task(title: str, priority: str = "medium") -> dict:
    """Mock task creation tool."""
    return {
        "task_id": "TASK-9042",
        "title": title,
        "priority": priority,
        "status": "Created"
    }


tool_registry.register(
    SafeTool(
        name="task_creator",
        description="Create a new task or action item in system tracker.",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Brief title of the task"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Task priority level"}
            },
            "required": ["title"]
        },
        timeout_seconds=3.0
    ),
    create_task
)
