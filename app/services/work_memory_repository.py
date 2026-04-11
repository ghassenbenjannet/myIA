from collections import deque
from uuid import uuid4

from app.schemas.work_memory import WorkMemoryRun


class InMemoryWorkMemoryRepository:
    """
    Minimal in-process repository for work memory runs.
    """

    def __init__(self, max_runs: int = 100) -> None:
        self._runs: dict[str, WorkMemoryRun] = {}
        self._ordered_ids: deque[str] = deque(maxlen=max_runs)
        self._max_runs = max_runs

    def save_run(self, run: WorkMemoryRun) -> WorkMemoryRun:
        if run.run_id not in self._runs and len(self._ordered_ids) == self._max_runs:
            oldest_id = self._ordered_ids.popleft()
            self._runs.pop(oldest_id, None)

        self._runs[run.run_id] = run
        if run.run_id in self._ordered_ids:
            self._ordered_ids.remove(run.run_id)
        self._ordered_ids.append(run.run_id)
        return run

    def create_run(
        self,
        raw_input: str,
        target_output: str,
        request_type: str,
        final_workflow: str,
        result,
        intermediate_analysis=None,
        context_used=None,
        parent_run_id: str | None = None,
        continuation_action: str | None = None,
    ) -> WorkMemoryRun:
        run = WorkMemoryRun(
            run_id=str(uuid4()),
            parent_run_id=parent_run_id,
            continuation_action=continuation_action,
            raw_input=raw_input,
            target_output=target_output,
            request_type=request_type,
            final_workflow=final_workflow,
            result=result,
            intermediate_analysis=intermediate_analysis,
            context_used=context_used,
        )
        return self.save_run(run)

    def get_run(self, run_id: str) -> WorkMemoryRun | None:
        return self._runs.get(run_id)

    def list_recent_runs(self, limit: int = 10) -> list[WorkMemoryRun]:
        recent_ids = list(self._ordered_ids)[-limit:]
        recent_ids.reverse()
        return [self._runs[run_id] for run_id in recent_ids if run_id in self._runs]


work_memory_repository = InMemoryWorkMemoryRepository()
