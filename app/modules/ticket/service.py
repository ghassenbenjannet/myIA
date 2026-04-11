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
    ) -> dict:
        request_type = classification["request_type"]

        return {
            "ticket_type": self._map_ticket_type(request_type),
            "title": self._build_title(request_type, user_input),
            "description": user_input,
            "context": context_hint or "No additional context provided.",
            "business_goal": self._build_business_goal(request_type),
            "acceptance_criteria": self._build_acceptance_criteria(request_type),
            "dependencies": self._build_dependencies(user_input),
            "open_points": self._build_open_points(user_input),
        }

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
            return "Corriger un comportement incorrect observé."
        if request_type == "evolution":
            return "Faire évoluer le produit pour répondre à un nouveau besoin."
        if request_type == "recipe":
            return "Préparer ou compléter la couverture de recette."
        return "Structurer et piloter une action PO."

    def _build_acceptance_criteria(self, request_type: str) -> list[str]:
        criteria = [
            "Le besoin est reformulé de manière claire et compréhensible.",
            "Les points à confirmer sont explicités.",
            "Les impacts ou dépendances sont identifiés si connus.",
        ]

        if request_type == "bug":
            criteria.insert(0, "Le comportement observé et le comportement attendu sont distingués.")

        if request_type == "evolution":
            criteria.insert(0, "Le nouveau comportement attendu est défini.")

        return criteria

    def _build_dependencies(self, user_input: str) -> list[str]:
        dependencies: list[str] = []
        lowered = user_input.lower()

        if "batch" in lowered:
            dependencies.append("Vérifier les traitements batch concernés.")
        if "import" in lowered:
            dependencies.append("Vérifier les flux d'import concernés.")
        if "api" in lowered:
            dependencies.append("Vérifier les impacts éventuels sur les API.")

        return dependencies

    def _build_open_points(self, user_input: str) -> list[str]:
        open_points = [
            "Le périmètre exact doit être confirmé.",
            "Les règles métier détaillées doivent être validées.",
        ]

        lowered = user_input.lower()
        if "urgent" in lowered:
            open_points.append("Le niveau de priorité doit être confirmé.")
        if "prod" in lowered or "production" in lowered:
            open_points.append("Confirmer si une anomalie est présente en production.")

        return open_points
