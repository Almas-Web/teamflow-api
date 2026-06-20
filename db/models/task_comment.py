from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship
from db.base_class import Base


class TaskComment(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User")