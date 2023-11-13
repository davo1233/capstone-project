from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import register, user_login, check_token
from src.ant_rewards import add_rewards, get_rewards
from src.badges import get_badge
from src.connections import accept_connection, create_connection,\
    get_connections,incoming_connection_requests, outgoing_connection_requests,\
    potential_connections, reject_connection
from src.data import  BadgeIn, ConnectionRequestIn, ProjectIn, \
    TaskIn, Token, UserIn
from src.database import Session, create_badges_db, get_db, get_project_by_id, lookup_username_db
from src.project import add_user_to_project, create_project, get_project,\
    get_users, project_tasklist 
from src.task import create_and_attach_new_label, create_new_task,\
    filter_tasks_type, sort_tasks_type, update_task, update_label_title
from src.user import get_projects, get_user_profile, search_user
from src.notifications import get_notifs
import subprocess
import uvicorn

# Setup
app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Welcome page
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
def startup_event():
    create_badges_db()

# Register
@app.post("/register")
async def create_user(newUser:UserIn, db: Session = Depends(get_db)):
    return register(newUser, db)

# Login
@app.post("/login", response_model=Token)
async def login(user: dict, db: Session = Depends(get_db)): 
    return user_login(user.get("username"), user.get("password"), db)


# Account - Own user profile
@app.get("/profile")
async def read_profile(token: str, username: str, db: Session = Depends(get_db)):
    return get_user_profile(token, username, db)

# User projects
@app.get("/user/projects")
async def read_user_projects(token: str, db: Session = Depends(get_db)):
    return get_projects(token, db)

@app.get("/project")
async def read_project(token: str, p_id: int, db : Session = Depends(get_db)):
    project = get_project(token, p_id, db)
    return project


# Project Tasklist
@app.get("/project/{project_id}/tasks")
async def read_tasks(project_id: int, token: str, db: Session = Depends(get_db)):
    return project_tasklist(token, project_id, db)

@app.get("/project/{project_id}/users/addable")
async def get_addable_users(project_id: int, token: str, db: Session = Depends(get_db)):
    connections = get_connections(token, check_token(token), db)
    project_users = get_users(project_id, db)
    addable_users = []
    for user in connections:
        if user not in project_users:
            addable_users.append(user)
    return addable_users


# Add user to project
@app.put("/project/{project_id}/users/add")
async def project_add_user(data: dict, db: Session = Depends(get_db)):
    return add_user_to_project(data.get("token"), data.get("project_id"), data.get("user_id"), db)

# View user profile
@app.get("/user/{user_id}")
async def connected_user_profile(token:str, username: str, db: Session = Depends(get_db)):
    return get_user_profile(token, username, db)

# Get user rewards
@app.get('/users/{user_id}/rewards/')
async def get_user_rewards(user_id: int,token:str = Header(...),db:Session = Depends(get_db)):
    return get_rewards(user_id,token,db)

# Update user rewards
@app.put('/users/{user_id}/rewards/{reward}')
async def update_user_rewards(user_id:int,reward:int,token:str = Header(...),  db:Session = Depends(get_db)):
    return add_rewards(user_id,reward,token,db)

# Get user badges
@app.get('/users/{username}/badges')
async def get_user_badges(username:str,token: str, db:Session = Depends(get_db)):
    return get_badge(username,token,db)

# Create project
@app.post("/project/create")
async def create_user_project(data : dict, db: Session = Depends(get_db)):
    project_in = ProjectIn()
    project_in.title = data.get("title")
    return create_project(data.get("token"), project_in, db)

# Return list of users that matches string
@app.get("/search")
async def search_user_list(token : str, query : str, db: Session = Depends(get_db)):
    return search_user(token, query, db)

# Connections
@app.get("/connections")
async def generate_connections_list(token: str, username: str, db: Session = Depends(get_db)):
    return get_connections(token, username, db)

# Get list of potential connections
@app.get("/connections/potential_connections")
async def generate_potential_connections(token: str = Header(...), db:Session = Depends(get_db)):
    return potential_connections(token,db)

# Get connection requests
@app.post("/connections/requests")
async def create_connection_request(request: dict, db:Session = Depends(get_db)):
    return create_connection(request,db)

# accept a request from the receiver's side
@app.put("/connections/requests/{connection_id}/accept")
def accept_connection_request(data: dict, db:Session = Depends(get_db)):
    return accept_connection(data.get("connection_id"), data.get("token"), db)

# Get incoming conneciton requests
@app.get("/connections/requests/incoming")
async def get_incoming_connection_requests(token: str, db:Session = Depends(get_db)):
    return incoming_connection_requests(token,db)

# Get sent connection requests
@app.get("/connections/requests/outgoing")
async def get_outgoing_connection_requests(token: str = Header(...),db:Session = Depends(get_db)):
    return outgoing_connection_requests(token,db)

# Delete connection requests
@app.delete("/connections/requests/{connection_id}/decline")
async def reject_connection_request(data: dict, db:Session = Depends(get_db)):
    return reject_connection(data.get("connection_id"), data.get("token"), db)

# Get notifications
@app.get('/notifications')
async def get_notifications(token:str, db:Session= Depends(get_db)):
    return get_notifs(token,db)

# create new task
@app.post("/project/{project_id}/newtask")
async def create_task(data:dict, db: Session = Depends(get_db)):
    token = data.get("token")
    project_id = data.get("project_id")
    taskInfo = data.get("taskInfo")
    assignee_id = lookup_username_db(db, taskInfo.get("assignee"))
    if (assignee_id is None):
        raise HTTPException(status_code=400, detail="Assignee's not selected")
    else:
        taskIn = TaskIn(**{
            "assignee" : assignee_id,
            "title" : taskInfo.get("title"),
            "dscrptn" : taskInfo.get("description"),
            "reward" : taskInfo.get("reward"),
            "deadline" : taskInfo.get("deadline")
        })
    
    return create_new_task(token, project_id, taskIn, db)

# update existing task
@app.put("/project/{project_id}/{task_id}")
async def create_task(data: dict, db: Session = Depends(get_db)):
    return update_task(data.get("token"), data.get("project_id"), data.get("task_id"), TaskIn(**data.get("taskInfo")), db)

# (create and) attach label to a task
@app.post("/project/{project_id}/{task_id}/labels")
async def create_label(data: dict, db: Session = Depends(get_db)):
    token = data.get("token")
    project_id = data.get("project_id")
    task_id = data.get("task_id")
    label_title = data.get("label_title")
    return create_and_attach_new_label(token, project_id, task_id, label_title, db)

# Update label description
@app.post("/project/{project_id}/{task_id}/labels/update")
async def update_label(data: dict, db: Session = Depends(get_db)):
    token = data.get("token")
    label_id = data.get("label_id")
    label_title = data.get("label_title")
    return update_label_title(token, label_id, label_title, db)

# get tasks based on sort type and whether they are ascending or descending
@app.get("/project/{project_id}/tasks/sort/{sort_type}/{asc_desc_type}")
async def sort_tasks(token: str, project_id:int, sort_type:int,asc_desc_type:int,db: Session = Depends(get_db)):
    return sort_tasks_type(token,project_id,sort_type,asc_desc_type,db)

# Filter tasks by label
@app.get("/project/{project_id}/tasks/filter/{filter_type}/{lookup}")
async def filter_tasks(token: str, project_id:int, filter_type:int,lookup:str,db: Session = Depends(get_db)):
    return filter_tasks_type(token,project_id,filter_type,lookup,db)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)