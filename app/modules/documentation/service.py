class DocumentationService:
    """
    MVP documentation service.
    Produces a structured documentation draft from raw notes or requests.
    """

    def run(
        self,
        user_input: str,
        context_hint: str | None,
        classification: dict,
    ) -> dict:
        return {
            "document_type": "working_draft",
            "title": self._build_title(user_input),
            "summary": "Draft de documentation structuré à partir de la demande fournie.",
            "context": context_hint or "No additional context provided.",
            "sections": [
                {
                    "title": "Contexte",
                    "content": user_input,
                },
                {
                    "title": "Points clés",
                    "content": "À compléter ou affiner lors de la validation métier.",
                },
                {
                    "title": "Questions ouvertes",
                    "content": [
                        "Quels éléments doivent être documentés en priorité ?",
                        "Quel est le public cible de cette documentation ?",
                        "Quel niveau de détail est attendu ?",
                    ],
                },
                {
                    "title": "Prochaines étapes",
                    "content": [
                        "Valider la structure du document.",
                        "Compléter les zones encore incomplètes.",
                        "Publier dans l'outil cible après validation.",
                    ],
                },
            ],
            "detected_type": classification["request_type"],
        }

    def _build_title(self, user_input: str) -> str:
        short_text = user_input.strip()
        if len(short_text) > 60:
            short_text = short_text[:57] + "..."
        return f"Draft documentation - {short_text}"
