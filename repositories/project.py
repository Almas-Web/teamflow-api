from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, ProjectRead

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project_or_404(self, project_id: int) -> Project:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def create_project(self, project: ProjectCreate, workspace_id: int) -> ProjectRead:
        db_project = Project(
            workspace_id=workspace_id,
            name=project.name,
            description=project.description
        )
        try:
            self.db.add(db_project)
            self.db.commit()
            self.db.refresh(db_project)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Something went wrong!")
        return ProjectRead.model_validate(db_project)

    def get_projects(self, workspace_id: int, skip: int = 0, limit: int = 100):
        query = self.db.query(Project).filter(Project.workspace_id == workspace_id)
        total_count = query.count()
        projects = query.offset(skip).limit(limit).all()
        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": [ProjectRead.model_validate(p) for p in projects]
        }

    def get_project_by_id(self, project_id: int) -> ProjectRead:
        project = self.get_project_or_404(project_id)
        return ProjectRead.model_validate(project)

    def update_project(self, project_id: int, payload: ProjectUpdate) -> ProjectRead:
        project = self.get_project_or_404(project_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return ProjectRead.model_validate(project)

    def delete_project(self, project_id: int):
        project = self.get_project_or_404(project_id)
        self.db.delete(project)
        self.db.commit()
        return {"message": "Project deleted successfully"}