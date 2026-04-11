from app.schemas.analysis import AnalysisResult


class AnalysisService:
    """
    MVP analysis service.

    For now, this produces a structured draft from the raw input
    using deterministic rules and lightweight heuristics.
    """

    def run(
        self,
        user_input: str,
        context_hint: str | None,
        classification: dict,
    ) -> AnalysisResult:
        ambiguities = self._extract_ambiguities(user_input)
        risks = self._extract_risks(user_input)
        open_questions = self._extract_open_questions(user_input)

        return AnalysisResult(
            reformulation=self._build_reformulation(user_input),
            request_summary="Structured analysis draft generated from raw input.",
            context_hint=context_hint,
            detected_type=classification["request_type"],
            ambiguities=ambiguities,
            risks=risks,
            open_questions=open_questions,
            recommended_next_step=(
                "Clarify the open questions, validate scope, then decide whether to create "
                "a ticket, documentation, or a recipe asset."
            ),
        )

    def _build_reformulation(self, user_input: str) -> str:
        return f"Analyse d'un sujet metier ou fonctionnel a partir de la demande suivante : {user_input}"

    def _extract_ambiguities(self, user_input: str) -> list[str]:
        ambiguities: list[str] = []

        lowered = user_input.lower()
        if "on ne sait pas" in lowered or "a confirmer" in lowered or "à confirmer" in lowered:
            ambiguities.append("Le perimetre exact ou le comportement cible n'est pas confirme.")

        if "impact" not in lowered:
            ambiguities.append("Les impacts fonctionnels ou techniques ne sont pas explicites.")

        return ambiguities

    def _extract_risks(self, user_input: str) -> list[str]:
        risks = ["Risque de mauvaise comprehension du besoin si les hypotheses ne sont pas validees."]

        lowered = user_input.lower()
        if "batch" in lowered or "import" in lowered:
            risks.append("Risque de divergence entre traitements unitaires et traitements batch.")

        if "legacy" in lowered:
            risks.append("Risque de regression lie a la complexite du legacy.")

        return risks

    def _extract_open_questions(self, user_input: str) -> list[str]:
        questions = [
            "Quel est le comportement actuel observe ?",
            "Quel est le comportement attendu cible ?",
            "Le perimetre exact est-il confirme par le metier ?",
        ]

        lowered = user_input.lower()
        if "batch" in lowered or "import" in lowered:
            questions.append("Le comportement cible doit-il s'appliquer aussi aux flux batch/import ?")

        return questions
