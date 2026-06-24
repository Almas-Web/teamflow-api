from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.session import get_db
from repositories.workspace import WorkspaceRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.workspace import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)

router = APIRouter()


# ---------------- LIST RESPONSE SCHEMA ----------------
class WorkspaceList(BaseModel):
    total_count: int
    skip: int
    limit: int
    data: List[WorkspaceRead]


# ---------------- CREATE WORKSPACE ----------------
@router.post(
    "/",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED
)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return WorkspaceRepository(db).create_workspace(
        workspace=payload,
        owner_id=current_user.id
    )


# ---------------- GET ALL WORKSPACES ----------------
@router.get(
    "/",
    response_model=WorkspaceList
)
def get_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return WorkspaceRepository(db).get_workspaces(
        skip=skip,
        limit=limit
    )


# ---------------- GET SINGLE WORKSPACE ----------------
@router.get(
    "/{workspace_id}",
    response_model=WorkspaceRead
)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return WorkspaceRepository(db).get_workspace_by_id(workspace_id)


# ---------------- UPDATE WORKSPACE ----------------
@router.put(
    "/{workspace_id}",
    response_model=WorkspaceRead
)
def update_workspace(
    workspace_id: int,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return WorkspaceRepository(db).update_workspace(
        workspace_id,
        payload
    )


# ---------------- DELETE WORKSPACE ----------------
@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_200_OK
)
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    return WorkspaceRepository(db).delete_workspace(workspace_id)