from app.schemas.documentation import DocumentationResult


class DocumentationService:
    """
    Documentation draft generator for the MVP.
    Produces a compact working document from raw notes or requests.
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
            summary="Document de travail structure a partir de la demande fournie.",
            context=context_hint or "Contexte complementaire non fourni.",
            sections=[
                {
                    "title": "Contexte",
                    "content": context_hint or user_input,
                },
                {
                    "title": "Objectif",
                    "content": user_input,
                },
                {
                    "title": "Points cles",
                    "content": [
                        "Verifier les regles ou decisions a documenter.",
                        "Completer les informations encore implicites.",
                    ],
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
        return f"Documentation de travail - {short_text}"
