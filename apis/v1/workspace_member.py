from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from db.models.user import User

from repositories.workspace import WorkspaceRepository
from repositories.workspace_member import WorkspaceMemberRepository
from repositories.user import UserRepository

from schemas.workspace_member import (
    WorkspaceMemberCreate,
    WorkspaceMemberRead,
    WorkspaceMemberUpdate,
)

router = APIRouter()


# ADD MEMBER
@router.post("/{workspace_id}/members", response_model=WorkspaceMemberRead)
def add_member(
    workspace_id: int,
    payload: WorkspaceMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace = WorkspaceRepository(db).get_workspace_by_id(workspace_id)

    if workspace.owner_id != current_user.id:
        raise HTTPException(403, "Only owner can add members")

    return WorkspaceMemberRepository(db).add_member(
        workspace_id,
        payload
    )


# GET MEMBERS
@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberRead])
def get_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    WorkspaceRepository(db).get_workspace_by_id(workspace_id)

    return WorkspaceMemberRepository(db).get_members(workspace_id)


# UPDATE ROLE
@router.put("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberRead)
def update_role(
    workspace_id: int,
    user_id: int,
    payload: WorkspaceMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace = WorkspaceRepository(db).get_workspace_by_id(workspace_id)

    if workspace.owner_id != current_user.id:
        raise HTTPException(403, "Only owner can update role")

    return WorkspaceMemberRepository(db).update_member_role(
        workspace_id,
        user_id,
        payload
    )


# REMOVE MEMBER
@router.delete("/{workspace_id}/members/{user_id}")
def remove_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    workspace = WorkspaceRepository(db).get_workspace_by_id(workspace_id)

    if workspace.owner_id != current_user.id:
        raise HTTPException(403, "Only owner can remove members")

    return WorkspaceMemberRepository(db).remove_member(
        workspace_id,
        user_id
    )