import pytest
from datetime import datetime, timedelta
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
from db.models.project import Project

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
        return User(id=1, email="developer@example.com")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_create_task(client, db_session):
    # Setup: Create a project to link the task to
    project = Project(id=1, workspace_id=1, name="Project Alpha")
    db_session.add(project)
    db_session.commit()

    payload = {
        "project_id": 1,
        "assigned_to": 1,
        "title": "Implement JWT Auth",
        "description": "Create secure authentication endpoints",
        "status": "todo",
        "priority": "high",
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    response = client.post("/tasks/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["project_id"] == payload["project_id"]
    assert data["priority"] == "high"
    assert "id" in data


def test_get_tasks_list(client, db_session):
    # Setup: Create a project and tasks
    project = Project(id=1, workspace_id=1, name="Project Alpha")
    db_session.add(project)
    db_session.commit()

    client.post("/tasks/", json={"project_id": 1, "title": "Task 1"})
    client.post("/tasks/", json={"project_id": 1, "title": "Task 2"})

    response = client.get("/tasks/?skip=0&limit=10")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_count"] == 2
    assert len(result["data"]) == 2


def test_get_single_task(client, db_session):
    project = Project(id=1, workspace_id=1, name="Project Alpha")
    db_session.add(project)
    db_session.commit()

    create_res = client.post("/tasks/", json={"project_id": 1, "title": "Critical Task"})
    task_id = create_res.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Critical Task"


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client, db_session):
    project = Project(id=1, workspace_id=1, name="Project Alpha")
    db_session.add(project)
    db_session.commit()

    create_res = client.post("/tasks/", json={"project_id": 1, "title": "Incomplete Task", "status": "todo"})
    task_id = create_res.json()["id"]

    update_payload = {
        "title": "Completed Task",
        "status": "done"
    }
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Completed Task"
    assert data["status"] == "done"


def test_delete_task(client, db_session):
    project = Project(id=1, workspace_id=1, name="Project Alpha")
    db_session.add(project)
    db_session.commit()

    create_res = client.post("/tasks/", json={"project_id": 1, "title": "Task to Delete"})
    task_id = create_res.json()["id"]

    delete_res = client.delete(f"/tasks/{task_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Task deleted successfully"

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404