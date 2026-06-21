from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from repositories.project import ProjectRepository
from repositories.user import UserRepository
from db.models.user import User

from schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter()


# CREATE PROJECT
@router.post("", response_model=ProjectRead)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    project_repo = ProjectRepository(db=db)

    return project_repo.create_project(
        project=payload
    )


# LIST PROJECTS
@router.get("")
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    project_repo = ProjectRepository(db=db)

    return project_repo.get_projects(
        skip=skip,
        limit=limit
    )


# GET SINGLE PROJECT
@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    project_repo = ProjectRepository(db=db)

    return project_repo.get_project_by_id(
        project_id=project_id
    )


# UPDATE PROJECT
@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    project_repo = ProjectRepository(db=db)

    return project_repo.update_project(
        project_id=project_id,
        payload=payload
    )


# DELETE PROJECT
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(UserRepository.get_current_user)
):
    project_repo = ProjectRepository(db=db)

    return project_repo.delete_project(
        project_id=project_id
    )