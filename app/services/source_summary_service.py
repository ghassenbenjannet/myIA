from app.schemas.source_request import SourceSummaryRequest
from app.schemas.source_summary import SourceSummaryResult
from app.services.source_reader import SourceReader


class SourceSummaryService:
    """
    Minimal source-to-summary service.

    It reads a single URL and produces a compact work artifact without LLMs.
    """

    def __init__(self, source_reader: SourceReader | None = None) -> None:
        self.source_reader = source_reader or SourceReader()

    def summarize(self, request: SourceSummaryRequest) -> SourceSummaryResult:
        source = self.source_reader.read_url(request.source_ref)
        text = source["text"]

        summary = self._build_summary(text, request.context_hint)
        key_points = self._extract_key_points(text)
        open_questions = self._extract_open_questions(text)

        return SourceSummaryResult(
            source_type=request.source_type,
            source_ref=source["url"],
            source_title=source["title"],
            summary=summary,
            key_points=key_points,
            open_questions=open_questions,
            next_step_hint=self._build_next_step_hint(open_questions),
        )

    def _build_summary(self, text: str, context_hint: str | None) -> str:
        short_text = text[:240].strip()
        if context_hint:
            return f"Resume de source lu avec le contexte suivant: {context_hint}. {short_text}"
        return f"Resume de source lu: {short_text}"

    def _extract_key_points(self, text: str) -> list[str]:
        chunks = [chunk.strip() for chunk in text.split(".") if chunk.strip()]
        return chunks[:3]

    def _extract_open_questions(self, text: str) -> list[str]:
        questions: list[str] = []
        if len(text) < 120:
            questions.append("La source est breve; verifier si des informations complementaires sont necessaires.")
        if "?" in text:
            questions.append("Certaines questions semblent deja presentes dans la source et doivent etre clarifiees.")
        return questions

    def _build_next_step_hint(self, open_questions: list[str]) -> str:
        if open_questions:
            return "Clarifier les zones encore floues puis transformer ce resume en analyse ou documentation."
        return "Transformer ce resume en analyse de travail ou documentation selon le besoin."
