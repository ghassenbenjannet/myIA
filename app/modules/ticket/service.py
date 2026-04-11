from app.schemas.ticket import TicketResult


class TicketService:
    """
    MVP ticket generation service.
    Produces a structured draft for bug/evolution/recipe/pilotage-related requests.
    """

    def run(
        self,
        user_input: str,
        context_hint: str | None,
        classification: dict,
    ) -> TicketResult:
        request_type = classification["request_type"]

        return TicketResult(
            ticket_type=self._map_ticket_type(request_type),
            title=self._build_title(request_type, user_input),
            description=user_input,
            context=context_hint or "No additional context provided.",
            business_goal=self._build_business_goal(request_type),
            acceptance_criteria=self._build_acceptance_criteria(request_type),
            dependencies=self._build_dependencies(user_input),
            open_points=self._build_open_points(user_input),
        )

    def _map_ticket_type(self, request_type: str) -> str:
        if request_type == "bug":
            return "bug"
        if request_type == "evolution":
            return "story"
        if request_type == "recipe":
            return "test"
        return "task"

    def _build_title(self, request_type: str, user_input: str) -> str:
        prefix_map = {
            "bug": "[BUG]",
            "evolution": "[EVOL]",
            "recipe": "[RECETTE]",
            "po_pilotage": "[PO]",
        }
        prefix = prefix_map.get(request_type, "[ANALYSE]")
        short_text = user_input.strip()
        if len(short_text) > 80:
            short_text = short_text[:77] + "..."
        return f"{prefix} {short_text}"

    def _build_business_goal(self, request_type: str) -> str:
        if request_type == "bug":
            return "Corriger un comportement incorrect observe."
        if request_type == "evolution":
            return "Faire evoluer le produit pour repondre a un nouveau besoin."
        if request_type == "recipe":
            return "Preparer ou completer la couverture de recette."
        return "Structurer et piloter une action PO."

    def _build_acceptance_criteria(self, request_type: str) -> list[str]:
        criteria = [
            "Le besoin est reformule de maniere claire et comprehensible.",
            "Les points a confirmer sont explicites.",
            "Les impacts ou dependances sont identifies si connus.",
        ]

        if request_type == "bug":
            criteria.insert(0, "Le comportement observe et le comportement attendu sont distingues.")

        if request_type == "evolution":
            criteria.insert(0, "Le nouveau comportement attendu est defini.")

        return criteria

    def _build_dependencies(self, user_input: str) -> list[str]:
        dependencies: list[str] = []
        lowered = user_input.lower()

        if "batch" in lowered:
            dependencies.append("Verifier les traitements batch concernes.")
        if "import" in lowered:
            dependencies.append("Verifier les flux d'import concernes.")
        if "api" in lowered:
            dependencies.append("Verifier les impacts eventuels sur les API.")

        return dependencies

    def _build_open_points(self, user_input: str) -> list[str]:
        open_points = [
            "Le perimetre exact doit etre confirme.",
            "Les regles metier detaillees doivent etre validees.",
        ]

        lowered = user_input.lower()
        if "urgent" in lowered:
            open_points.append("Le niveau de priorite doit etre confirme.")
        if "prod" in lowered or "production" in lowered:
            open_points.append("Confirmer si une anomalie est presente en production.")

        return open_points
