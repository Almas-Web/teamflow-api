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
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember
from db.models.invitation import Invitation

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
        return User(id=1, email="admin@example.com")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_create_invitation_success(client, db_session):
    # Setup: Create a workspace to invite someone to
    workspace = Workspace(id=1, name="Workspace Alpha", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    payload = {
        "workspace_id": 1,
        "email": "invitee@example.com"
    }
    response = client.post("/invitations", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == 1
    assert data["email"] == "invitee@example.com"
    assert data["status"] == "pending"
    assert "token" in data


def test_create_invitation_workspace_not_found(client):
    payload = {
        "workspace_id": 999,
        "email": "invitee@example.com"
    }
    response = client.post("/invitations", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Workspace not found"


def test_get_invitations_by_workspace(client, db_session):
    workspace = Workspace(id=2, name="Workspace Beta", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    # Create two invitations
    client.post("/invitations", json={"workspace_id": 2, "email": "user1@example.com"})
    client.post("/invitations", json={"workspace_id": 2, "email": "user2@example.com"})

    response = client.get("/invitations?workspace_id=2&skip=0&limit=10")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_count"] == 2
    assert len(result["data"]) == 2


def test_accept_invitation_success(client, db_session):
    workspace = Workspace(id=3, name="Workspace Gamma", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    # Create invitation directly through API to extract token
    create_res = client.post("/invitations", json={"workspace_id": 3, "email": "user3@example.com"})
    token = create_res.json()["token"]

    # Current user (id=1) accepts the token
    accept_payload = {"token": token}
    response = client.post("/invitations/accept", json=accept_payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Invitation accepted and user added to workspace"

    # Verify the invitation record changed status
    db_invite = db_session.query(Invitation).filter(Invitation.token == token).first()
    assert db_invite.status == "accepted"


def test_accept_invitation_invalid_token(client):
    response = client.post("/invitations/accept", json={"token": "fake-token-string"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid invitation token"


def test_accept_invitation_expired(client, db_session):
    workspace = Workspace(id=4, name="Workspace Delta", owner_id=1)
    db_session.add(workspace)
    
    # Manually inject an already expired invitation
    expired_invite = Invitation(
        workspace_id=4,
        email="late@example.com",
        token="expired-token-123",
        status="pending",
        expires_at=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(expired_invite)
    db_session.commit()

    response = client.post("/invitations/accept", json={"token": "expired-token-123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invitation expired"


def test_accept_invitation_already_member(client, db_session):
    workspace = Workspace(id=5, name="Workspace Epsilon", owner_id=1)
    # Make current user (id=1) already a member
    member = WorkspaceMember(workspace_id=5, user_id=1, role="member")
    
    invite = Invitation(
        workspace_id=5,
        email="admin@example.com",
        token="valid-token-but-member",
        status="pending",
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add_all([workspace, member, invite])
    db_session.commit()

    response = client.post("/invitations/accept", json={"token": "valid-token-but-member"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User already in workspace"


def test_delete_invitation(client, db_session):
    workspace = Workspace(id=6, name="Workspace Zeta", owner_id=1)
    db_session.add(workspace)
    db_session.commit()

    create_res = client.post("/invitations", json={"workspace_id": 6, "email": "cancel@example.com"})
    invite_id = create_res.json()["id"]

    delete_res = client.delete(f"/invitations/{invite_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Invitation deleted successfully"