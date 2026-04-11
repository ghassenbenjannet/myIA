from app.schemas.context import ContextUsed


class ReadOnlyContextProvider:
    """
    Minimal readonly context provider.

    This is a deterministic stub that simulates targeted knowledge retrieval
    for a few known business topics.
    """

    def fetch(
        self,
        user_input: str,
        context_hint: str | None,
        request_type: str | None = None,
    ) -> ContextUsed | None:
        lowered = self._normalize(f"{user_input} {context_hint or ''}")

        if any(keyword in lowered for keyword in ("remise", "facturation", "commande")):
            return ContextUsed(
                source_name="stub_confluence",
                summary="Contexte documentaire simulé sur les regles de commande, remise et facturation.",
                snippets=[
                    "Les remises doivent respecter les regles de calcul validees par le metier.",
                    "Les traitements batch et les commandes web doivent rester coherents sur les cas standards.",
                ],
                confidence_hint=0.72,
            )

        return None

    def _normalize(self, value: str) -> str:
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
