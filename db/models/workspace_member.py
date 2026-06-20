from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship
from db.base_class import Base


class WorkspaceMember(Base):
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")