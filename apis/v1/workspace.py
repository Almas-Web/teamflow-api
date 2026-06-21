from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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


# CREATE WORKSPACE
@router.post("", response_model=WorkspaceRead)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace_repo = WorkspaceRepository(db=db)

    return workspace_repo.create_workspace(
        workspace=payload,
        owner_id=current_user.id
    )


# LIST WORKSPACES
@router.get("")
def get_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace_repo = WorkspaceRepository(db=db)

    return workspace_repo.get_workspaces(
        skip=skip,
        limit=limit
    )


# GET SINGLE WORKSPACE
@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace_repo = WorkspaceRepository(db=db)

    return workspace_repo.get_workspace_by_id(
        workspace_id=workspace_id
    )


# UPDATE WORKSPACE
@router.put("/{workspace_id}", response_model=WorkspaceRead)
def update_workspace(
    workspace_id: int,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace_repo = WorkspaceRepository(db=db)

    return workspace_repo.update_workspace(
        workspace_id=workspace_id,
        payload=payload
    )


# DELETE WORKSPACE
@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace_repo = WorkspaceRepository(db=db)

    return workspace_repo.delete_workspace(
        workspace_id=workspace_id
    )