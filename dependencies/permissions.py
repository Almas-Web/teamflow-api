from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from repositories.user import UserRepository
# Ensure this import matches your actual file structure
from db.models.workspace_member import WorkspaceMember 

def role_checker(allowed_roles: list[str]):
    def dependency(
        workspace_id: int,
        current_user = Depends(UserRepository.get_current_user),
        db: Session = Depends(get_db)
    ):
        # Verify workspace membership
        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace"
            )

        # Verify authorized role
        if member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}, but you have: {member.role}"
            )
        
        return current_user
    
    return dependency