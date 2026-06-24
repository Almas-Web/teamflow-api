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
        return User(id=1, email="owner@example.com")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_add_member_as_owner(client, db_session):
    workspace = Workspace(id=10, name="Alpha Team", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    payload = {
        "user_id": 2,
        "role": "admin"
    }
    # Added /workspaces prefix
    response = client.post("/workspaces/10/members", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == 10
    assert data["user_id"] == 2
    assert data["role"] == "admin"


def test_add_member_as_non_owner(client, db_session):
    workspace = Workspace(id=20, name="Beta Team", owner_id=99)
    db_session.add(workspace)
    db_session.commit()

    payload = {
        "user_id": 3,
        "role": "member"
    }
    # Added /workspaces prefix
    response = client.post("/workspaces/20/members", json=payload)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Only owner can add members"


def test_get_members_list(client, db_session):
    workspace = Workspace(id=30, name="Gamma Team", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    client.post("/workspaces/30/members", json={"user_id": 5, "role": "member"})
    client.post("/workspaces/30/members", json={"user_id": 6, "role": "admin"})

    # Added /workspaces prefix
    response = client.get("/workspaces/30/members")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2


def test_update_member_role_as_owner(client, db_session):
    workspace = Workspace(id=40, name="Delta Team", owner_id=1)
    db_session.add(workspace)
    db_session.commit()
    
    client.post("/workspaces/40/members", json={"user_id": 7, "role": "member"})

    update_payload = {"role": "admin"}
    # Added /workspaces prefix
    response = client.put("/workspaces/40/members/7", json=update_payload)
    
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_update_member_role_not_found(client, db_session):
    workspace = Workspace(id=50, name="Epsilon Team", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    update_payload = {"role": "admin"}
    # Added /workspaces prefix
    response = client.put("/workspaces/50/members/999", json=update_payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


def test_remove_member_as_owner(client, db_session):
    workspace = Workspace(id=60, name="Zeta Team", owner_id=1)
    db_session.add(workspace)
    db_session.commit()
    
    client.post("/workspaces/60/members", json={"user_id": 8, "role": "member"})

    # Added /workspaces prefix
    response = client.delete("/workspaces/60/members/8")
    assert response.status_code == 200
    assert response.json()["message"] == "Member removed successfully"