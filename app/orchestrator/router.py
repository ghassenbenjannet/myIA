from typing import Literal

WorkflowName = Literal["analysis", "ticket", "documentation"]


class WorkflowRouter:
    """
    Simple routing layer for the MVP.

    Rules:
    - analysis -> analysis module
    - bug/evolution/recipe/po_pilotage -> ticket module
    - documentation -> documentation module
    - unknown -> analysis module
    """

    def route(self, request_type: str, target_output: str = "auto") -> WorkflowName:
        if target_output == "analysis":
            return "analysis"
        if target_output == "ticket":
            return "ticket"
        if target_output == "documentation":
            return "documentation"

        if request_type == "documentation":
            return "documentation"

        if request_type in {"bug", "evolution", "recipe", "po_pilotage"}:
            return "ticket"

        return "analysis"
