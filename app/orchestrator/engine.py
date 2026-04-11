from fastapi import HTTPException

from app.modules.analysis.service import AnalysisService
from app.modules.classifier.service import ClassifierService
from app.modules.documentation.service import DocumentationService
from app.modules.ticket.service import TicketService
from app.orchestrator.router import WorkflowRouter
from app.quality.gate import QualityGate
from app.schemas.analysis import AnalysisResult
from app.schemas.jira_result import JiraIssueResult
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse
from app.schemas.source_summary import SourceSummaryResult
from app.schemas.work_memory import WorkMemoryRun
from app.services.context_provider import ReadOnlyContextProvider
from app.services.context_selection import ContextSelectionPolicy
from app.services.topic_repository import topic_repository
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
        self.topic_repository = topic_repository

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
        topic = self.topic_repository.create_topic(
            run_id=run.run_id,
            topic_label=self.topic_repository.build_default_label(
                raw_input=request.user_input,
                result=result,
            ),
        )
        run = self.work_memory_repository.assign_topic(run.run_id, topic.topic_id) or run

        return ProcessResponse(
            run_id=run.run_id,
            topic_id=topic.topic_id,
            request_type=classification["request_type"],
            selected_workflow=workflow,
            confidence=classification["confidence"],
            result=result,
            intermediate_analysis=intermediate_analysis,
            context_used=context_used,
            quality_checks=quality["quality_checks"],
            warnings=quality["warnings"],
        )

    def continue_run(self, source_run_id: str, action: str) -> ProcessResponse:
        source_run = self.work_memory_repository.get_run(source_run_id)
        if source_run is None:
            raise HTTPException(status_code=404, detail="Run not found")

        analysis_source = self._get_analysis_source(source_run)
        result, workflow, request_type, target_output, intermediate_analysis = self._build_continuation_result(
            source_run=source_run,
            action=action,
            analysis_source=analysis_source,
        )

        quality = self.quality_gate.evaluate(
            workflow=workflow,
            result=result,
        )

        child_run = self.work_memory_repository.create_run(
            raw_input=source_run.raw_input,
            target_output=target_output,
            request_type=request_type,
            final_workflow=workflow,
            result=result,
            intermediate_analysis=intermediate_analysis,
            context_used=source_run.context_used,
            topic_id=source_run.topic_id,
            parent_run_id=source_run.run_id,
            continuation_action=action,
        )
        topic_id = self._ensure_topic_for_continuation(source_run, child_run)
        child_run = self.work_memory_repository.assign_topic(child_run.run_id, topic_id) or child_run

        return ProcessResponse(
            run_id=child_run.run_id,
            topic_id=topic_id,
            request_type=request_type,
            selected_workflow=workflow,
            confidence=0.95,
            result=result,
            intermediate_analysis=intermediate_analysis,
            context_used=source_run.context_used,
            quality_checks=quality["quality_checks"],
            warnings=quality["warnings"],
        )

    def _build_continuation_result(
        self,
        source_run: WorkMemoryRun,
        action: str,
        analysis_source: AnalysisResult | None,
    ):
        if isinstance(source_run.result, SourceSummaryResult):
            return self._build_source_summary_continuation_result(source_run.result, action)

        if isinstance(source_run.result, JiraIssueResult):
            return self._build_jira_continuation_result(source_run.result, action)

        if action == "draft_ticket":
            if analysis_source is None:
                raise HTTPException(status_code=400, detail="No analysis available for draft_ticket")
            return (
                self.ticket_service.from_analysis(analysis_source),
                "ticket",
                analysis_source.detected_type,
                "ticket",
                analysis_source,
            )

        if action == "draft_documentation":
            if analysis_source is None:
                raise HTTPException(status_code=400, detail="No analysis available for draft_documentation")
            return (
                self.documentation_service.from_analysis(analysis_source),
                "documentation",
                analysis_source.detected_type,
                "documentation",
                analysis_source,
            )

        if action == "refine_analysis":
            if analysis_source is None:
                raise HTTPException(status_code=400, detail="No analysis available for refine_analysis")
            refined = analysis_source.model_copy(
                update={
                    "request_summary": "Analyse PO reprise a partir d'un run existant.",
                    "recommended_next_step": "Completer les zones encore floues puis choisir le livrable suivant.",
                }
            )
            return (
                refined,
                "analysis",
                analysis_source.detected_type,
                "analysis",
                None,
            )

        raise HTTPException(status_code=400, detail="Unsupported continuation action")

    def _build_source_summary_continuation_result(
        self,
        source_summary: SourceSummaryResult,
        action: str,
    ):
        if action == "draft_documentation":
            return (
                self.documentation_service.from_source_summary(source_summary),
                "documentation",
                "source_summary",
                "documentation",
                None,
            )

        if action == "refine_analysis":
            derived_analysis = self.analysis_service.from_source_summary(source_summary)
            return (
                derived_analysis,
                "analysis",
                derived_analysis.detected_type,
                "analysis",
                None,
            )

        if action == "draft_ticket":
            derived_analysis = self.analysis_service.from_source_summary(source_summary)
            return (
                self.ticket_service.from_analysis(derived_analysis),
                "ticket",
                derived_analysis.detected_type,
                "ticket",
                derived_analysis,
            )

        raise HTTPException(status_code=400, detail="Unsupported continuation action")

    def _build_jira_continuation_result(
        self,
        jira_issue: JiraIssueResult,
        action: str,
    ):
        if action == "draft_documentation":
            return (
                self.documentation_service.from_jira_issue(jira_issue),
                "documentation",
                "jira_read",
                "documentation",
                None,
            )

        if action == "refine_analysis":
            derived_analysis = self.analysis_service.from_jira_issue(jira_issue)
            return (
                derived_analysis,
                "analysis",
                derived_analysis.detected_type,
                "analysis",
                None,
            )

        if action == "draft_ticket":
            derived_analysis = self.analysis_service.from_jira_issue(jira_issue)
            return (
                self.ticket_service.from_analysis(derived_analysis),
                "ticket",
                derived_analysis.detected_type,
                "ticket",
                derived_analysis,
            )

        raise HTTPException(status_code=400, detail="Unsupported continuation action")

    def _ensure_topic_for_continuation(self, source_run: WorkMemoryRun, child_run: WorkMemoryRun) -> str:
        if source_run.topic_id:
            existing_topic = self.topic_repository.get_topic(source_run.topic_id)
            if existing_topic is not None:
                self.topic_repository.attach_run(source_run.topic_id, child_run.run_id)
                self.work_memory_repository.assign_topic(child_run.run_id, source_run.topic_id)
                return source_run.topic_id

        topic = self.topic_repository.create_topic(
            run_id=source_run.run_id,
            topic_label=self.topic_repository.build_default_label(
                raw_input=source_run.raw_input,
                result=source_run.result,
            ),
        )
        self.work_memory_repository.assign_topic(source_run.run_id, topic.topic_id)
        self.topic_repository.attach_run(topic.topic_id, child_run.run_id)
        self.work_memory_repository.assign_topic(child_run.run_id, topic.topic_id)
        return topic.topic_id

    def _get_analysis_source(self, source_run: WorkMemoryRun) -> AnalysisResult | None:
        if isinstance(source_run.result, AnalysisResult):
            return source_run.result
        return source_run.intermediate_analysis

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
