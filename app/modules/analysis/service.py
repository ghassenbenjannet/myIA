from app.schemas.analysis import AnalysisResult


class AnalysisService:
    """
    Deterministic analysis service for the MVP.

    The goal is to produce a more actionable PO-style analysis without
    introducing NLP or external dependencies.
    """

    TECHNICAL_KEYWORDS = {
        "api": "Des interfaces API peuvent etre impactees.",
        "batch": "Des traitements batch peuvent devoir etre verifies.",
        "import": "Les flux d'import peuvent etre affectes.",
        "flux": "Les flux inter-applications doivent etre verifies.",
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
    ) -> AnalysisResult:
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
                detected_type=classification["request_type"],
                current_behavior=current_behavior,
                expected_behavior=expected_behavior,
            ),
            request_summary=self._build_request_summary(
                detected_type=classification["request_type"],
                current_behavior=current_behavior,
                expected_behavior=expected_behavior,
                business_impacts=business_impacts,
                technical_impacts=technical_impacts,
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
                expected_behavior=expected_behavior,
                ambiguities=ambiguities,
                recommended_output=recommended_output,
            ),
            recommended_output=recommended_output,
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

    def _build_reformulation(
        self,
        user_input: str,
        detected_type: str,
        current_behavior: str | None,
        expected_behavior: str | None,
    ) -> str:
        if current_behavior and expected_behavior:
            return (
                f"Sujet analyse de type {detected_type}: un comportement actuel semble poser probleme "
                f"et un comportement cible est a clarifier ou valider. Demande initiale: {user_input}"
            )
        if current_behavior:
            return (
                f"Sujet analyse de type {detected_type}: la demande decrit surtout un comportement actuel "
                f"problematique a investiguer. Demande initiale: {user_input}"
            )
        if expected_behavior:
            return (
                f"Sujet analyse de type {detected_type}: la demande decrit surtout un comportement cible "
                f"ou une attente a cadrer. Demande initiale: {user_input}"
            )
        return (
            f"Sujet analyse de type {detected_type}: la demande doit etre structuree avant transformation "
            f"en livrable actionnable. Demande initiale: {user_input}"
        )

    def _build_request_summary(
        self,
        detected_type: str,
        current_behavior: str | None,
        expected_behavior: str | None,
        business_impacts: list[str],
        technical_impacts: list[str],
    ) -> str:
        parts = [f"Analyse orientee PO pour un sujet classe {detected_type}."]
        if current_behavior:
            parts.append("Un comportement actuel a ete identifie.")
        if expected_behavior:
            parts.append("Un comportement attendu est present ou sous-entendu.")
        if business_impacts:
            parts.append("Des impacts metier potentiels ont ete releves.")
        if technical_impacts:
            parts.append("Des impacts techniques potentiels ont ete releves.")
        return " ".join(parts)

    def _extract_current_behavior(self, user_input: str, lowered: str) -> str | None:
        if any(hint in lowered for hint in self.CURRENT_BEHAVIOR_HINTS):
            return f"Le comportement actuel semble problematique ou en echec: {user_input.strip()}"
        return None

    def _extract_expected_behavior(self, user_input: str, lowered: str) -> str | None:
        if any(hint in lowered for hint in self.EXPECTED_BEHAVIOR_HINTS):
            return f"Le comportement attendu semble etre exprime dans la demande: {user_input.strip()}"
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
            ambiguities.append("Le comportement actuel n'est pas decrit de maniere suffisamment explicite.")

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
        risks = ["Risque de mauvaise priorisation si le besoin n'est pas suffisamment cadre."]

        if technical_impacts:
            risks.append("Risque de regression technique si les composants impactes ne sont pas identifies.")

        if business_impacts:
            risks.append("Risque d'impact metier si le comportement cible n'est pas valide avec les parties prenantes.")

        if dependencies:
            risks.append("Risque d'oublier un systeme ou flux dependant lors de la mise en oeuvre.")

        if "production" in lowered or "prod" in lowered:
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

        if "production" in lowered or "prod" in lowered:
            questions.append("Le sujet est-il reproducible et quantifie en production ?")

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
        expected_behavior: str | None,
        ambiguities: list[str],
        recommended_output: str,
    ) -> str:
        if ambiguities:
            return (
                "Clarifier les zones d'incertitude, valider le comportement attendu et confirmer le perimetre "
                f"avant de produire un livrable de type {recommended_output}."
            )
        if expected_behavior is not None and recommended_output == "ticket":
            return "Transformer cette analyse en draft ticket avec description, impacts et criteres d'acceptation."
        if recommended_output == "documentation":
            return "Transformer cette analyse en draft de documentation structuree."
        if recommended_output == "recipe":
            return "Transformer cette analyse en draft de recette avec cas de test cibles."
        return "Completer l'analyse avec les parties prenantes avant de decider du livrable suivant."
