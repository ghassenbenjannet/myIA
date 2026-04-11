class ContextSelectionPolicy:
    """
    Minimal policy deciding whether readonly external context should be loaded.

    The rules are intentionally compact and deterministic:
    use context only for analysis-oriented flows and only when a business topic
    covered by the provider is present.
    """

    BUSINESS_ANCHORS = ("remise", "facturation", "commande", "paiement")
    FUZZY_HINTS = (
        "on ne sait pas",
        "a confirmer",
        "a clarifier",
        "à confirmer",
        "à clarifier",
        "probleme",
        "problème",
        "sujet",
    )

    def should_use_context(
        self,
        user_input: str,
        workflow: str,
        target_output: str,
        request_type: str,
        analyze_then_ticket: bool = False,
    ) -> bool:
        lowered = self._normalize(user_input)
        has_business_anchor = any(anchor in lowered for anchor in self.BUSINESS_ANCHORS)

        if not has_business_anchor:
            return False

        if workflow == "documentation":
            return False

        if workflow == "analysis":
            return True

        if workflow == "ticket" and analyze_then_ticket:
            return request_type == "analysis" or any(hint in lowered for hint in self.FUZZY_HINTS)

        if target_output == "ticket":
            return False

        return False

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
