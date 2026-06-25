from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from repositories.project import ProjectRepository
from db.models.user import User
from dependencies.permissions import role_checker
from schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter()

@router.post("", response_model=ProjectRead)
def create_project(
    workspace_id: int,
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["owner", "admin"]))
):
    project_repo = ProjectRepository(db=db)
    return project_repo.create_project(project=payload, workspace_id=workspace_id)

@router.get("")
def get_projects(
    workspace_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["owner", "admin", "member"]))
):
    project_repo = ProjectRepository(db=db)
    return project_repo.get_projects(workspace_id=workspace_id, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    workspace_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["owner", "admin", "member"]))
):
    project_repo = ProjectRepository(db=db)
    return project_repo.get_project_by_id(project_id=project_id)

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    workspace_id: int,
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["owner", "admin"]))
):
    project_repo = ProjectRepository(db=db)
    return project_repo.update_project(project_id=project_id, payload=payload)

@router.delete("/{project_id}")
def delete_project(
    workspace_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["owner"]))
):
    project_repo = ProjectRepository(db=db)
    return project_repo.delete_project(project_id=project_id)