class ClassifierService:
    """
    Very simple heuristic classifier for the MVP.

    This is intentionally deterministic and lightweight.
    A real LLM-based or hybrid classifier can replace it later.
    """

    def classify(self, user_input: str, context_hint: str | None = None) -> dict:
        text = f"{user_input} {context_hint or ''}".lower()

        if any(keyword in text for keyword in ["bug", "erreur", "incident", "anomalie", "ko"]):
            return {
                "request_type": "bug",
                "confidence": 0.9,
                "reasons": ["bug-related keywords detected"],
            }

        if any(
            keyword in text
            for keyword in ["evolution", "évolution", "amélioration", "nouveau besoin", "feature"]
        ):
            return {
                "request_type": "evolution",
                "confidence": 0.88,
                "reasons": ["evolution-related keywords detected"],
            }

        if any(
            keyword in text
            for keyword in ["recette", "test", "cas de test", "non regression", "non-régression"]
        ):
            return {
                "request_type": "recipe",
                "confidence": 0.84,
                "reasons": ["recipe/test-related keywords detected"],
            }

        if any(
            keyword in text
            for keyword in ["confluence", "documentation", "doc", "compte-rendu", "synthèse"]
        ):
            return {
                "request_type": "documentation",
                "confidence": 0.86,
                "reasons": ["documentation-related keywords detected"],
            }

        if any(
            keyword in text
            for keyword in ["backlog", "priorisation", "epic", "jira", "pilotage", "suivi"]
        ):
            return {
                "request_type": "po_pilotage",
                "confidence": 0.8,
                "reasons": ["PO management keywords detected"],
            }

        return {
            "request_type": "analysis",
            "confidence": 0.75,
            "reasons": ["default fallback to analysis"],
        }
