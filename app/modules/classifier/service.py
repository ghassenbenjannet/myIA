from typing import Literal


ClassificationType = Literal[
    "bug",
    "evolution",
    "documentation",
    "recipe",
    "po_pilotage",
    "analysis",
]


class ClassifierService:
    """
    Deterministic heuristic classifier for the MVP.

    The logic stays intentionally simple and testable:
    explicit target_output may guide the result, then keyword groups are scored.
    """

    BUG_KEYWORDS = {
        "bug",
        "erreur",
        "incident",
        "anomalie",
        "ko",
        "bloquant",
        "defaut",
        "crash",
        "echec",
        "fail",
    }
    EVOLUTION_KEYWORDS = {
        "evolution",
        "evol",
        "evolutionnaire",
        "evolutionnel",
        "evolutions",
        "evolutionner",
        "evolutionnee",
        "amelioration",
        "nouveau besoin",
        "besoin",
        "feature",
        "fonctionnalite",
        "optimisation",
    }
    RECIPE_KEYWORDS = {
        "recette",
        "tester",
        "test",
        "tests",
        "cas de test",
        "non regression",
        "non-regression",
        "validation",
        "homologation",
    }
    DOCUMENTATION_KEYWORDS = {
        "confluence",
        "documentation",
        "documenter",
        "doc",
        "compte-rendu",
        "compte rendu",
        "synthese",
        "procedure",
        "mode operatoire",
    }
    PO_PILOTAGE_KEYWORDS = {
        "backlog",
        "priorisation",
        "priorite",
        "epic",
        "jira",
        "pilotage",
        "suivi",
        "roadmap",
        "arbitrage",
        "lotissement",
    }

    def classify(
        self,
        user_input: str,
        context_hint: str | None = None,
        target_output: str = "auto",
    ) -> dict:
        text = self._normalize_text(f"{user_input} {context_hint or ''}")

        if target_output == "analysis":
            return self._build_result("analysis", 0.96, ["forced by target_output=analysis"])

        if target_output == "documentation":
            return self._build_result(
                "documentation",
                0.96,
                ["forced by target_output=documentation"],
            )

        scores = {
            "bug": self._count_matches(text, self.BUG_KEYWORDS),
            "evolution": self._count_matches(text, self.EVOLUTION_KEYWORDS),
            "recipe": self._count_matches(text, self.RECIPE_KEYWORDS),
            "documentation": self._count_matches(text, self.DOCUMENTATION_KEYWORDS),
            "po_pilotage": self._count_matches(text, self.PO_PILOTAGE_KEYWORDS),
        }

        if target_output == "ticket":
            ticket_type = self._select_ticket_type(scores)
            if ticket_type is not None:
                return self._build_result(
                    ticket_type,
                    0.92,
                    [f"guided by target_output=ticket and matched {ticket_type} keywords"],
                )
            return self._build_result("po_pilotage", 0.78, ["target_output=ticket fallback"])

        best_type = self._select_best_type(scores)
        if best_type is None:
            return self._build_result("analysis", 0.75, ["default fallback to analysis"])

        confidence = self._confidence_from_score(scores[best_type])
        return self._build_result(
            best_type,
            confidence,
            [f"{best_type}-related keywords detected"],
        )

    def _normalize_text(self, value: str) -> str:
        replacements = {
            "é": "e",
            "è": "e",
            "ê": "e",
            "à": "a",
            "â": "a",
            "ù": "u",
            "û": "u",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ç": "c",
        }
        normalized = value.lower()
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        return normalized

    def _count_matches(self, text: str, keywords: set[str]) -> int:
        return sum(1 for keyword in keywords if keyword in text)

    def _select_ticket_type(self, scores: dict[str, int]) -> ClassificationType | None:
        ticket_candidates = ("bug", "evolution", "recipe", "po_pilotage")
        ranked = sorted(ticket_candidates, key=lambda item: scores[item], reverse=True)
        best = ranked[0]
        if scores[best] == 0:
            return None
        return best

    def _select_best_type(self, scores: dict[str, int]) -> ClassificationType | None:
        priority = ("bug", "documentation", "recipe", "evolution", "po_pilotage")
        ranked = sorted(priority, key=lambda item: (scores[item], -priority.index(item)), reverse=True)
        best = ranked[0]
        if scores[best] == 0:
            return None
        return best

    def _confidence_from_score(self, score: int) -> float:
        if score >= 3:
            return 0.93
        if score == 2:
            return 0.88
        return 0.82

    def _build_result(self, request_type: ClassificationType, confidence: float, reasons: list[str]) -> dict:
        return {
            "request_type": request_type,
            "confidence": confidence,
            "reasons": reasons,
        }
