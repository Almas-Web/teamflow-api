import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Adjust the import path according to your project structure
from main import app  
from db.base_class import Base
from db.session import get_db
from repositories.user import UserRepository
from db.models.user import User
from db.models.task import Task
from db.models.task_comment import TaskComment

# In-memory SQLite configuration for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def mock_get_current_user():
        return User(id=1, email="commenter@example.com")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_create_comment(client, db_session):
    # Setup: Create a parent task to comment on
    task = Task(id=1, project_id=1, title="Review PR")
    db_session.add(task)
    db_session.commit()

    payload = {
        "task_id": 1,
        "comment": "Looks good to me, merging!"
    }
    response = client.post("/comments", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == payload["comment"]
    assert data["task_id"] == payload["task_id"]
    assert data["user_id"] == 1
    assert "id" in data


def test_create_comment_task_not_found(client):
    payload = {
        "task_id": 999,
        "comment": "Orphan comment"
    }
    response = client.post("/comments", json=payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_get_comments_by_task(client, db_session):
    task = Task(id=1, project_id=1, title="Review PR")
    db_session.add(task)
    db_session.commit()

    client.post("/comments", json={"task_id": 1, "comment": "First comment"})
    client.post("/comments", json={"task_id": 1, "comment": "Second comment"})

    response = client.get("/comments/task/1?skip=0&limit=10")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_count"] == 2
    assert len(result["data"]) == 2


def test_get_single_comment(client, db_session):
    task = Task(id=1, project_id=1, title="Review PR")
    db_session.add(task)
    db_session.commit()

    create_res = client.post("/comments", json={"task_id": 1, "comment": "Target comment"})
    comment_id = create_res.json()["id"]

    response = client.get(f"/comments/{comment_id}")
    assert response.status_code == 200
    assert response.json()["comment"] == "Target comment"


def test_get_comment_not_found(client):
    response = client.get("/comments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_update_comment(client, db_session):
    task = Task(id=1, project_id=1, title="Review PR")
    db_session.add(task)
    db_session.commit()

    create_res = client.post("/comments", json={"task_id": 1, "comment": "Typo comment"})
    comment_id = create_res.json()["id"]

    update_payload = {
        "comment": "Fixed comment text"
    }
    response = client.put(f"/comments/{comment_id}", json=update_payload)
    
    assert response.status_code == 200
    assert response.json()["comment"] == "Fixed comment text"


def test_delete_comment(client, db_session):
    task = Task(id=1, project_id=1, title="Review PR")
    db_session.add(task)
    db_session.commit()

    create_res = client.post("/comments", json={"task_id": 1, "comment": "Delete me"})
    comment_id = create_res.json()["id"]

    delete_res = client.delete(f"/comments/{comment_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Comment deleted successfully"

    get_res = client.get(f"/comments/{comment_id}")
    assert get_res.status_code == 404