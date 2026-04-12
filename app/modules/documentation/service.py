import json
import logging
import re

from app.schemas.analysis import AnalysisResult
from app.schemas.confluence_result import ConfluencePageResult
from app.schemas.documentation import DocumentationResult
from app.schemas.jira_result import JiraIssueResult
from app.schemas.source_summary import SourceSummaryResult
from app.services.llm.provider import LLMProvider
from app.services.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

_DOCUMENTATION_SYSTEM = (
    "Tu es un assistant Product Owner expert. "
    "Tu produis des documents de travail structurés en JSON. "
    "Réponds UNIQUEMENT avec un objet JSON valide, sans texte supplémentaire, sans bloc de code markdown."
)


def _strip_code_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


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
        llm_provider: LLMProvider | None = None,
    ) -> DocumentationResult:
        if llm_provider is not None:
            try:
                return self._run_with_llm(user_input, context_hint, classification, llm_provider)
            except Exception as exc:
                logger.warning("LLM documentation.run failed, falling back to deterministic: %s", exc)
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

    def _run_with_llm(
        self,
        user_input: str,
        context_hint: str | None,
        classification: dict,
        llm_provider: LLMProvider,
    ) -> DocumentationResult:
        prompt = prompt_manager.render(
            "documentation",
            {
                "user_input": user_input,
                "context_hint": context_hint,
                "request_type": classification["request_type"],
            },
        )
        raw = llm_provider.generate(prompt, system=_DOCUMENTATION_SYSTEM, workflow="documentation")
        data = json.loads(_strip_code_block(raw))
        self._normalize_doc_json(data, classification["request_type"])
        return DocumentationResult(**data)

    def from_analysis(self, analysis: AnalysisResult, llm_provider: LLMProvider | None = None) -> DocumentationResult:
        if llm_provider is not None:
            try:
                return self._from_analysis_with_llm(analysis, llm_provider)
            except Exception as exc:
                logger.warning("LLM documentation.from_analysis failed, falling back to deterministic: %s", exc)
        return DocumentationResult(
            document_type="working_draft",
            title=self._build_title(analysis.reformulation),
            summary="Document de travail derive d'une analyse existante.",
            context=analysis.context_hint or "Contexte complementaire non fourni.",
            sections=[
                {
                    "title": "Contexte",
                    "content": analysis.context_hint or analysis.reformulation,
                },
                {
                    "title": "Objectif",
                    "content": analysis.expected_behavior or analysis.reformulation,
                },
                {
                    "title": "Points cles",
                    "content": analysis.business_impacts + analysis.technical_impacts or [analysis.request_summary],
                },
                {
                    "title": "Questions ouvertes",
                    "content": analysis.open_questions or analysis.ambiguities,
                },
                {
                    "title": "Prochaines etapes",
                    "content": [analysis.recommended_next_step],
                },
            ],
            detected_type=analysis.detected_type,
        )

    def _normalize_doc_json(self, data: dict, request_type: str) -> None:
        """In-place normalization of LLM-produced documentation JSON to match DocumentationResult schema."""
        data.pop("result_type", None)
        for str_field in ("title", "summary", "document_type"):
            if not data.get(str_field):
                data[str_field] = ""
        if not data.get("context"):
            data["context"] = ""
        if not data.get("detected_type"):
            data["detected_type"] = request_type
        if not isinstance(data.get("sections"), list):
            data["sections"] = []

    def _from_analysis_with_llm(self, analysis: AnalysisResult, llm_provider: LLMProvider) -> DocumentationResult:
        prompt = prompt_manager.render(
            "documentation",
            {
                "user_input": analysis.reformulation,
                "context_hint": analysis.context_hint,
                "request_type": analysis.detected_type,
            },
        )
        raw = llm_provider.generate(prompt, system=_DOCUMENTATION_SYSTEM, workflow="documentation")
        data = json.loads(_strip_code_block(raw))
        self._normalize_doc_json(data, analysis.detected_type)
        return DocumentationResult(**data)

    def from_source_summary(self, source_summary: SourceSummaryResult) -> DocumentationResult:
        return DocumentationResult(
            document_type="working_draft",
            title=self._build_title(source_summary.source_title or source_summary.source_ref),
            summary="Document de travail derive d'un resume de source.",
            context=f"Source initiale: {source_summary.source_ref}",
            sections=[
                {
                    "title": "Contexte",
                    "content": source_summary.source_title or source_summary.source_ref,
                },
                {
                    "title": "Objectif",
                    "content": source_summary.summary,
                },
                {
                    "title": "Points cles",
                    "content": source_summary.key_points or [source_summary.summary],
                },
                {
                    "title": "Questions ouvertes",
                    "content": source_summary.open_questions or ["Quels points de la source doivent encore etre confirmes ?"],
                },
                {
                    "title": "Prochaines etapes",
                    "content": [source_summary.next_step_hint],
                },
            ],
            detected_type="source_summary",
        )

    def from_jira_issue(self, jira_issue: JiraIssueResult) -> DocumentationResult:
        return DocumentationResult(
            document_type="working_draft",
            title=self._build_title(f"{jira_issue.issue_key} - {jira_issue.title}"),
            summary="Document de travail derive d'un ticket Jira lu en readonly.",
            context=f"Ticket Jira lu: {jira_issue.issue_key}",
            sections=[
                {
                    "title": "Contexte",
                    "content": jira_issue.url or jira_issue.issue_key,
                },
                {
                    "title": "Objectif",
                    "content": jira_issue.title,
                },
                {
                    "title": "Points cles",
                    "content": [
                        item
                        for item in [
                            f"Statut: {jira_issue.status}" if jira_issue.status else None,
                            f"Type: {jira_issue.issue_type}" if jira_issue.issue_type else None,
                            f"Priorite: {jira_issue.priority}" if jira_issue.priority else None,
                            f"Labels: {', '.join(jira_issue.labels)}" if jira_issue.labels else None,
                            jira_issue.description,
                        ]
                        if item
                    ]
                    or [jira_issue.summary],
                },
                {
                    "title": "Questions ouvertes",
                    "content": jira_issue.open_points or ["Quels elements du ticket Jira doivent encore etre clarifies ?"],
                },
                {
                    "title": "Prochaines etapes",
                    "content": ["Clarifier le besoin attendu puis transformer ce ticket Jira en analyse ou draft exploitable."],
                },
            ],
            detected_type="jira_read",
        )

    def from_confluence_page(self, page: ConfluencePageResult) -> DocumentationResult:
        return DocumentationResult(
            document_type="working_draft",
            title=self._build_title(page.title),
            summary="Document de travail derive d'une page Confluence.",
            context=f"Page Confluence lue: {page.page_id}",
            sections=[
                {
                    "title": "Contexte",
                    "content": page.url or page.page_id,
                },
                {
                    "title": "Objectif",
                    "content": page.title,
                },
                {
                    "title": "Points cles",
                    "content": page.key_points or [page.summary],
                },
                {
                    "title": "Questions ouvertes",
                    "content": page.open_points or ["Quels elements de la page Confluence doivent encore etre clarifies ?"],
                },
                {
                    "title": "Prochaines etapes",
                    "content": ["Clarifier le besoin attendu puis transformer cette page en analyse ou draft exploitable."],
                },
            ],
            detected_type="confluence_read",
        )

    def _build_title(self, user_input: str) -> str:
        short_text = user_input.strip()
        if len(short_text) > 60:
            short_text = short_text[:57] + "..."
        return f"Documentation de travail - {short_text}"
