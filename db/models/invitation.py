from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship
from db.base_class import Base


class Invitation(Base):
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    email = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    status = Column(String, default="pending")
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    #relationships
    workspace = relationship("Workspace", back_populates="invitations")