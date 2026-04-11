from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.topic import WorkTopic
from app.services.work_memory_repository import work_memory_repository


class InMemoryTopicRepository:
    """
    Minimal in-memory repository for work topics.
    """

    def __init__(self) -> None:
        self._topics: dict[str, WorkTopic] = {}

    def create_topic(self, *, run_id: str, topic_label: str) -> WorkTopic:
        now = datetime.now(UTC)
        topic = WorkTopic(
            topic_id=str(uuid4()),
            topic_label=topic_label,
            created_at=now,
            updated_at=now,
            root_run_id=run_id,
            latest_run_id=run_id,
            run_ids=[run_id],
        )
        self._topics[topic.topic_id] = topic
        return topic

    def attach_run(self, topic_id: str, run_id: str) -> WorkTopic | None:
        topic = self._topics.get(topic_id)
        if topic is None:
            return None

        run_ids = list(topic.run_ids)
        if run_id not in run_ids:
            run_ids.append(run_id)

        updated = topic.model_copy(
            update={
                "latest_run_id": run_id,
                "run_ids": run_ids,
                "updated_at": datetime.now(UTC),
            }
        )
        self._topics[topic_id] = updated
        return updated

    def get_topic(self, topic_id: str) -> WorkTopic | None:
        return self._topics.get(topic_id)

    def list_recent_topics(self, limit: int = 10) -> list[WorkTopic]:
        topics = sorted(
            self._topics.values(),
            key=lambda topic: topic.updated_at,
            reverse=True,
        )
        return topics[:limit]

    def build_default_label(self, raw_input: str, result) -> str:
        if hasattr(result, "title") and getattr(result, "title"):
            return str(getattr(result, "title"))
        if hasattr(result, "reformulation") and getattr(result, "reformulation"):
            return str(getattr(result, "reformulation"))
        if hasattr(result, "source_title") and getattr(result, "source_title"):
            return str(getattr(result, "source_title"))
        if hasattr(result, "issue_key") and hasattr(result, "title"):
            return f"{getattr(result, 'issue_key')} - {getattr(result, 'title')}"
        if len(raw_input) > 80:
            return raw_input[:77] + "..."
        return raw_input

    def get_topic_runs(self, topic_id: str):
        topic = self.get_topic(topic_id)
        if topic is None:
            return []
        runs = []
        for run_id in topic.run_ids:
            run = work_memory_repository.get_run(run_id)
            if run is not None:
                runs.append(run)
        return runs


topic_repository = InMemoryTopicRepository()
