from app.modules.analysis.service import AnalysisService
from app.modules.classifier.service import ClassifierService
from app.modules.documentation.service import DocumentationService
from app.modules.ticket.service import TicketService
from app.orchestrator.router import WorkflowRouter
from app.quality.gate import QualityGate
from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse


class ProcessEngine:
    def __init__(self) -> None:
        self.classifier = ClassifierService()
        self.router = WorkflowRouter()
        self.analysis_service = AnalysisService()
        self.ticket_service = TicketService()
        self.documentation_service = DocumentationService()
        self.quality_gate = QualityGate()

    def process(self, request: ProcessRequest) -> ProcessResponse:
        classification = self.classifier.classify(
            user_input=request.user_input,
            context_hint=request.context_hint,
        )

        workflow = self.router.route(
            request_type=classification["request_type"],
            target_output=request.target_output,
        )

        if workflow == "analysis":
            result = self.analysis_service.run(
                user_input=request.user_input,
                context_hint=request.context_hint,
                classification=classification,
            )
        elif workflow == "ticket":
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

        return ProcessResponse(
            request_type=classification["request_type"],
            selected_workflow=workflow,
            confidence=classification["confidence"],
            result=result,
            quality_checks=quality["quality_checks"],
            warnings=quality["warnings"],
        )
