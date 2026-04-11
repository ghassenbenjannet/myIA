from app.schemas.documentation import DocumentationResult


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
    ) -> DocumentationResult:
        return DocumentationResult(
            document_type="working_draft",
            title=self._build_title(user_input),
            summary="Draft de documentation structure a partir de la demande fournie.",
            context=context_hint or "No additional context provided.",
            sections=[
                {
                    "title": "Contexte",
                    "content": user_input,
                },
                {
                    "title": "Points cles",
                    "content": "A completer ou affiner lors de la validation metier.",
                },
                {
                    "title": "Questions ouvertes",
                    "content": [
                        "Quels elements doivent etre documentes en priorite ?",
                        "Quel est le public cible de cette documentation ?",
                        "Quel niveau de detail est attendu ?",
                    ],
                },
                {
                    "title": "Prochaines etapes",
                    "content": [
                        "Valider la structure du document.",
                        "Completer les zones encore incompletes.",
                        "Publier dans l'outil cible apres validation.",
                    ],
                },
            ],
            detected_type=classification["request_type"],
        )

    def _build_title(self, user_input: str) -> str:
        short_text = user_input.strip()
        if len(short_text) > 60:
            short_text = short_text[:57] + "..."
        return f"Draft documentation - {short_text}"
