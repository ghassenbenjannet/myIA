from pydantic import BaseModel

from app.schemas.analysis import AnalysisResult
from app.schemas.documentation import DocumentationResult
from app.schemas.ticket import TicketResult

QualityResult = AnalysisResult | TicketResult | DocumentationResult | dict


class QualityGate:
    """
    Minimal quality gate for the MVP.

    This does not reject output yet.
    It returns checks and warnings that can later be used
    for confidence scoring or human validation.
    """

    def evaluate(self, workflow: str, result: QualityResult) -> dict[str, list[str]]:
        quality_checks: list[str] = []
        warnings: list[str] = []
        payload = self._to_dict(result)

        if payload:
            quality_checks.append("result_not_empty")
        else:
            warnings.append("empty_result")
            return {
                "quality_checks": quality_checks,
                "warnings": warnings,
            }

        if workflow == "analysis":
            self._check_analysis(payload, quality_checks, warnings)
        elif workflow == "ticket":
            self._check_ticket(payload, quality_checks, warnings)
        elif workflow == "documentation":
            self._check_documentation(payload, quality_checks, warnings)

        return {
            "quality_checks": quality_checks,
            "warnings": warnings,
        }

    def _to_dict(self, result: QualityResult) -> dict:
        if isinstance(result, BaseModel):
            return result.model_dump()
        return result

    def _check_analysis(
        self,
        result: dict,
        quality_checks: list[str],
        warnings: list[str],
    ) -> None:
        if result.get("reformulation"):
            quality_checks.append("analysis_reformulation_present")
        else:
            warnings.append("analysis_missing_reformulation")

        if result.get("ambiguities"):
            quality_checks.append("analysis_ambiguities_present")
        else:
            warnings.append("analysis_missing_ambiguities")

        if result.get("open_questions"):
            quality_checks.append("analysis_open_questions_present")
        else:
            warnings.append("analysis_missing_open_questions")

    def _check_ticket(
        self,
        result: dict,
        quality_checks: list[str],
        warnings: list[str],
    ) -> None:
        if result.get("title"):
            quality_checks.append("ticket_title_present")
        else:
            warnings.append("ticket_missing_title")

        if result.get("description"):
            quality_checks.append("ticket_description_present")
        else:
            warnings.append("ticket_missing_description")

        if result.get("acceptance_criteria"):
            quality_checks.append("ticket_acceptance_criteria_present")
        else:
            warnings.append("ticket_missing_acceptance_criteria")

    def _check_documentation(
        self,
        result: dict,
        quality_checks: list[str],
        warnings: list[str],
    ) -> None:
        if result.get("title"):
            quality_checks.append("documentation_title_present")
        else:
            warnings.append("documentation_missing_title")

        if result.get("sections"):
            quality_checks.append("documentation_sections_present")
        else:
            warnings.append("documentation_missing_sections")
