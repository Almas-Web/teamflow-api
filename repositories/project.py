from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.project import Project
from schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    # Helper (REUSABLE)
    def get_project_or_404(self, project_id: int) -> Project:
        project = (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        return project

    # CREATE
    def create_project(
        self,
        project: ProjectCreate
    ) -> Project:

        db_project = Project(
            workspace_id=project.workspace_id,
            name=project.name,
            description=project.description
        )

        try:
            self.db.add(db_project)
            self.db.commit()
            self.db.refresh(db_project)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return db_project

    # LIST
    def get_projects(
        self,
        skip: int = 0,
        limit: int = 100
    ):
        total_count = (
            self.db.query(func.count(Project.id)).scalar()
        )

        projects = (
            self.db.query(Project)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": projects
        }

    # GET ONE
    def get_project_by_id(
        self,
        project_id: int
    ) -> Project:

        return self.get_project_or_404(project_id)

    # UPDATE
    def update_project(
        self,
        project_id: int,
        payload: ProjectUpdate
    ) -> Project:

        project = self.get_project_or_404(project_id)

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(project, key, value)

        self.db.commit()
        self.db.refresh(project)

        return project

    # DELETE
    def delete_project(
        self,
        project_id: int
    ):

        project = self.get_project_or_404(project_id)

        self.db.delete(project)
        self.db.commit()

        return {
            "message": "Project deleted successfully"
        }