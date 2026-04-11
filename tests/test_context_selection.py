from app.services.context_selection import ContextSelectionPolicy


def test_context_selection_uses_context_for_analysis_with_business_anchor() -> None:
    policy = ContextSelectionPolicy()

    decision = policy.should_use_context(
        user_input="La remise ne se calcule plus sur certaines commandes web.",
        workflow="analysis",
        target_output="analysis",
        request_type="analysis",
    )

    assert decision is True


def test_context_selection_skips_context_for_generic_analysis_without_anchor() -> None:
    policy = ContextSelectionPolicy()

    decision = policy.should_use_context(
        user_input="Sujet flou a clarifier avec le metier.",
        workflow="analysis",
        target_output="analysis",
        request_type="analysis",
    )

    assert decision is False


def test_context_selection_skips_context_for_clear_direct_ticket() -> None:
    policy = ContextSelectionPolicy()

    decision = policy.should_use_context(
        user_input="Bug paiement en production, erreur bloquante.",
        workflow="ticket",
        target_output="ticket",
        request_type="bug",
        analyze_then_ticket=False,
    )

    assert decision is False
