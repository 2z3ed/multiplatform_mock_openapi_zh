"""
Repository-level tests for voc_topic
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.voc_topic import VOCTopic
from shared_db.base import Base
from app.repositories.voc_topic_repository import VOCTopicRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestVOCTopicRepository:
    """Test voc_topic repository"""

    def test_create_voc_topic(self, db_session):
        """Test creating VOC topic in database"""
        repo = VOCTopicRepository(db_session)
        topic = repo.create(
            topic_name="物流延误投诉",
            topic_type="complaint",
            source="conversation",
            occurrence_count=10
        )

        assert topic.id is not None
        assert topic.topic_name == "物流延误投诉"
        assert topic.topic_type == "complaint"
        assert topic.source == "conversation"
        assert topic.occurrence_count == 10

    def test_create_with_minimal_fields(self, db_session):
        """Test creating VOC topic with minimal fields"""
        repo = VOCTopicRepository(db_session)
        topic = repo.create(
            topic_name="测试主题",
            topic_type="feedback",
            source="survey"
        )

        assert topic.id is not None
        assert topic.occurrence_count == 0
        assert topic.summary is None
        assert topic.extra_json is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing topic by id"""
        repo = VOCTopicRepository(db_session)
        created = repo.create(
            topic_name="测试主题",
            topic_type="complaint",
            source="conversation"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent topic returns None"""
        repo = VOCTopicRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all topics"""
        repo = VOCTopicRepository(db_session)
        repo.create(topic_name="主题1", topic_type="complaint", source="conversation")
        repo.create(topic_name="主题2", topic_type="feedback", source="survey")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_topic_type(self, db_session):
        """Test listing topics by topic_type"""
        repo = VOCTopicRepository(db_session)
        repo.create(topic_name="主题1", topic_type="complaint", source="conversation")
        repo.create(topic_name="主题2", topic_type="feedback", source="survey")
        repo.create(topic_name="主题3", topic_type="complaint", source="survey")

        results = repo.list_by_topic_type("complaint")
        assert len(results) == 2

    def test_occurrence_count(self, db_session):
        """Test occurrence_count field"""
        repo = VOCTopicRepository(db_session)
        topic = repo.create(
            topic_name="高频主题",
            topic_type="complaint",
            source="conversation",
            occurrence_count=100
        )

        assert topic.occurrence_count == 100

    def test_delete(self, db_session):
        """Test deleting topic"""
        repo = VOCTopicRepository(db_session)
        created = repo.create(
            topic_name="待删除主题",
            topic_type="complaint",
            source="conversation"
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
