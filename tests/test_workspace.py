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
        return User(id=1, email="workspaceowner@example.com")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_create_workspace(client):
    payload = {
        "name": "Engineering Workspace"
    }
    response = client.post("/workspaces/", json=payload)
    
    assert response.status_code == 201 
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["owner_id"] == 1
    assert "id" in data


def test_get_workspaces_list(client):
    client.post("/workspaces/", json={"name": "Workspace A"})
    client.post("/workspaces/", json={"name": "Workspace B"})
    
    response = client.get("/workspaces/?skip=0&limit=10")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_count"] == 2
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] == "Workspace A"


def test_get_single_workspace(client):
    create_res = client.post("/workspaces/", json={"name": "Secret Workspace"})
    workspace_id = create_res.json()["id"]
    
    response = client.get(f"/workspaces/{workspace_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Secret Workspace"


def test_get_workspace_not_found(client):
    response = client.get("/workspaces/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Workspace not found"


def test_update_workspace(client):
    create_res = client.post("/workspaces/", json={"name": "Old Workspace Name"})
    workspace_id = create_res.json()["id"]
    
    update_payload = {"name": "New Revamped Workspace"}
    response = client.put(f"/workspaces/{workspace_id}", json=update_payload)
    
    assert response.status_code == 200
    assert response.json()["name"] == "New Revamped Workspace"


def test_delete_workspace(client):
    create_res = client.post("/workspaces/", json={"name": "Temporary Workspace"})
    workspace_id = create_res.json()["id"]
    
    delete_res = client.delete(f"/workspaces/{workspace_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Workspace deleted successfully"
    
    get_res = client.get(f"/workspaces/{workspace_id}")
    assert get_res.status_code == 404