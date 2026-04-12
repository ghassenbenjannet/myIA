import json

from app.services.llm.provider import LLMProvider

_STUB_ANALYSIS = {
    "reformulation": "[Stub LLM] Reformulation à générer avec le modèle Claude réel.",
    "request_summary": "Résumé produit par le stub LLM — activez ANTHROPIC_API_KEY pour une analyse réelle.",
    "current_behavior": "Comportement actuel à décrire dans le contexte réel.",
    "expected_behavior": "Comportement attendu à valider avec le métier.",
    "business_impacts": [
        "Impact métier à compléter avec le modèle réel.",
    ],
    "technical_impacts": [],
    "dependencies": [],
    "ambiguities": [
        "Le périmètre exact reste à confirmer — stub actif.",
    ],
    "risks": [
        "Résultat généré par le stub LLM — activer l'API Claude pour une analyse réelle.",
    ],
    "open_questions": [
        "Quel est le comportement cible attendu par le métier ?",
        "Quels systèmes dépendants sont concernés ?",
    ],
    "recommended_output": "ticket",
    "recommended_next_step": "Configurer ANTHROPIC_API_KEY et LLM_ENABLED=true pour activer le mode assisté réel.",
}

_STUB_TICKET = {
    "title": "[Stub LLM] Titre à générer avec le modèle Claude réel",
    "ticket_type": "story",
    "context": "Contexte généré par le stub LLM.",
    "business_goal": "En tant qu'utilisateur, je souhaite que le comportement attendu soit correct.",
    "description": "Description générée par le stub LLM — activez ANTHROPIC_API_KEY pour un résultat réel.",
    "current_behavior": None,
    "expected_behavior": None,
    "business_impacts": [],
    "technical_impacts": [],
    "dependencies": [],
    "open_points": [
        "Ce ticket est généré par le stub — activez l'API Claude pour un résultat réel.",
    ],
    "acceptance_criteria": [
        "Le comportement attendu est conforme à la description.",
        "Les cas limites ont été validés avec le métier.",
    ],
}

_STUB_DOCUMENTATION = {
    "title": "Documentation de travail — Stub LLM",
    "document_type": "working_draft",
    "summary": "Document généré par le stub LLM — activez ANTHROPIC_API_KEY pour un résultat réel.",
    "context": None,
    "sections": [
        {"title": "Contexte", "content": "Contexte à compléter avec le modèle Claude réel."},
        {"title": "Objectif", "content": "Objectif à définir avec le modèle Claude réel."},
        {
            "title": "Points clés",
            "content": ["Point clé à compléter.", "Activer l'API Claude pour un contenu réel."],
        },
        {
            "title": "Questions ouvertes",
            "content": ["Stub actif — configurer LLM_ENABLED=true et ANTHROPIC_API_KEY."],
        },
        {
            "title": "Prochaines étapes",
            "content": ["Activer le modèle LLM et relancer l'analyse."],
        },
    ],
    "detected_type": "stub",
}


class StubLLMProvider(LLMProvider):
    """Stub provider for development and CI without API credentials.

    Returns valid-schema JSON for each workflow so the full LLM code path
    can be exercised without calling the real API.
    """

    @property
    def name(self) -> str:
        return "stub"

    @property
    def is_available(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        workflow: str | None = None,
    ) -> str:
        if workflow == "ticket":
            return json.dumps(_STUB_TICKET, ensure_ascii=False)
        if workflow == "documentation":
            return json.dumps(_STUB_DOCUMENTATION, ensure_ascii=False)
        return json.dumps(_STUB_ANALYSIS, ensure_ascii=False)
