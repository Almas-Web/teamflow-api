from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship
from db.base_class import Base


class Workspace(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace")
    projects = relationship("Project", back_populates="workspace")
    invitations = relationship("Invitation", back_populates="workspace")