"""Responses API Function Calling loop for the testing Harness."""

import json
import os
from typing import Any, Dict

from openai import OpenAI

from agent_tools import FUNCTION_TOOLS, execute_tool
from harness import WorkflowRunner
from workspace import Workspace


def run_function_calling(goal: str, workspace: Workspace, max_turns: int = 6) -> Dict[str, Any]:
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    runner = WorkflowRunner(workspace)
    input_items = [{"role": "user", "content": goal}]

    for turn in range(1, max_turns + 1):
        runner._event("function_calling.turn.started", turn=turn)
        response = client.responses.create(
            model=model,
            input=input_items,
            tools=FUNCTION_TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
        )
        input_items.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            runner._event("function_calling.completed", turn=turn)
            return {
                "status": "completed",
                "turns": turn,
                "output": response.output_text,
            }

        for call in calls:
            try:
                arguments = json.loads(call.arguments)
                result = execute_tool(call.name, arguments, workspace)
                output = {"ok": True, "result": result}
            except Exception as error:
                output = {"ok": False, "error": str(error)}
            runner._event(
                "function_calling.tool.completed",
                turn=turn,
                tool=call.name,
                ok=output["ok"],
            )
            input_items.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(output, ensure_ascii=False),
            })

    raise RuntimeError(f"Function Calling exceeded max_turns={max_turns}")
