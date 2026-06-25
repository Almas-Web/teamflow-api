import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.base_class import Base
from db.session import get_db
from repositories.user import UserRepository
from db.models.user import User
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember

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
        return User(id=1, name="Test User", email="test@example.com", password="password")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def authorized_client(client, db_session):
    ws = Workspace(id=1, name="Test Workspace")
    db_session.add(ws)
    member = WorkspaceMember(workspace_id=1, user_id=1, role="owner")
    db_session.add(member)
    db_session.commit()
    return client

def test_create_project_forbidden(client):
    response = client.post("/workspaces/1/projects", json={"workspace_id": 1, "name": "Test"})
    assert response.status_code in [401, 403]

def test_create_project_success(authorized_client):
    payload = {
        "workspace_id": 1, 
        "name": "New Project", 
        "description": "Description"
    }
    response = authorized_client.post("/workspaces/1/projects", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "New Project"

def test_delete_project_success(authorized_client):
    payload = {
        "workspace_id": 1, 
        "name": "Delete Me", 
        "description": "Temp"
    }
    create_response = authorized_client.post("/workspaces/1/projects", json=payload)
    project_id = create_response.json()["id"]
    
    response = authorized_client.delete(f"/workspaces/1/projects/{project_id}")
    assert response.status_code == 200