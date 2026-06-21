from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from repositories.invitation import InvitationRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.invitation import (
    InvitationCreate,
    InvitationRead,
    InvitationAccept,
)

router = APIRouter()


# CREATE INVITATION
@router.post("", response_model=InvitationRead)
def create_invitation(
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = InvitationRepository(db=db)

    return repo.create_invitation(
        payload=payload
    )


# LIST INVITATIONS (BY WORKSPACE)
@router.get("")
def get_invitations(
    workspace_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = InvitationRepository(db=db)

    return repo.get_invitations(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit
    )


# ACCEPT INVITATION
@router.post("/accept")
def accept_invitation(
    payload: InvitationAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = InvitationRepository(db=db)

    return repo.accept_invitation(
        token=payload.token,
        user_id=current_user.id
    )


# DELETE / CANCEL INVITATION
@router.delete("/{invitation_id}")
def delete_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    repo = InvitationRepository(db=db)

    return repo.delete_invitation(
        invitation_id=invitation_id
    )