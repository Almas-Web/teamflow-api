import secrets
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.invitation import Invitation
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember

from schemas.invitation import InvitationCreate


class InvitationRepository:
    def __init__(self, db: Session):
        self.db = db

    # Helper
    def get_invitation_or_404(self, invitation_id: int) -> Invitation:
        invitation = (
            self.db.query(Invitation)
            .filter(Invitation.id == invitation_id)
            .first()
        )

        if not invitation:
            raise HTTPException(
                status_code=404,
                detail="Invitation not found"
            )

        return invitation

    # CREATE INVITATION
    def create_invitation(
        self,
        payload: InvitationCreate,
        expires_in_hours: int = 24
    ) -> Invitation:

        # check workspace exists
        workspace = (
            self.db.query(Workspace)
            .filter(Workspace.id == payload.workspace_id)
            .first()
        )

        if not workspace:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found"
            )

        # generate token
        token = secrets.token_urlsafe(32)

        db_invite = Invitation(
            workspace_id=payload.workspace_id,
            email=payload.email,
            token=token,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )

        try:
            self.db.add(db_invite)
            self.db.commit()
            self.db.refresh(db_invite)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return db_invite

    # LIST INVITATIONS
    def get_invitations(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        total_count = (
            self.db.query(func.count(Invitation.id))
            .filter(Invitation.workspace_id == workspace_id)
            .scalar()
        )

        invitations = (
            self.db.query(Invitation)
            .filter(Invitation.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "data": invitations
        }

    # ACCEPT INVITATION
    def accept_invitation(self, token: str, user_id: int):

        invitation = (
            self.db.query(Invitation)
            .filter(Invitation.token == token)
            .first()
        )

        if not invitation:
            raise HTTPException(
                status_code=404,
                detail="Invalid invitation token"
            )

        if invitation.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Invitation already used"
            )

        if invitation.expires_at and invitation.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Invitation expired"
            )

        # check if already member
        existing_member = (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == invitation.workspace_id,
                WorkspaceMember.user_id == user_id
            )
            .first()
        )

        if existing_member:
            raise HTTPException(
                status_code=400,
                detail="User already in workspace"
            )

        # add member
        member = WorkspaceMember(
            workspace_id=invitation.workspace_id,
            user_id=user_id,
            role="member"
        )

        invitation.status = "accepted"

        try:
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Something went wrong!"
            )

        return {
            "message": "Invitation accepted and user added to workspace"
        }

    # DELETE / CANCEL INVITATION
    def delete_invitation(self, invitation_id: int):

        invitation = self.get_invitation_or_404(invitation_id)

        self.db.delete(invitation)
        self.db.commit()

        return {
            "message": "Invitation deleted successfully"
        }