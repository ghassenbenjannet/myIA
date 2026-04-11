from app.schemas.analysis import AnalysisResult
from app.schemas.ticket import TicketResult


class TicketService:
    """
    Deterministic ticket draft generator for the MVP.

    The ticket stays compact and honest: when the input is too poor, the service
    raises open points instead of inventing details.
    """

    TECHNICAL_KEYWORDS = {
        "api": "Des interfaces API peuvent etre impactees.",
        "batch": "Des traitements batch peuvent etre impactes.",
        "import": "Des flux d'import peuvent etre impactes.",
        "flux": "Des flux applicatifs ou echanges de donnees peuvent etre impactes.",
        "interface": "Des interfaces entre systemes peuvent etre impactees.",
    }

    DEPENDENCY_KEYWORDS = {
        "api": "Verifier les API ou services exposes.",
        "batch": "Verifier les traitements batch concernes.",
        "import": "Verifier les flux d'import concernes.",
        "flux": "Verifier les flux applicatifs ou echanges de donnees.",
        "interface": "Verifier les interfaces entre systemes concernes.",
        "commande": "Verifier les objets de gestion lies aux commandes.",
        "facturation": "Verifier les regles et objets de facturation.",
        "remise": "Verifier les regles de calcul de remise.",
        "paiement": "Verifier les composants ou flux de paiement.",
    }

    BUSINESS_KEYWORDS = {
        "utilisateur": "Le parcours utilisateur peut etre degrade.",
        "client": "La satisfaction client peut etre impactee.",
        "commande": "Le traitement des commandes peut etre bloque ou incorrect.",
        "facturation": "La facturation peut devenir erronee ou incomplete.",
        "remise": "Le calcul des remises peut etre incorrect.",
        "paiement": "Le parcours de paiement peut etre degrade.",
        "metier": "Des regles metier peuvent etre mal appliquees.",
    }

    CURRENT_BEHAVIOR_HINTS = (
        "bug",
        "erreur",
        "incident",
        "anomalie",
        "ko",
        "ne fonctionne plus",
        "ne se calcule plus",
        "bloque",
        "bloquante",
        "production",
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
    ) -> TicketResult:
        request_type = classification["request_type"]
        lowered = self._normalize(user_input)

        current_behavior = self._extract_current_behavior(user_input, lowered, request_type)
        expected_behavior = self._extract_expected_behavior(user_input, lowered)
        business_impacts = self._extract_messages(lowered, self.BUSINESS_KEYWORDS)
        technical_impacts = self._extract_messages(lowered, self.TECHNICAL_KEYWORDS)
        dependencies = self._extract_messages(lowered, self.DEPENDENCY_KEYWORDS)
        open_points = self._build_open_points(
            lowered=lowered,
            current_behavior=current_behavior,
            expected_behavior=expected_behavior,
            business_impacts=business_impacts,
            dependencies=dependencies,
        )

        return TicketResult(
            ticket_type=self._map_ticket_type(request_type),
            title=self._build_title(request_type, user_input, current_behavior, expected_behavior),
            description=self._build_description(
                user_input=user_input,
                request_type=request_type,
                current_behavior=current_behavior,
                expected_behavior=expected_behavior,
                business_impacts=business_impacts,
                technical_impacts=technical_impacts,
            ),
            context=self._build_context(context_hint, request_type, classification["confidence"]),
            current_behavior=current_behavior,
            expected_behavior=expected_behavior,
            business_goal=self._build_business_goal(request_type, business_impacts, expected_behavior),
            business_impacts=business_impacts,
            technical_impacts=technical_impacts,
            dependencies=dependencies,
            open_points=open_points,
            acceptance_criteria=self._build_acceptance_criteria(
                request_type=request_type,
                current_behavior=current_behavior,
                expected_behavior=expected_behavior,
                dependencies=dependencies,
                open_points=open_points,
            ),
        )

    def from_analysis(self, analysis: AnalysisResult) -> TicketResult:
        ticket_type = self._map_analysis_output_to_ticket_type(analysis.recommended_output)
        title = self._build_title_from_analysis(analysis)
        description = self._build_description_from_analysis(analysis)
        context = self._build_context_from_analysis(analysis)
        business_goal = self._build_business_goal_from_analysis(analysis)
        open_points = self._build_open_points_from_analysis(analysis)
        acceptance_criteria = self._build_acceptance_criteria_from_analysis(
            analysis=analysis,
            open_points=open_points,
        )

        return TicketResult(
            ticket_type=ticket_type,
            title=title,
            description=description,
            context=context,
            current_behavior=analysis.current_behavior,
            expected_behavior=analysis.expected_behavior,
            business_goal=business_goal,
            business_impacts=list(analysis.business_impacts),
            technical_impacts=list(analysis.technical_impacts),
            dependencies=list(analysis.dependencies),
            open_points=open_points,
            acceptance_criteria=acceptance_criteria,
        )

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

    def _map_ticket_type(self, request_type: str) -> str:
        if request_type == "bug":
            return "bug"
        if request_type == "evolution":
            return "story"
        if request_type == "recipe":
            return "test"
        return "task"

    def _build_title(
        self,
        request_type: str,
        user_input: str,
        current_behavior: str | None,
        expected_behavior: str | None,
    ) -> str:
        prefix_map = {
            "bug": "[BUG]",
            "evolution": "[EVOL]",
            "recipe": "[RECETTE]",
            "po_pilotage": "[PO]",
        }
        prefix = prefix_map.get(request_type, "[ANALYSE]")

        if current_behavior is not None:
            base_title = "Comportement incorrect a investiguer"
        elif request_type == "evolution":
            base_title = self._build_evolution_title(user_input)
        elif expected_behavior is not None:
            base_title = "Besoin d'evolution a cadrer"
        else:
            base_title = user_input.strip()

        if any(keyword in self._normalize(user_input) for keyword in ("paiement", "commande", "facturation", "remise")):
            base_title = f"{base_title} sur le perimetre {self._extract_business_scope(user_input)}"

        if len(base_title) > 80:
            base_title = base_title[:77] + "..."

        return f"{prefix} {base_title}"

    def _extract_business_scope(self, user_input: str) -> str:
        lowered = self._normalize(user_input)
        for scope in ("paiement", "commande", "facturation", "remise"):
            if scope in lowered:
                return scope
        return "fonctionnel"

    def _build_evolution_title(self, user_input: str) -> str:
        title = user_input.strip()
        lowered = self._normalize(title)

        prefixes = (
            "evolution demandee :",
            "evolution demandee:",
            "evolution :",
            "evolution:",
            "besoin :",
            "besoin:",
        )
        for prefix in prefixes:
            if lowered.startswith(prefix):
                title = title[len(prefix):].strip()
                break

        if title:
            title = title[0].upper() + title[1:]
        else:
            title = "Besoin d'evolution a cadrer"

        return title

    def _build_title_from_analysis(self, analysis: AnalysisResult) -> str:
        prefix = "[RECETTE]" if analysis.recommended_output == "recipe" else "[TICKET]"
        base_title = analysis.expected_behavior or analysis.reformulation or analysis.request_summary

        if base_title.startswith("Le comportement attendu semble etre exprime dans la demande: "):
            base_title = base_title.removeprefix("Le comportement attendu semble etre exprime dans la demande: ").strip()
        elif base_title.startswith("Sujet analyse de type "):
            parts = base_title.split("Demande initiale:", maxsplit=1)
            if len(parts) == 2:
                base_title = parts[1].strip()

        if len(base_title) > 80:
            base_title = base_title[:77] + "..."

        return f"{prefix} {base_title}"

    def _build_description(
        self,
        user_input: str,
        request_type: str,
        current_behavior: str | None,
        expected_behavior: str | None,
        business_impacts: list[str],
        technical_impacts: list[str],
    ) -> str:
        parts = [
            f"Type de sujet: {request_type}.",
            f"Demande initiale: {user_input.strip()}",
        ]

        if current_behavior is not None:
            parts.append(f"Comportement actuel: {current_behavior}")
        else:
            parts.append("Comportement actuel: a confirmer.")

        if expected_behavior is not None:
            parts.append(f"Comportement attendu: {expected_behavior}")
        else:
            parts.append("Comportement attendu: a confirmer.")

        if business_impacts:
            parts.append(f"Impacts metier identifies: {' '.join(business_impacts)}")

        if technical_impacts:
            parts.append(f"Impacts techniques identifies: {' '.join(technical_impacts)}")

        return " ".join(parts)

    def _build_context(self, context_hint: str | None, request_type: str, confidence: float) -> str:
        context_parts = [f"Classification heuristique: {request_type} (confidence={confidence:.2f})."]
        if context_hint:
            context_parts.append(f"Contexte fourni: {context_hint}")
        else:
            context_parts.append("Aucun contexte complementaire n'a ete fourni.")
        return " ".join(context_parts)

    def _build_context_from_analysis(self, analysis: AnalysisResult) -> str:
        context_parts = [f"Ticket derive d'une analyse de type {analysis.detected_type}."]
        if analysis.context_hint:
            context_parts.append(f"Contexte d'analyse: {analysis.context_hint}")
        context_parts.append(f"Suite recommandee: {analysis.recommended_next_step}")
        return " ".join(context_parts)

    def _extract_current_behavior(
        self,
        user_input: str,
        lowered: str,
        request_type: str,
    ) -> str | None:
        if request_type == "evolution":
            if any(hint in lowered for hint in self.CURRENT_BEHAVIOR_HINTS if hint != "production"):
                return f"Le comportement actuel semble incorrect ou instable: {user_input.strip()}"
            if self._mentions_production(lowered) and any(
                hint in lowered for hint in ("bug", "erreur", "incident", "anomalie", "ko")
            ):
                return f"Le comportement actuel semble incorrect ou instable: {user_input.strip()}"
            return None

        if request_type == "bug" or any(hint in lowered for hint in self.CURRENT_BEHAVIOR_HINTS):
            return f"Le comportement actuel semble incorrect ou instable: {user_input.strip()}"
        return None

    def _extract_expected_behavior(self, user_input: str, lowered: str) -> str | None:
        if any(hint in lowered for hint in self.EXPECTED_BEHAVIOR_HINTS):
            return f"Le comportement cible semble exprime ou attendu dans la demande: {user_input.strip()}"
        return None

    def _build_business_goal(
        self,
        request_type: str,
        business_impacts: list[str],
        expected_behavior: str | None,
    ) -> str:
        if request_type == "bug":
            return "Corriger le comportement observe et securiser le parcours impacte."
        if request_type == "evolution":
            return "Faire evoluer le produit pour couvrir le besoin attendu."
        if request_type == "recipe":
            return "Structurer un support de recette exploitable pour valider le besoin."
        if expected_behavior is not None:
            return "Structurer une action PO a partir du comportement cible identifie."
        if business_impacts:
            return "Clarifier le besoin et preparer un ticket actionnable sur le perimetre impacte."
        return "Structurer le sujet et lever les points ouverts avant execution."

    def _build_business_goal_from_analysis(self, analysis: AnalysisResult) -> str:
        if analysis.expected_behavior is not None:
            return "Traduire le comportement attendu identifie dans l'analyse en action produit exploitable."
        if analysis.business_impacts:
            return f"Traiter le sujet pour limiter l'impact metier suivant: {analysis.business_impacts[0]}"
        return analysis.recommended_next_step

    def _extract_messages(self, lowered: str, mapping: dict[str, str]) -> list[str]:
        messages: list[str] = []
        for keyword, message in mapping.items():
            if keyword in lowered and message not in messages:
                messages.append(message)
        return messages

    def _build_description_from_analysis(self, analysis: AnalysisResult) -> str:
        parts = [analysis.request_summary]

        if analysis.current_behavior is not None:
            parts.append(f"Comportement actuel: {analysis.current_behavior}")

        if analysis.expected_behavior is not None:
            parts.append(f"Comportement attendu: {analysis.expected_behavior}")

        if analysis.business_impacts:
            parts.append(f"Impacts metier: {' '.join(analysis.business_impacts)}")

        if analysis.technical_impacts:
            parts.append(f"Impacts techniques: {' '.join(analysis.technical_impacts)}")

        return " ".join(parts)

    def _build_open_points(
        self,
        lowered: str,
        current_behavior: str | None,
        expected_behavior: str | None,
        business_impacts: list[str],
        dependencies: list[str],
    ) -> list[str]:
        open_points: list[str] = []

        if current_behavior is None:
            open_points.append("Le comportement actuel doit etre confirme avec des exemples concrets.")

        if expected_behavior is None:
            open_points.append("Le comportement attendu doit etre explicite avant execution.")

        if not business_impacts:
            open_points.append("Les impacts metier doivent etre precises avec le metier ou le PO.")

        if not dependencies:
            open_points.append("Verifier s'il existe des flux, interfaces ou objets dependants.")

        if "urgent" in lowered:
            open_points.append("Le niveau reel de priorite et le delai attendu doivent etre confirmes.")

        if self._mentions_production(lowered):
            open_points.append("Confirmer la reproductibilite et l'ampleur du sujet en production.")

        return open_points

    def _build_open_points_from_analysis(self, analysis: AnalysisResult) -> list[str]:
        open_points: list[str] = []

        for item in analysis.ambiguities + analysis.open_questions:
            if item not in open_points:
                open_points.append(item)

        if not open_points:
            open_points.append("Verifier qu'aucun point bloquant ne reste avant execution.")

        return open_points

    def _mentions_production(self, lowered: str) -> bool:
        tokens = lowered.replace(":", " ").replace(",", " ").replace(".", " ").split()
        return "prod" in tokens or "production" in tokens

    def _build_acceptance_criteria(
        self,
        request_type: str,
        current_behavior: str | None,
        expected_behavior: str | None,
        dependencies: list[str],
        open_points: list[str],
    ) -> list[str]:
        criteria = [
            "Le besoin est reformule de maniere claire et comprensible.",
            "Le perimetre du ticket est explicite.",
        ]

        if current_behavior is not None:
            criteria.append("Le comportement actuel observe est decrit de facon exploitable.")
        else:
            criteria.append("Le comportement actuel a ete confirme avant lancement de l'execution.")

        if expected_behavior is not None:
            criteria.append("Le comportement attendu cible est formule de facon testable.")
        else:
            criteria.append("Le comportement attendu a ete valide avec le metier avant execution.")

        if request_type == "bug":
            criteria.append("Le correctif ne degrade pas le parcours deja en place.")

        if dependencies:
            criteria.append("Les dependances techniques ou fonctionnelles identifiees ont ete verifiees.")

        if open_points:
            criteria.append("Les points ouverts bloquants ont ete clarifies avant demarrage.")

        return criteria

    def _build_acceptance_criteria_from_analysis(
        self,
        analysis: AnalysisResult,
        open_points: list[str],
    ) -> list[str]:
        criteria = [
            "Le sujet issu de l'analyse est reformule de maniere claire et exploitable.",
        ]

        if analysis.expected_behavior is not None:
            criteria.append("Le comportement attendu identifie dans l'analyse est couvert de facon testable.")
        else:
            criteria.append("Le comportement attendu est clarifie avant demarrage.")

        if analysis.dependencies:
            criteria.append("Les dependances identifiees dans l'analyse ont ete verifiees.")

        if open_points:
            criteria.append("Les ambiguities et questions ouvertes issues de l'analyse ont ete traitees avant execution.")

        return criteria

    def _map_analysis_output_to_ticket_type(self, recommended_output: str) -> str:
        if recommended_output == "recipe":
            return "test"
        return "story"
