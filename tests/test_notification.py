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
from db.models.notification import Notification

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
        return User(id=1, email="recipient@example.com")

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[UserRepository.get_current_user] = mock_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()


# Test Cases

def test_create_notification(client):
    payload = {
        "user_id": 1,
        "message": "You have been added to a new project"
    }
    response = client.post("/notifications", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == payload["message"]
    assert data["user_id"] == payload["user_id"]
    assert data["is_read"] is False
    assert "id" in data


def test_get_notifications_by_user(client, db_session):
    # Setup: Create target notifications for current_user (id=1)
    db_session.add(Notification(user_id=1, message="Notification 1"))
    db_session.add(Notification(user_id=1, message="Notification 2"))
    # Notification for a different user
    db_session.add(Notification(user_id=99, message="Other Notification"))
    db_session.commit()

    response = client.get("/notifications?skip=0&limit=10")
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_count"] == 2
    assert len(result["data"]) == 2
    assert result["data"][0]["message"] == "Notification 1"


def test_mark_notification_as_read(client, db_session):
    notification = Notification(user_id=1, message="Unread event", is_read=False)
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)

    response = client.put(f"/notifications/{notification.id}/read")
    
    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_mark_notification_as_read_not_found(client):
    response = client.put("/notifications/999/read")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_delete_notification(client, db_session):
    notification = Notification(user_id=1, message="Temporary alert")
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)

    delete_res = client.delete(f"/notifications/{notification.id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Notification deleted successfully"

    # Verify tracking cleanup
    check_response = client.get("/notifications")
    assert check_response.json()["total_count"] == 0