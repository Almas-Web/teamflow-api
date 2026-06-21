from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.workspace import Workspace
from schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
)


class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    # Helper (REUSABLE)
    def get_workspace_or_404(self, workspace_id: int) -> Workspace:
        workspace = (
            self.db.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )

        if not workspace:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found"
            )

        return workspace

    # CREATE
    def create_workspace(
        self,
        workspace: WorkspaceCreate,
        owner_id: int
    ) -> Workspace:

        db_workspace = Workspace(
            name=workspace.name,
            owner_id=owner_id
        )

        try:
            self.db.add(db_workspace)
            self.db.commit()
            self.db.refresh(db_workspace)

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return db_workspace

    # LIST
    def get_workspaces(
        self,
        skip: int = 0,
        limit: int = 100
    ):
        total_count = (
            self.db.query(func.count(Workspace.id)).scalar()
        )

        workspaces = (
            self.db.query(Workspace)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": workspaces
        }

    # GET ONE
    def get_workspace_by_id(
        self,
        workspace_id: int
    ) -> Workspace:

        return self.get_workspace_or_404(workspace_id)

    # UPDATE
    def update_workspace(
        self,
        workspace_id: int,
        payload: WorkspaceUpdate
    ) -> Workspace:

        workspace = self.get_workspace_or_404(workspace_id)

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(workspace, key, value)

        self.db.commit()
        self.db.refresh(workspace)

        return workspace

    # DELETE
    def delete_workspace(
        self,
        workspace_id: int
    ):

        workspace = self.get_workspace_or_404(workspace_id)

        self.db.delete(workspace)
        self.db.commit()

        return {
            "message": "Workspace deleted successfully"
        }