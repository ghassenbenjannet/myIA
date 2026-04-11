from app.modules.analysis.service import AnalysisService
from app.modules.classifier.service import ClassifierService
from app.modules.documentation.service import DocumentationService
from app.modules.ticket.service import TicketService
from app.orchestrator.router import WorkflowRouter
from app.quality.gate import QualityGate
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse
from app.services.context_provider import ReadOnlyContextProvider
from app.services.context_selection import ContextSelectionPolicy
from app.services.work_memory_repository import work_memory_repository


class ProcessEngine:
    FUZZY_INPUT_HINTS = (
        "on ne sait pas",
        "a confirmer",
        "a clarifier",
        "à confirmer",
        "à clarifier",
        "probleme",
        "problème",
        "sujet",
    )

    def __init__(self) -> None:
        self.classifier = ClassifierService()
        self.router = WorkflowRouter()
        self.analysis_service = AnalysisService()
        self.ticket_service = TicketService()
        self.documentation_service = DocumentationService()
        self.quality_gate = QualityGate()
        self.context_provider = ReadOnlyContextProvider()
        self.context_selection_policy = ContextSelectionPolicy()
        self.work_memory_repository = work_memory_repository

    def process(self, request: ProcessRequest) -> ProcessResponse:
        classification = self.classifier.classify(
            user_input=request.user_input,
            context_hint=request.context_hint,
            target_output=request.target_output,
        )

        workflow = self.router.route(
            request_type=classification["request_type"],
            target_output=request.target_output,
        )
        intermediate_analysis = None
        context_used = None

        if workflow == "analysis":
            context_used = self._maybe_get_context_for_analysis(
                request=request,
                classification=classification,
                workflow=workflow,
                analyze_then_ticket=False,
            )
            result = self.analysis_service.run(
                user_input=request.user_input,
                context_hint=self._merge_context_hint(request.context_hint, context_used),
                classification=classification,
            )
        elif workflow == "ticket":
            if self._should_analyze_before_ticket(request, classification):
                context_used = self._maybe_get_context_for_analysis(
                    request=request,
                    classification=classification,
                    workflow=workflow,
                    analyze_then_ticket=True,
                )
                intermediate_analysis = self.analysis_service.run(
                    user_input=request.user_input,
                    context_hint=self._merge_context_hint(request.context_hint, context_used),
                    classification=classification,
                )
                if self._analysis_confirms_fuzziness(intermediate_analysis):
                    result = self.ticket_service.from_analysis(intermediate_analysis)
                else:
                    intermediate_analysis = None
                    context_used = None
                    result = self.ticket_service.run(
                        user_input=request.user_input,
                        context_hint=request.context_hint,
                        classification=classification,
                    )
            else:
                result = self.ticket_service.run(
                    user_input=request.user_input,
                    context_hint=request.context_hint,
                    classification=classification,
                )
        else:
            result = self.documentation_service.run(
                user_input=request.user_input,
                context_hint=request.context_hint,
                classification=classification,
            )

        quality = self.quality_gate.evaluate(
            workflow=workflow,
            result=result,
        )

        run = self.work_memory_repository.create_run(
            raw_input=request.user_input,
            target_output=request.target_output,
            request_type=classification["request_type"],
            final_workflow=workflow,
            result=result,
            intermediate_analysis=intermediate_analysis,
            context_used=context_used,
        )

        return ProcessResponse(
            run_id=run.run_id,
            request_type=classification["request_type"],
            selected_workflow=workflow,
            confidence=classification["confidence"],
            result=result,
            intermediate_analysis=intermediate_analysis,
            context_used=context_used,
            quality_checks=quality["quality_checks"],
            warnings=quality["warnings"],
        )

    def _should_analyze_before_ticket(
        self,
        request: ProcessRequest,
        classification: dict,
    ) -> bool:
        if request.target_output != "ticket":
            return False

        lowered = self._normalize_text(request.user_input)
        if classification["request_type"] == "analysis":
            return True

        return any(hint in lowered for hint in self.FUZZY_INPUT_HINTS)

    def _analysis_confirms_fuzziness(self, analysis) -> bool:
        return (
            analysis.expected_behavior is None
            or bool(analysis.ambiguities)
            or bool(analysis.open_questions)
        )

    def _normalize_text(self, value: str) -> str:
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

    def _maybe_get_context_for_analysis(
        self,
        request: ProcessRequest,
        classification: dict,
        workflow: str,
        analyze_then_ticket: bool,
    ):
        if not self.context_selection_policy.should_use_context(
            user_input=request.user_input,
            workflow=workflow,
            target_output=request.target_output,
            request_type=classification["request_type"],
            analyze_then_ticket=analyze_then_ticket,
        ):
            return None

        return self.context_provider.fetch(
            user_input=request.user_input,
            context_hint=request.context_hint,
            request_type=classification["request_type"],
        )

    def _merge_context_hint(self, context_hint: str | None, context_used) -> str | None:
        if context_used is None:
            return context_hint

        parts: list[str] = []
        if context_hint:
            parts.append(context_hint)
        parts.append(f"Contexte externe ({context_used.source_name}): {context_used.summary}")
        if context_used.snippets:
            parts.append(f"Extraits utiles: {' '.join(context_used.snippets)}")
        return " ".join(parts)
