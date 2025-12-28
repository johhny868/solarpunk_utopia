"""Repository for Knowledge Osmosis

Study circles and learning artifacts data access.
"""
import sqlite3
import json
from typing import List, Optional
from datetime import datetime

from app.models.knowledge_osmosis import (
    StudyCircle,
    LearningArtifact,
    UnansweredQuestion,
    CircleStatus,
    ArtifactType,
    QuestionStatus,
)


class KnowledgeOsmosisRepository:
    """Database access for Knowledge Osmosis."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_study_circle(self, circle: StudyCircle) -> StudyCircle:
        """Create a new study circle."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO study_circles (
                id, name, description, topic, facilitator_user_id,
                member_count, status, artifact_commitment,
                created_at, started_at, completed_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            circle.id, circle.name, circle.description, circle.topic,
            circle.facilitator_user_id, circle.member_count, circle.status.value,
            circle.artifact_commitment,
            circle.created_at.isoformat() if circle.created_at else None,
            circle.started_at.isoformat() if circle.started_at else None,
            circle.completed_at.isoformat() if circle.completed_at else None,
            circle.created_by
        ))

        conn.commit()
        conn.close()
        return circle

    def create_artifact(self, artifact: LearningArtifact) -> LearningArtifact:
        """Create a new learning artifact."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO learning_artifacts (
                id, circle_id, created_by_user_id, title, description,
                artifact_type, content, topic, tags, difficulty, language,
                builds_on_artifact_id, attribution_text,
                view_count, use_count, published_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact.id, artifact.circle_id, artifact.created_by_user_id,
            artifact.title, artifact.description, artifact.artifact_type.value,
            artifact.content, artifact.topic, json.dumps(artifact.tags),
            artifact.difficulty, artifact.language,
            artifact.builds_on_artifact_id, artifact.attribution_text,
            artifact.view_count, artifact.use_count,
            artifact.published_at.isoformat() if artifact.published_at else None,
            artifact.updated_at.isoformat() if artifact.updated_at else None
        ))

        conn.commit()
        conn.close()
        return artifact

    def get_artifacts_by_topic(self, topic: str, limit: int = 20) -> List[LearningArtifact]:
        """Get artifacts by topic."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM learning_artifacts
            WHERE topic = ?
            ORDER BY use_count DESC, published_at DESC
            LIMIT ?
        """, (topic, limit))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_artifact(row) for row in rows]

    def create_unanswered_question(self, question: UnansweredQuestion) -> UnansweredQuestion:
        """Create an unanswered question."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO unanswered_questions (
                id, artifact_id, circle_id, question, context,
                status, answered_by_circle_id, answer_artifact_id,
                asked_at, answered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            question.id, question.artifact_id, question.circle_id,
            question.question, question.context, question.status.value,
            question.answered_by_circle_id, question.answer_artifact_id,
            question.asked_at.isoformat() if question.asked_at else None,
            question.answered_at.isoformat() if question.answered_at else None
        ))

        conn.commit()
        conn.close()
        return question

    def _row_to_artifact(self, row: sqlite3.Row) -> LearningArtifact:
        return LearningArtifact(
            id=row['id'],
            circle_id=row['circle_id'],
            created_by_user_id=row['created_by_user_id'],
            title=row['title'],
            description=row['description'],
            artifact_type=ArtifactType(row['artifact_type']),
            content=row['content'],
            topic=row['topic'],
            tags=json.loads(row['tags']) if row['tags'] else [],
            difficulty=row['difficulty'],
            language=row['language'],
            builds_on_artifact_id=row['builds_on_artifact_id'],
            attribution_text=row['attribution_text'],
            view_count=row['view_count'],
            use_count=row['use_count'],
            published_at=datetime.fromisoformat(row['published_at']) if row['published_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
