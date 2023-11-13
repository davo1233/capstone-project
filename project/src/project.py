from datetime import date
from fastapi import HTTPException
from src.auth import check_token
from src.database import get_project_users, get_project_tasks,get_project_by_name, \
    get_tasks_by_status,get_tasks_by_date,add_project_db,add_project_user,lookup_username_db,\
    get_user_connections,get_user_details,get_project_by_id, Session
from src.notifications import add_notifications
from src.data import ProjectIn, NotificationIn

def get_project(token: str, project_id: int, db: Session):
    check_token(token)
    return get_project_by_id(db, project_id)

def get_users(project_id: int, db: Session):
    return get_project_users(db, project_id)

# Tasklist
def project_tasklist(token: str, project_id: int, db: Session):
    check_token(token)
    return get_project_tasks(db, project_id)

def project_filter_by_name(token:str, project_name:str, db:Session):
    check_token(token)
    return get_project_by_name(db,project_name)



def add_user_to_project(token: str, project_id: int, user_id: int, db: Session):
    username = check_token(token)
    u_id = lookup_username_db(db, username)
    user = get_user_details(db, user_id)
    project = get_project_by_id(db, project_id)
    if user in project.users:
        raise HTTPException(status_code=400, 
            detail="User already in project")
    connections = get_user_connections(db, u_id) 
    if not connections or user not in connections:
        raise HTTPException(status_code=400, 
            detail="Not connected to user")
    notifData = NotificationIn(user_id = user_id, message = f'You have been added to the project {project.title}.'\
                               ,type='project', type_id = project_id,title= project.title)
    add_notifications(db, notifData)
    return add_project_user(db, project_id, user_id)

def create_project(token: str, project: ProjectIn, db: Session):
    username = check_token(token)
    u_id = lookup_username_db(db, username)
    user = get_user_details(db, u_id)
    return add_project_db(db, user, project)