from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from db.session import get_db
from db.redis import get_cache, set_cache

from db.models.user import User
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember
from db.models.task import Task
from db.models.project import Project

from repositories.user import UserRepository 

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_statistics(
    current_user: User = Depends(UserRepository.get_current_user), 
    db: Session = Depends(get_db)
):
    cache_key = f"dashboard:{current_user.id}"
    
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    try:
        owned_workspaces = db.query(Workspace).filter(Workspace.owner_id == current_user.id).count()
        total_workspaces = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).count()
        total_tasks = db.query(Task).filter(Task.assigned_to == current_user.id).count()
        
        todo_tasks = db.query(Task).filter(Task.assigned_to == current_user.id, Task.status == "todo").count()
        in_progress_tasks = db.query(Task).filter(Task.assigned_to == current_user.id, Task.status == "in_progress").count()
        done_tasks = db.query(Task).filter(Task.assigned_to == current_user.id, Task.status == "done").count()

        dashboard_data = {
            "workspaces": {
                "owned": owned_workspaces,
                "joined": total_workspaces
            },
            "tasks": {
                "total": total_tasks,
                "todo": todo_tasks,
                "in_progress": in_progress_tasks,
                "done": done_tasks
            }
        }

        set_cache(cache_key, dashboard_data, expire=300)
        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard data: {str(e)}"
        )