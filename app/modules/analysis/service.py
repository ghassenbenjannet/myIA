import json
import logging
import re

from app.schemas.analysis import AnalysisResult
from app.schemas.confluence_result import ConfluencePageResult
from app.schemas.jira_result import JiraIssueResult
from app.schemas.source_summary import SourceSummaryResult
from app.services.llm.provider import LLMProvider
from app.services.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

_ANALYSIS_SYSTEM = (
    "Tu es un assistant Product Owner expert. "
    "Tu analyses des demandes métier et produis des analyses PO structurées en JSON. "
    "Réponds UNIQUEMENT avec un objet JSON valide, sans texte supplémentaire, sans bloc de code markdown."
)


def _strip_code_block(text: str) -> str:
    """Remove markdown code fences that some models add despite instructions."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


class AnalysisService:
    """
    Deterministic analysis service for the MVP.

    The goal is to produce a compact, PO-oriented analysis without
    introducing NLP or external dependencies.
    """

    TECHNICAL_KEYWORDS = {
        "api": "Des interfaces API peuvent etre impactees.",
        "batch": "Des traitements batch peuvent devoir etre verifies.",
        "import": "Les flux d'import peuvent etre affectes.",
        "flux": "Des flux inter-applications doivent etre verifies.",
        "interface": "Les interfaces entre systemes doivent etre controlees.",
        "legacy": "Le patrimoine legacy peut complexifier la correction.",
    }

    DEPENDENCY_KEYWORDS = {
        "api": "Verifier les API ou services exposes.",
        "batch": "Verifier les traitements batch concernes.",
        "import": "Verifier les flux d'import concernes.",
        "flux": "Verifier les flux applicatifs ou echanges de donnees.",
        "commande": "Verifier les objets de gestion lies aux commandes.",
        "facturation": "Verifier les regles et objets de facturation.",
        "paiement": "Verifier les composants ou flux de paiement.",
    }

    BUSINESS_KEYWORDS = {
        "utilisateur": "Le parcours utilisateur peut etre degrade.",
        "client": "La satisfaction client peut etre impactee.",
        "commande": "Le traitement des commandes peut etre bloque ou incorrect.",
        "facturation": "La facturation peut devenir erronee ou incomplete.",
        "remise": "Le calcul des remises peut etre incorrect.",
        "metier": "Des regles metier peuvent etre mal appliquees.",
        "paiement": "Le parcours de paiement peut etre degrade.",
    }

    CURRENT_BEHAVIOR_HINTS = (
        "ne se calcule plus",
        "ne fonctionne plus",
        "erreur",
        "incident",
        "anomalie",
        "ko",
        "bloque",
        "bloquante",
        "echoue",
    )

    EXPECTED_BEHAVIOR_HINTS = (
        "doit",
        "attendu",
        "souhaite",
        "devrait",
        "permettre",
        "afin de",
    )

    def run(
        self,
        user_input: str,
        context_hint: str | None,
        classification: dict,
        llm_provider: LLMProvider | None = None,
    ) -> AnalysisResult:
        if llm_provider is not None:
            try:
                return self._run_with_llm(user_input, context_hint, classification, llm_provider)
            except Exception as exc:
                logger.warning("LLM analysis failed, falling back to deterministic: %s", exc)
        lowered = self._normalize(user_input)

        current_behavior = self._extract_current_behavior(user_input, lowered)
        expected_behavior = self._extract_expected_behavior(user_input, lowered)
        business_impacts = self._extract_impacts(lowered, self.BUSINESS_KEYWORDS)
        technical_impacts = self._extract_impacts(lowered, self.TECHNICAL_KEYWORDS)
        dependencies = self._extract_dependencies(lowered)
        ambiguities = self._extract_ambiguities(
            lowered=lowered,
            current_behavior=current_behavior,
            expected_behavior=expected_behavior,
            business_impacts=business_impacts,
        )
        risks = self._extract_risks(lowered, business_impacts, technical_impacts, dependencies)
        open_questions = self._extract_open_questions(
            lowered=lowered,
            current_behavior=current_behavior,
            expected_behavior=expected_behavior,
            dependencies=dependencies,
        )
        recommended_output = self._recommend_output(lowered, expected_behavior)

        return AnalysisResult(
            reformulation=self._build_reformulation(
                user_input=user_input,
                current_behavior=current_behavior,
                expected_behavior=expected_behavior,
            ),
            request_summary=self._build_request_summary(
                current_behavior=current_behavior,
                expected_behavior=expected_behavior,
                business_impacts=business_impacts,
                technical_impacts=technical_impacts,
                dependencies=dependencies,
            ),
            context_hint=context_hint,
            detected_type=classification["request_type"],
            current_behavior=current_behavior,
            expected_behavior=expected_behavior,
            business_impacts=business_impacts,
            technical_impacts=technical_impacts,
            dependencies=dependencies,
            ambiguities=ambiguities,
            risks=risks,
            open_questions=open_questions,
            recommended_next_step=self._build_recommended_next_step(
                ambiguities=ambiguities,
                recommended_output=recommended_output,
            ),
            recommended_output=recommended_output,
        )

    def _run_with_llm(
        self,
        user_input: str,
        context_hint: str | None,
        classification: dict,
        llm_provider: LLMProvider,
    ) -> AnalysisResult:
        prompt = prompt_manager.render(
            "analysis",
            {
                "user_input": user_input,
                "context_hint": context_hint,
                "request_type": classification["request_type"],
            },
        )
        raw = llm_provider.generate(prompt, system=_ANALYSIS_SYSTEM, workflow="analysis")
        data = json.loads(_strip_code_block(raw))
        # Fields with defaults or set externally are not expected from LLM JSON
        data.pop("result_type", None)
        data.setdefault("detected_type", classification["request_type"])
        data.setdefault("context_hint", context_hint)
        # Ensure list fields are always lists
        for field in ("business_impacts", "technical_impacts", "dependencies", "ambiguities", "risks", "open_questions"):
            if not isinstance(data.get(field), list):
                data[field] = []
        return AnalysisResult(**data)

    def from_source_summary(self, source_summary: SourceSummaryResult) -> AnalysisResult:
        source_text = self._build_source_text(source_summary)
        lowered = self._normalize(source_text)
        business_impacts = self._extract_impacts(lowered, self.BUSINESS_KEYWORDS)
        technical_impacts = self._extract_impacts(lowered, self.TECHNICAL_KEYWORDS)
        dependencies = self._extract_dependencies(lowered)
        open_questions = list(source_summary.open_questions)
        if not open_questions:
            open_questions.append("Quels elements de la source doivent etre confirmes avec le metier ?")

        risks = ["Risque de mauvaise interpretation si la source ne couvre pas tout le perimetre."]
        if technical_impacts:
            risks.append("Risque de regression technique si les dependances issues de la source ne sont pas verifiees.")
        if business_impacts:
            risks.append("Risque d'impact metier si la source est incomplete ou datee.")

        return AnalysisResult(
            reformulation=self._build_source_reformulation(source_summary),
            request_summary=source_summary.summary,
            context_hint=f"Source initiale: {source_summary.source_ref}",
            detected_type="analysis",
            current_behavior=self._extract_source_current_behavior(source_summary),
            expected_behavior=None,
            business_impacts=business_impacts,
            technical_impacts=technical_impacts,
            dependencies=dependencies,
            ambiguities=[
                "Le comportement attendu n'est pas formule clairement dans la source.",
            ],
            risks=risks,
            open_questions=open_questions,
            recommended_next_step=source_summary.next_step_hint,
            recommended_output="analysis",
        )

    def from_confluence_page(self, page: ConfluencePageResult) -> AnalysisResult:
        page_text = self._build_confluence_text(page)
        lowered = self._normalize(page_text)
        business_impacts = self._extract_impacts(lowered, self.BUSINESS_KEYWORDS)
        technical_impacts = self._extract_impacts(lowered, self.TECHNICAL_KEYWORDS)
        dependencies = self._extract_dependencies(lowered)
        open_questions = list(page.open_points)
        if not open_questions:
            open_questions.append("Quels points de la page Confluence doivent encore etre confirmes avec le metier ?")

        ambiguities = ["Le comportement attendu n'est pas explicite dans la page Confluence."]
        if not page.content_preview:
            ambiguities.append("Le contenu de la page Confluence est partiellement disponible.")

        risks = ["Risque de mauvaise interpretation si la page Confluence ne couvre pas tout le perimetre."]
        if technical_impacts:
            risks.append("Risque de regression technique si les dependances identifiees ne sont pas verifiees.")
        if business_impacts:
            risks.append("Risque d'impact metier si la page Confluence est incomplete ou datee.")

        return AnalysisResult(
            reformulation=f"La page Confluence '{page.title}' porte sur un sujet a analyser avant transformation en livrable.",
            request_summary=page.summary,
            context_hint=f"Page Confluence lue: {page.page_id}",
            detected_type="analysis",
            current_behavior=self._extract_confluence_current_behavior(page),
            expected_behavior=None,
            business_impacts=business_impacts,
            technical_impacts=technical_impacts,
            dependencies=dependencies,
            ambiguities=ambiguities,
            risks=risks,
            open_questions=open_questions,
            recommended_next_step="Clarifier le besoin attendu puis transformer cette analyse en ticket ou documentation selon le besoin.",
            recommended_output="analysis",
        )

    def from_jira_issue(self, jira_issue: JiraIssueResult) -> AnalysisResult:
        issue_text = self._build_jira_text(jira_issue)
        lowered = self._normalize(issue_text)
        business_impacts = self._extract_impacts(lowered, self.BUSINESS_KEYWORDS)
        technical_impacts = self._extract_impacts(lowered, self.TECHNICAL_KEYWORDS)
        dependencies = self._extract_dependencies(lowered)
        open_questions = list(jira_issue.open_points)
        if not open_questions:
            open_questions.append("Quels points du ticket Jira doivent encore etre confirmes avec le metier ?")

        ambiguities = ["Le comportement attendu n'est pas explicite dans le ticket Jira."]
        if not jira_issue.description:
            ambiguities.append("La description Jira reste trop courte pour cadrer completement le sujet.")

        risks = ["Risque de mauvaise interpretation si le ticket Jira ne couvre pas tout le besoin."]
        if technical_impacts:
            risks.append("Risque de regression technique si les dependances mentionnees par Jira ne sont pas verifiees.")
        if business_impacts:
            risks.append("Risque d'impact metier si le ticket Jira reste incomplet.")

        return AnalysisResult(
            reformulation=f"Le ticket Jira {jira_issue.issue_key} porte sur {jira_issue.title.lower()} et doit etre analyse avant transformation en livrable.",
            request_summary=jira_issue.summary,
            context_hint=f"Ticket Jira lu: {jira_issue.issue_key}",
            detected_type="analysis",
            current_behavior=self._extract_jira_current_behavior(jira_issue),
            expected_behavior=None,
            business_impacts=business_impacts,
            technical_impacts=technical_impacts,
            dependencies=dependencies,
            ambiguities=ambiguities,
            risks=risks,
            open_questions=open_questions,
            recommended_next_step="Clarifier le besoin attendu puis transformer cette analyse en ticket ou documentation selon le besoin.",
            recommended_output="analysis",
        )

    def _build_confluence_text(self, page: ConfluencePageResult) -> str:
        return " ".join(
            [
                page.title,
                page.summary,
                page.content_preview or "",
                *page.key_points,
                *page.open_points,
            ]
        ).strip()

    def _extract_confluence_current_behavior(self, page: ConfluencePageResult) -> str | None:
        if page.key_points:
            return f"Point cle issu de Confluence: {page.key_points[0]}"
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

    def _build_reformulation(
        self,
        user_input: str,
        current_behavior: str | None,
        expected_behavior: str | None,
    ) -> str:
        topic = self._short_subject(user_input)
        if current_behavior and expected_behavior:
            return f"Le sujet porte sur {topic}, avec un comportement observe a investiguer et un comportement cible a cadrer."
        if current_behavior:
            return f"Le sujet porte sur {topic}, avec un comportement observe a investiguer."
        if expected_behavior:
            return f"Le sujet porte sur {topic}, avec un comportement cible ou un besoin a cadrer."
        return f"Le sujet porte sur {topic} et doit etre clarifie avant transformation en livrable actionnable."

    def _short_subject(self, user_input: str) -> str:
        subject = user_input.strip()
        prefixes = (
            "le metier dit que ",
            "peux-tu regarder ",
            "peux tu regarder ",
            "sujet ",
        )
        lowered = self._normalize(subject)
        for prefix in prefixes:
            if lowered.startswith(prefix):
                subject = subject[len(prefix):].strip()
                break

        if len(subject) > 90:
            subject = subject[:87].rstrip() + "..."

        return subject.lower()

    def _build_source_text(self, source_summary: SourceSummaryResult) -> str:
        return " ".join(
            [
                source_summary.source_title or "",
                source_summary.summary,
                *source_summary.key_points,
                *source_summary.open_questions,
            ]
        ).strip()

    def _build_source_reformulation(self, source_summary: SourceSummaryResult) -> str:
        source_label = source_summary.source_title or source_summary.source_ref
        return f"La source {source_label} met en avant un sujet a analyser avant de produire un livrable."

    def _build_jira_text(self, jira_issue: JiraIssueResult) -> str:
        return " ".join(
            [
                jira_issue.title,
                jira_issue.description or "",
                jira_issue.summary,
                jira_issue.status or "",
                jira_issue.issue_type or "",
                jira_issue.priority or "",
                *jira_issue.labels,
                *jira_issue.open_points,
            ]
        ).strip()

    def _extract_source_current_behavior(
        self,
        source_summary: SourceSummaryResult,
    ) -> str | None:
        if source_summary.key_points:
            return f"Comportement observe dans la source: {source_summary.key_points[0]}"
        return None

    def _extract_jira_current_behavior(self, jira_issue: JiraIssueResult) -> str | None:
        if jira_issue.description:
            return f"Comportement observe dans Jira: {jira_issue.description}"
        return f"Comportement observe dans Jira: {jira_issue.title}"

    def _build_request_summary(
        self,
        current_behavior: str | None,
        expected_behavior: str | None,
        business_impacts: list[str],
        technical_impacts: list[str],
        dependencies: list[str],
    ) -> str:
        parts = ["Analyse PO preliminaire."]
        if current_behavior:
            parts.append("Le comportement actuel est partiellement decrit.")
        if expected_behavior:
            parts.append("Le comportement attendu est partiellement decrit.")
        if business_impacts:
            parts.append("Des impacts metier ont ete identifies.")
        if technical_impacts:
            parts.append("Des impacts techniques ont ete identifies.")
        if dependencies:
            parts.append("Des dependances sont a verifier.")
        return " ".join(parts)

    def _extract_current_behavior(self, user_input: str, lowered: str) -> str | None:
        if any(hint in lowered for hint in self.CURRENT_BEHAVIOR_HINTS):
            return f"Comportement observe: {user_input.strip()}"
        return None

    def _extract_expected_behavior(self, user_input: str, lowered: str) -> str | None:
        if any(hint in lowered for hint in self.EXPECTED_BEHAVIOR_HINTS):
            return f"Comportement cible a confirmer: {user_input.strip()}"
        return None

    def _extract_impacts(self, lowered: str, mapping: dict[str, str]) -> list[str]:
        impacts: list[str] = []
        for keyword, message in mapping.items():
            if keyword in lowered and message not in impacts:
                impacts.append(message)
        return impacts

    def _extract_dependencies(self, lowered: str) -> list[str]:
        dependencies: list[str] = []
        for keyword, message in self.DEPENDENCY_KEYWORDS.items():
            if keyword in lowered and message not in dependencies:
                dependencies.append(message)
        return dependencies

    def _extract_ambiguities(
        self,
        lowered: str,
        current_behavior: str | None,
        expected_behavior: str | None,
        business_impacts: list[str],
    ) -> list[str]:
        ambiguities: list[str] = []

        if "a confirmer" in lowered or "on ne sait pas" in lowered or "a clarifier" in lowered:
            ambiguities.append("Le perimetre exact ou certaines hypotheses restent a confirmer.")
        if current_behavior is None:
            ambiguities.append("Le comportement actuel n'est pas suffisamment explicite.")
        if expected_behavior is None:
            ambiguities.append("Le comportement attendu n'est pas formule clairement.")
        if not business_impacts:
            ambiguities.append("Les impacts metier concrets restent a preciser.")

        return ambiguities

    def _extract_risks(
        self,
        lowered: str,
        business_impacts: list[str],
        technical_impacts: list[str],
        dependencies: list[str],
    ) -> list[str]:
        risks = ["Risque de mauvaise priorisation si le besoin reste insuffisamment cadre."]

        if technical_impacts:
            risks.append("Risque de regression technique si les composants impactes ne sont pas identifies.")
        if business_impacts:
            risks.append("Risque d'impact metier si le comportement cible n'est pas valide.")
        if dependencies:
            risks.append("Risque d'oublier un systeme ou flux dependant lors de la mise en oeuvre.")
        if self._mentions_production(lowered):
            risks.append("Risque operationnel plus eleve si le sujet concerne deja la production.")

        return risks

    def _extract_open_questions(
        self,
        lowered: str,
        current_behavior: str | None,
        expected_behavior: str | None,
        dependencies: list[str],
    ) -> list[str]:
        questions: list[str] = []

        if current_behavior is None:
            questions.append("Quel est le comportement actuel observe de facon factuelle ?")
        if expected_behavior is None:
            questions.append("Quel est le comportement cible attendu par le metier ?")
        questions.append("Quel est le perimetre exact du sujet et des cas concernes ?")

        if dependencies:
            questions.append("Quels systemes, flux ou objets dependants doivent etre verifies ?")
        if "utilisateur" in lowered or "client" in lowered:
            questions.append("Quel est l'impact concret pour l'utilisateur ou le client final ?")
        if self._mentions_production(lowered):
            questions.append("Le sujet est-il reproductible et quantifie en production ?")

        return questions

    def _recommend_output(self, lowered: str, expected_behavior: str | None) -> str:
        if "documentation" in lowered or "documenter" in lowered:
            return "documentation"
        if "recette" in lowered or "test" in lowered:
            return "recipe"
        if expected_behavior is not None or "bug" in lowered or "erreur" in lowered or "evolution" in lowered:
            return "ticket"
        return "analysis"

    def _build_recommended_next_step(
        self,
        ambiguities: list[str],
        recommended_output: str,
    ) -> str:
        if ambiguities:
            return (
                "Clarifier les zones d'incertitude, valider le comportement attendu et confirmer le perimetre "
                f"avant de produire un livrable de type {recommended_output}."
            )
        if recommended_output == "ticket":
            return "Transformer cette analyse en draft ticket avec description, impacts et criteres d'acceptation."
        if recommended_output == "documentation":
            return "Transformer cette analyse en draft de documentation de travail."
        if recommended_output == "recipe":
            return "Transformer cette analyse en draft de recette avec cas de test cibles."
        return "Completer l'analyse avec les parties prenantes avant de decider du livrable suivant."

    def _mentions_production(self, lowered: str) -> bool:
        tokens = lowered.replace(":", " ").replace(",", " ").replace(".", " ").split()
        return "prod" in tokens or "production" in tokens
