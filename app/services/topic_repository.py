from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.topic import TopicSummary, WorkTopic
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

    def list_topics(self) -> list[WorkTopic]:
        topics = sorted(
            self._topics.values(),
            key=lambda topic: topic.updated_at,
            reverse=True,
        )
        return topics

    def list_topic_summaries(self) -> list[TopicSummary]:
        return [
            TopicSummary(
                topic_id=topic.topic_id,
                topic_label=topic.topic_label,
                created_at=topic.created_at,
                updated_at=topic.updated_at,
                root_run_id=topic.root_run_id,
                latest_run_id=topic.latest_run_id,
                status=topic.status,
                run_count=len(topic.run_ids),
            )
            for topic in self.list_topics()
        ]

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
        return sorted(runs, key=lambda run: run.created_at)

    def clear(self) -> None:
        self._topics.clear()


topic_repository = InMemoryTopicRepository()
