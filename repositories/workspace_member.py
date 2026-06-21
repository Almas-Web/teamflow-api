from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from db.models.workspace_member import WorkspaceMember
from schemas.workspace_member import (
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
)


class WorkspaceMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    # ADD MEMBER
    def add_member(
        self,
        workspace_id: int,
        payload: WorkspaceMemberCreate
    ) -> WorkspaceMember:

        db_member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=payload.user_id,
            role=payload.role or "member"
        )

        try:
            self.db.add(db_member)
            self.db.commit()
            self.db.refresh(db_member)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="User already exists in workspace or invalid data"
            )

        return db_member

    # GET MEMBERS
    def get_members(self, workspace_id: int):
        members = (
            self.db.query(WorkspaceMember)
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .all()
        )

        return members

    # UPDATE MEMBER ROLE
    def update_member_role(
        self,
        workspace_id: int,
        user_id: int,
        payload: WorkspaceMemberUpdate
    ) -> WorkspaceMember:

        member = (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            )
            .first()
        )

        if not member:
            raise HTTPException(
                status_code=404,
                detail="Member not found"
            )

        if payload.role:
            member.role = payload.role

        self.db.commit()
        self.db.refresh(member)

        return member

    # REMOVE MEMBER
    def remove_member(
        self,
        workspace_id: int,
        user_id: int
    ):

        member = (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            )
            .first()
        )

        if not member:
            raise HTTPException(
                status_code=404,
                detail="Member not found"
            )

        self.db.delete(member)
        self.db.commit()

        return {
            "message": "Member removed successfully"
        }