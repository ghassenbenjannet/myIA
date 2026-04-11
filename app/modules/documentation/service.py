from app.schemas.analysis import AnalysisResult
from app.schemas.documentation import DocumentationResult
from app.schemas.jira_result import JiraIssueResult
from app.schemas.source_summary import SourceSummaryResult


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

    def from_analysis(self, analysis: AnalysisResult) -> DocumentationResult:
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

    def _build_title(self, user_input: str) -> str:
        short_text = user_input.strip()
        if len(short_text) > 60:
            short_text = short_text[:57] + "..."
        return f"Documentation de travail - {short_text}"
