from fastapi import APIRouter
from apis.v1 import user, workspace, workspace_member, project, task, task_comment, invitation, notification, dashboard

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(workspace.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(workspace_member.router, prefix="/workspaces", tags=["workspace-members"])

# UPDATED: Added the correct prefix so that workspace_id is captured in the route
api_router.include_router(project.router, prefix="/workspaces/{workspace_id}/projects", tags=["projects"])

api_router.include_router(task.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(task_comment.router, prefix="/comments", tags=["task-comments"])
api_router.include_router(invitation.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])