import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app  # Adjust the import path according to your project structure
from db.base_class import Base
from db.session import get_db
from repositories.user import UserRepository
from db.models.user import User

# 1. Setup In-Memory SQLite Database for Testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 2. Database and Authentication Mock Fixtures
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
        return User(id=1, email="testuser@example.com")

    # Override dependencies
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_create_project(client):
    payload = {
        "workspace_id": 1,
        "name": "New Awesome Project",
        "description": "This is a test description"
    }
    response = client.post("/projects", json=payload) 
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["workspace_id"] == payload["workspace_id"]
    assert "id" in data


def test_get_projects_list(client):
    client.post("/projects", json={"workspace_id": 1, "name": "Project 1"})
    
    response = client.get("/projects?skip=0&limit=10")
    assert response.status_code == 200
    
    result = response.json()
    assert "total_count" in result
    assert result["total_count"] == 1
    assert len(result["data"]) == 1


def test_get_single_project(client):
    create_res = client.post("/projects", json={"workspace_id": 1, "name": "Unique Project"})
    project_id = create_res.json()["id"]
    
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Unique Project"


def test_get_project_not_found(client):
    response = client.get("/projects/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_update_project(client):
    create_res = client.post("/projects", json={"workspace_id": 1, "name": "Old Name"})
    project_id = create_res.json()["id"]
    
    update_payload = {"name": "Updated Brand New Name"}
    response = client.put(f"/projects/{project_id}", json=update_payload)
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Brand New Name"


def test_delete_project(client):
    create_res = client.post("/projects", json={"workspace_id": 1, "name": "To Be Deleted"})
    project_id = create_res.json()["id"]
    
    delete_res = client.delete(f"/projects/{project_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Project deleted successfully"
    
    get_res = client.get(f"/projects/{project_id}")
    assert get_res.status_code == 404