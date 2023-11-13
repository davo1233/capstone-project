from src.auth import check_token
from src.database import Session, lookup_username_db, create_new_task_db, update_task_db, get_task_id_by_title\
    ,get_tasks_by_state,get_tasks_by_date,get_tasks_by_deadline,get_tasks_by_assignee\
    ,get_tasks_by_id, get_tasks_by_name, create_and_attach_new_label_db, get_project_users, update_label_db
from src.notifications import add_notifications, create_notification_reminder, remove_notification_reminder
from src.data import TaskIn, TaskFilter, NotificationIn, TaskState
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from src.ant_rewards import add_rewards

# from src.data import 

def create_new_task(token:str, project_id:int, taskInfo:TaskIn, db:Session):
    """Creates a new task within project"""
    # authenticate user is able to assign tasks
    reporter_uname = check_token(token)
    u_id = lookup_username_db(db, reporter_uname)
    # check existing task within project with same title does not exist
    if get_task_id_by_title(db, project_id, taskInfo.title) is not None:
        raise HTTPException(status_code=400, detail="Task with same title already exists")
    if taskInfo.assignee is None:
        raise HTTPException(status_code=400, detail="Task assignee does not exist")
    new_task = create_new_task_db(db, project_id, lookup_username_db(db, reporter_uname), taskInfo)
    notifData = NotificationIn(user_id = taskInfo.assignee, message = f'You have been assigned to the new task {taskInfo.title} by {reporter_uname}.',\
                               type= 'task', type_id = project_id, title=taskInfo.title)
    add_notifications(db, notifData)
    create_notification_reminder(db, taskInfo.deadline, timedelta(hours = 1),project_id,taskInfo, 'Your task is almost due.')
    return new_task



def update_task(token:str, project_id:int, task_id:int, taskInfo:TaskIn, db:Session):
    """Updates the fields of an existing task"""
    # authenticate user is able to alter tasks
    check_token(token)
    # check other task within project with same title does not exist 
    rtn_task_id = get_task_id_by_title(db, project_id, taskInfo.title)
    all_users = get_project_users(db,project_id)
    if rtn_task_id is not None and rtn_task_id != task_id:
        raise HTTPException(status_code=400, detail="Task with same title already exists")
    
    if taskInfo.assignee is None:
        raise HTTPException(status_code=400, detail="No Assignee")
    
    if task_id == 0:
        raise HTTPException(status_code=400, detail="0 is not a valid task id")
    
    for user in all_users:
        user_id = user.id
        if taskInfo.status == str(TaskState.Completed.value + 1) and user_id != taskInfo.assignee:
            notifData = NotificationIn(user_id = user_id, message = f'The task {taskInfo.title} was completed.',\
                type= 'task', type_id = project_id,title=taskInfo.title)
            add_notifications(db, notifData)
        elif user_id != taskInfo.assignee:
            notifData = NotificationIn(user_id = user_id, message = f'The task {taskInfo.title} that you were assigned to was updated.',\
                                    type= 'task', type_id = project_id,title=taskInfo.title)
            add_notifications(db, notifData)

    if taskInfo.status == str(TaskState.Completed.value + 1):
        add_rewards(taskInfo.assignee, taskInfo.reward, token, db)
        remove_notification_reminder(rtn_task_id)
        

    return update_task_db(db, task_id, taskInfo)

def create_and_attach_new_label(token:str, project_id:int, task_id:int, label_title:str, db:Session):
    """
    Attach a label to a task.
    If the label doesn't exist for this project,
    create it and save it for future use.
    """
    # authenticate user
    check_token(token)
     # (Create and) attach label to the given task
    return create_and_attach_new_label_db(db, task_id, label_title)

def update_label_title(token: str, label_id: int, label_title: str, db: Session):
    check_token(token)
    return update_label_db(db, label_id, label_title)

def sort_tasks_type(token:str, project_id:int, sort_type:int,asc_desc_type:int, db:Session):
    print(sort_type)
    print(asc_desc_type)
    print(TaskFilter.Assigned_Taskmaster.value)
    check_token(token)
    print('test')
    if sort_type == TaskFilter.Time_Created.value:
        print(f' time created sort type  {TaskFilter.Time_Created.value}')
        return tasks_sort_by_date(project_id,asc_desc_type, db)
    elif sort_type == TaskFilter.Deadline.value:
        print(f' deadline sort type  {TaskFilter.Deadline.value}')
        return tasks_sort_by_deadline(project_id,asc_desc_type,db)
    elif sort_type == TaskFilter.Assigned_Taskmaster.value:
        print(f' deadline sort type  {TaskFilter.Assigned_Taskmaster.value}')
        return tasks_sort_by_assignee(project_id,asc_desc_type,db)
    else:
        raise HTTPException(status_code=400, detail="invalid sort type")
    
def filter_tasks_type(token:str, project_id:int, filter_type:int,lookup:int, db:Session):
    check_token(token)
    if filter_type == TaskFilter.State.value:
        return tasks_filter_by_state(project_id,lookup, db)
    elif filter_type == TaskFilter.ID.value:
        return tasks_filter_by_id(project_id,lookup,db)
    elif filter_type == TaskFilter.Name.value:
        return tasks_filter_by_name(project_id,lookup,db)
    else:
        raise HTTPException(status_code=400, detail="invalid filter type")
    
def tasks_sort_by_date(project_id:int, asc_desc_type:int,db:Session):
    return get_tasks_by_date(db,project_id,asc_desc_type)

def tasks_sort_by_deadline(project_id:int, asc_desc_type:int,db:Session):
    return get_tasks_by_deadline(db,project_id,asc_desc_type)


def tasks_sort_by_assignee(project_id:int, asc_desc_type:int,db:Session):
    return get_tasks_by_assignee(db,project_id,asc_desc_type)
    
def tasks_filter_by_state(project_id:int, lookup:int,db:Session):
    return get_tasks_by_state(db,project_id,lookup)

def tasks_filter_by_id(project_id:int, lookup:int,db:Session):
    return get_tasks_by_id(db,project_id,lookup)

def tasks_filter_by_name(project_id:int, lookup:int,db:Session):
    return get_tasks_by_name(db,project_id,lookup)


