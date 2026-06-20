from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship

from sqlalchemy.orm import relationship
from db.base_class import Base


class Project(Base):
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    tasks = relationship("Task", back_populates="project")