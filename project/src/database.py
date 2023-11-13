import datetime
from enum import Enum
from fastapi import HTTPException
import json
import mysql.connector
from sqlalchemy import and_, asc, create_engine, desc, insert, literal,select,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, defer, joinedload
from src.data import AntReward, Badge, \
	ConnectionRequest, ConnectionRequestIn, connections,\
	engine, Label, Project, ProjectIn, Task, TaskIn, TaskState,\
	 User, UserIn, NotificationIn,Notification, user_badges

# Setup
Session = sessionmaker(bind=engine)

# for tests
engine = create_engine('mysql+mysqlconnector://chadgpt:chadgpt@localhost/chadgpt')

def get_db():
	db = Session()
	try:
		yield db
	finally:
		db.close()


''' ===================== DATABASE FUNCTIONS ===================== '''

def get_project_users(db, project_id):
	project = db.query(Project).filter(Project.id==project_id).first()
	return project.users

# Returns tasks by its id
def get_project_task_by_id(db:Session, task_id,project_id):
	project = db.query(Project).filter(Project.id == project_id).first()
	for task in project.tasks:
		if task.id == task_id:
			return task_id
	return None

# returns projects by name
def get_project_by_name(db:Session, project_name):
    project_name = db.query(Project).filter(Project.name==project_name).all()
    return project_name

# Get project by id
def get_project_by_id(db: Session, project_id: int):
	project = db.query(Project).filter(Project.id==project_id).first()
	return project

#return tasks by state 
def get_tasks_by_status(db,project_id,status):
	project = db.query(Project).filter(Project.id == project_id).first()
	tasks = []
	for task in project.tasks:
		if task.status == status:
			tasks.append(task)
	return tasks

#return tasks by date
def get_tasks_by_date(db,project_id,date):
	filtered_tasks = []
	project = db.query(Project).filter(Project.id == project_id).first()
	for task in project.tasks:
		filtered_tasks += select(task).where(task.c.due_date < date)
	return filtered_tasks


# Get user details
def get_user_details(db: Session, user_id):
    user = db.query(User).filter(User.id==user_id).options(joinedload(User.projects).joinedload(Project.tasks), defer(User.password)).first()
    for project in user.projects:
        project.tasks = [task for task in project.tasks if user_id == task.assignee]
    return user

#return all connections of a user
def get_user_connections(db,user_id):
	user = db.query(User).filter(User.id==user_id).first()
	if not user:
		return None
	return user.connections

#return potential connections by checking for friends already added and excluding one self
def get_potential_connections(db,username):
	check_user_id = lookup_username_db(db,username)
	if check_user_id is None:
		return None
	users = db.query(User).filter(User.id != check_user_id).all()
	users_data = {}
	curr_friends_id = [] 
	curr_friends = check_friends(db,check_user_id)
	for friend in curr_friends:
		curr_friends_id.append(friend.id)
	for user in users:
		if user.id not in curr_friends_id: 
			users_data[user.id] = user.username
	return users_data

# create a connection
def create_connection_db(db:Session,request:ConnectionRequestIn):
	receiver_id = request.receiver_id
	sender_id = request.sender_id
	if lookup_id_db(db,receiver_id) is None or lookup_id_db(db,sender_id) is None:
		raise HTTPException(status_code=404, detail="User not found")
	elif check_connection_request_exists(db,sender_id, receiver_id) == True:
		raise HTTPException(status_code=400, detail="Request already initiated")
	connection_data = {
		'sender_id': sender_id,
		'receiver_id': receiver_id,
	}
	new_connection_request = ConnectionRequest(**connection_data)
	db.add(new_connection_request)
	db.commit()
	return {"status": "Connection request initiated"}

#accept conn request
def accept_connection_db(db:Session,connection_id: int):
	'''
	Accepts connection request from user. Forms new connection between users.
	Parameters:
		connection_id (int): id of connection request
	'''
	accepted_conn = db.query(ConnectionRequest).filter\
		(ConnectionRequest.connection_id==connection_id).first()
	receiver_id = accepted_conn.receiver_id
	sender_id = accepted_conn.sender_id
	sender_data = {
		'user_id':sender_id,
		'friend_id':receiver_id,
	}
	receiver_data = {
		'user_id':receiver_id,
		'friend_id':sender_id,
	}
	db.execute(insert(connections).values(sender_data))
	db.execute(insert(connections).values(receiver_data))
	db.commit()
	remove_connection_request(db,connection_id)
	return {'message': 'Connection request accepted', 'connection_id':connection_id,\
	"accept":True}

def add_badges_db(db:Session,user_id:int,amount:int): 
	'''
	Gives/Adds badges 
	Parameters:
		user_id (int): user id
		amount (int): amount of points rewarded
	'''
	user = db.query(User).filter(User.id == user_id).first()
	if amount >= 10 and amount < 20:
		small_badge = db.query(Badge).filter(Badge.id == 1).first()
		user.badges.append(small_badge)
		db.commit()
	elif amount >= 20 and amount < 50:
		small_badge = db.query(Badge).filter(Badge.id == 1).first()
		medium_badge = db.query(Badge).filter(Badge.id == 2).first()
		user.badges.append(small_badge)
		user.badges.append(medium_badge)
		db.commit()
	elif amount >= 50:
		small_badge = db.query(Badge).filter(Badge.id == 1).first()
		medium_badge = db.query(Badge).filter(Badge.id == 2).first()
		large_badge = db.query(Badge).filter(Badge.id == 3).first()
		user.badges.append(large_badge)
		user.badges.append(medium_badge)
		user.badges.append(small_badge)
		db.commit()
	db.close()
	

def add_notifications_db(db, notificationData:NotificationIn):
	notif_data = { 
        'user_id': notificationData.user_id,
	    'message': notificationData.message,
	    'date_created': datetime.datetime.now(),
	    'viewed':False,
	    'type':notificationData.type,
	    'type_id':notificationData.type_id
	}
	
	new_notif = Notification(**notif_data)
	db.add(new_notif)
	db.commit()


def add_project_db(db: Session, user: User, project: ProjectIn):
	project_data = {
		'title': project.title
	}
	new_project = Project(**project_data)
	new_project.users.append(user)
	db.add(new_project)
	db.commit()
	return new_project.id

# Add user to project
def add_project_user(db: Session, project_id, user_id: int):
	project = db.query(Project).filter(Project.id==project_id).first()
	user = db.query(User).filter(User.id==user_id).first()
	project.users.append(user)
	db.commit()

def add_rewards_db(db, reward: int, user_id: int):
    reward_instance = db.query(AntReward).filter(AntReward.user_id == user_id).first()
    old_amount = reward_instance.amount
    new_amount = old_amount + reward
    reward_instance.amount = new_amount
    add_badges_db(db, user_id, reward_instance.amount)
    db.commit()
    new_reward = db.query(AntReward).filter(AntReward.user_id == user_id).first()
    return new_reward

# function to check if request has already been sent to the receiving user
def check_connection_request_exists(db,sender_id:int, receiver_id:int):
	exists = db.query(ConnectionRequest).filter(and_(ConnectionRequest.sender_id == sender_id,\
						  ConnectionRequest.receiver_id == receiver_id)).first()
	return bool(exists)

#function to check if a connection id exists 
def connection_id_exists(db,connection_id:int):
	conn = db.query(ConnectionRequest).get(connection_id)
	if conn is None:
		return None
	else:
		return conn

# check if users are friends already 
def check_friend(db,sender_id:int,receiver_id:int):
	friends = db.query(User).join(connections,receiver_id == connections.c.friend_id)\
		.filter(connections.c.user_id == sender_id).first()
	return friends

#check all friends different from the function above
def check_friends(db, user_id: int):
    friends = db.query(User).join(connections, User.id == connections.c.friend_id)\
        .filter(connections.c.user_id == user_id).all()
    return friends

# Attach a label to a task, creating it if it doesn't already exist
def create_and_attach_new_label_db(db, task_id:int, label_title:str):
    task = db.query(Task).filter(Task.id==task_id).first()
    # for label in task.labels:
    #     if label.title == label_title:
    #         # Label exists - just attach
    #         insert_stmt = insert(task_label_association)
    #         new_assoc = {'task_id': task_id, 'label_id': label.id}
    #         insert_stmt = insert_stmt.values(new_assoc)
    #         result = engine.connect().execute(insert_stmt)
    #         return
	
	# else, create a new label and then attach			
    lbl_data = {'title': label_title, 'task_id': task_id}
    new_lbl = Label(**lbl_data)
    db.add(new_lbl)
    db.commit()
	
    # insert_stmt = insert(task_label_association)
    # new_assoc = {'task_id': task_id, 'label_id': new_lbl.id}
    # insert_stmt = insert_stmt.values(new_assoc)
    # result = engine.connect().execute(insert_stmt)
    return new_lbl

def update_label_db(db: Session, label_id: int, label_title: str):
	label = db.query(Label).filter(Label.id == label_id).first()
	label.title = label_title
	db.commit()

def create_badges_db():
	session = Session()
	badge1 = None
	badge2 = None
	badge3 = None
	chad_one = session.query(Badge).filter(Badge.name == 'CHAD 1').first()
	chad_two = session.query(Badge).filter(Badge.name == 'CHAD 2').first()
	chad_three = session.query(Badge).filter(Badge.name == 'CHAD 3').first()
	if chad_one is None and chad_two is None and chad_three is None:
		badge1 = Badge(name='CHAD 1', description='You have reached 10 crumbs!')
		badge2 = Badge(name='CHAD 2', description='You have reached 20 crumbs!')
		badge3 = Badge(name='CHAD 3', description='You have reached 50 crumbs!')
		session.add_all([badge1, badge2, badge3])
		session.commit()
	session.close()

# create a connection
def create_connection_db(db:Session,request:ConnectionRequestIn):
	receiver_id = request.receiver_id
	sender_id = request.sender_id
	if lookup_id_db(db,receiver_id) is None or lookup_id_db(db,sender_id) is None:
		raise HTTPException(status_code=404, detail="User not found")
	elif check_connection_request_exists(db,sender_id, receiver_id) == True:
		raise HTTPException(status_code=400, detail="Request already initiated")
	connection_data = {
		'sender_id': sender_id,
		'receiver_id': receiver_id,
	}
	new_connection_request = ConnectionRequest(**connection_data)
	db.add(new_connection_request)
	db.commit() 
	return {"status": "Connection request initiated"}

# creates a task and adds it into the database
def create_new_task_db(db: Session, project_id: int, reporter: int, task: TaskIn):
    task_data = { 
        'project_id': project_id,
	    'title': task.title,
        'description': task.dscrptn,
        'assignee': task.assignee,
		'reward':task.reward,
        'status': task.status,
        'due_date': task.deadline,
	    'created_datetime': datetime.datetime.now(),
        'reporter': reporter,
        'importance': task.importance
	}
    new_task = Task(**task_data)
    db.add(new_task)
    db.commit()
    return new_task

# creates the user and adds it into the database
def create_new_user_db(db: Session,user: UserIn):
	user_data = {
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'firstname': user.firstname,
        'lastname': user.lastname,
	}
	new_user = User(**user_data)
	db.add(new_user)
	db.commit()
	user_id = lookup_username_db(db,user.username)
	new_reward = AntReward(user_id=user_id, amount=0)
	db.add(new_reward)
	db.commit()
	return new_user

# def create_rewards()
# 	    reward = AntReward(**reward_in.dict())
#     session.add(reward)
#     session.commit()

# find a receiver user id in a connect request
def find_receiver_id(db, connection_id:int):
	connection = db.query(ConnectionRequest).filter(ConnectionRequest.connection_id==connection_id).first()
	return connection.receiver_id

def get_badges(db, user_id:int):
	user = db.query(User).filter(User.id == user_id).first()
	badges = user.badges
	return badges

def get_notifications_db(db,user_id:int):
	notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
	return notifications

# get all incoming connection requests
def get_incoming_connections(db,username:str):
	user_id = lookup_username_db(db,username) 
	user = db.query(User).filter(User.id == user_id).first()
	incoming_requests = user.incoming_requests
	incoming_requests_with_username = []
	for request in incoming_requests:
		# Might work
		sender_username = id_to_username(db, request.sender_id)
		incoming_requests_with_username.append({
			"connection_id" : request.connection_id,
			"sender_username" : sender_username
		})
	return incoming_requests_with_username

def get_outgoing_connections(db,username:str):
	user_id = lookup_username_db(db,username)
	user = db.query(User).filter(User.id == user_id).first()
	outgoing_requests = user.sent_requests
	return outgoing_requests

#return potential connections by checking for friends already added and excluding one self
def get_potential_connections(db,username):
	check_user_id = lookup_username_db(db,username)
	if check_user_id is None:
		return None
	users = db.query(User).filter(User.id != check_user_id).all()
	users_data = {}
	curr_friends_id = [] 
	curr_friends = check_friends(db,check_user_id)
	for friend in curr_friends:
		curr_friends_id.append(friend.id)
	for user in users:
		if user.id not in curr_friends_id: 
			users_data[user.id] = user.username
	return users_data

# Get project by id
def get_project_by_id(db: Session, project_id: int):
	project = db.query(Project).filter(Project.id==project_id).options(
		joinedload(Project.users),
		joinedload(Project.tasks),
		# joinedload(Project.labels)
	).first()
	return project

# returns projects by name
def get_project_by_name(db:Session, project_name):
    project_name = db.query(Project).filter(Project.name==project_name).all()
    return project_name

# Returns tasks within specified project by its title
def get_project_id_by_title(db:Session, title: str):
	project = db.query(Project).filter(Project.title == title).first()
	if project is None:
		return None
	return project.id

# Returns tasks by its id
def get_project_task_by_id(db:Session, task_id,project_id):
	project = db.query(Project).filter(Project.id == project_id).first()
	for task in project.tasks:
		if task.id == task_id:
			return task_id
	return None

# Returns taskslist
def get_project_tasks(db, project_id):
    tasks = db.query(Task).filter(Task.project_id==project_id).options(
	    joinedload(Task.assigned_user),
	    joinedload(Task.labels)
	).all()
    return tasks

def get_project_users(db, project_id):
	project = db.query(Project).filter(Project.id==project_id).first()
	return project.users


def get_rewards_db(db,user_id:int):
	user =db.query(User).filter(User.id == user_id).first()
	ant_rewards_points = user.badges
	return ant_rewards_points

def get_tasks_by_assignee(db:Session,project_id,sort_type):
	if sort_type == 0:  # Sort by ascending date
		tasks = db.query(Task).filter(Task.project_id == project_id).order_by(asc(Task.assignee)).all()
	else:  # Sort by descending date
		tasks = db.query(Task).filter(Task.project_id == project_id).order_by(desc(Task.assignee)).all()
	return tasks

def get_tasks_by_deadline(db:Session,project_id,sort_type):
    if sort_type == 0:  # Sort by ascending date
        tasks = db.query(Task).filter(Task.project_id == project_id).order_by(asc(Task.due_date)).all()
    else:  # Sort by descending date
        tasks = db.query(Task).filter(Task.project_id == project_id).order_by(desc(Task.due_date)).all()
    return tasks

#return tasks by date
def get_tasks_by_date(db:Session,project_id,sort_type):
	if sort_type == 0:  # Sort by ascending date
		tasks = db.query(Task).filter(Task.project_id == project_id).order_by(asc(Task.created_datetime)).all()
	else:  # Sort by descending date
		tasks = db.query(Task).filter(Task.project_id == project_id).order_by(desc(Task.created_datetime)).all()
	return tasks

def get_tasks_by_id(db:Session,project_id,lookup):
	id = int(lookup)
	tasks = db.query(Task).filter(Task.project_id == project_id).filter(Task.id == id).first()
	return tasks

def get_tasks_by_name(db:Session,project_id,lookup):
	tasks = db.query(Task).filter(Task.project_id == project_id).filter(Task.title.ilike(f'%{lookup}%')).all()
	return tasks

def get_tasks_by_state(db:Session,project_id,lookup):
	state_val = int(lookup)
	if TaskState.In_Progress.value == state_val:
		tasks = db.query(Task).filter(Task.project_id == project_id).filter(Task.status == TaskState.In_Progress).all()
	elif TaskState.Not_Started.value == state_val:
		tasks = db.query(Task).filter(Task.project_id == project_id).filter(Task.status == TaskState.Not_Started).all()
	elif TaskState.Blocked.value == state_val:
		tasks = db.query(Task).filter(Task.project_id == project_id).filter(Task.status == TaskState.Blocked).all()
	elif TaskState.Completed.value == state_val:
		tasks = db.query(Task).filter(Task.project_id == project_id).filter(Task.status == TaskState.Completed).all()
	return tasks

#return tasks by state 
def get_tasks_by_status(db,project_id,status):
	project = db.query(Project).filter(Project.id == project_id).first()
	tasks = []
	for task in project.tasks:
		if task.status == status:
			tasks.append(task)
	return tasks

# Returns tasks within specified project by its title
def get_task_id_by_title(db:Session, project_id, title: str):
	project = db.query(Project).filter(Project.id == project_id).first()
	for task in project.tasks:
		if task.title == title:
			return task.id
	return None

# Get user details
def get_user_details(db: Session, user_id):
    user = db.query(User).filter(User.id==user_id).options(joinedload(User.projects).joinedload(Project.tasks),joinedload(User.connections), defer(User.password)).first()
    if user is None:
        return None
    for project in user.projects:
        project.tasks = [task for task in project.tasks if user_id == task.assignee]
    return user

#return all connections of a user
def get_user_connections(db: Session, user_id):
	user = db.query(User).filter(User.id==user_id).first()
	if not user:
		return None
	return user.connections

# # Get user details
# def get_user_details(db: Session, user_id):
#     details = db.query(User).filter(User.id==literal(user_id)).options(defer(User.password)).first()
#     return  details
# Get user projects
def get_user_projects(db: Session, user_id):
    user = db.query(User).filter(User.id==user_id).first()
    return user.projects

# Returns all one user's tasks
def get_users_tasks(db:Session, user_id: int):
	tasks = db.query(Task).filter(Task.assignee == user_id)
	return tasks

def id_to_username(db:Session, id: int):
	result = db.query(User).filter(User.id==id).first()
	if result == None:
		return None
	username = result.username
	return username

def lookup_id_db(db:Session,user_id:int):
	result = db.query(User).filter(User.id==user_id).first()
	if result == None:
		return None
	return User.id

# finds the username in the database and returns the id if it exists
def lookup_username_db(db:Session,username: str):
	result = db.query(User).filter(User.username==username).first()
	if result == None:
		return None
	username_id = result.id
	return username_id

#reject an incoming request from a user
def reject_connection_db(db,connection_id:int):
	remove_connection_request(db,connection_id)
	return {'message': 'Connection request rejected', 'connection_id':connection_id,\
	"accept":False}

# delete a connection request once it is accepted/rejected
def remove_connection_request(db,connection_id:int):
	deleted_conn = db.query(ConnectionRequest).filter_by(connection_id=connection_id).first()
	db.delete(deleted_conn)
	db.commit()

# Check if users are connected
def return_connections(db: Session, user_id: int):
	user = db.query(User).filter(User.id==user_id).first()
	if not user:
		return None
	return user.connections

def search_for_user(db: Session, search: str):
	# Case insensitive
	users = db.query(User).filter(User.username.ilike(f'%{search}%')).all()
	return users

# updates a task's details given a task ID
def update_task_db(db: Session, task_id: int, taskInfo: TaskIn): 
    task = db.query(Task).filter(Task.id==task_id).first()
    
    if taskInfo.assignee is not None:
        task.assignee = taskInfo.assignee
      
    if taskInfo.title is not None:
        task.title = taskInfo.title
	
    if taskInfo.dscrptn is not None:
        task.description = taskInfo.dscrptn

    if taskInfo.status is not None:
        task.status = taskInfo.status
    
    if taskInfo.importance is not None:
        task.importance = taskInfo.importance
    
    if taskInfo.deadline is not None:
        task.due_date = taskInfo.deadline
	
    if taskInfo.reward is not None:
        task.reward = taskInfo.reward
    
    db.commit()

    return {"status": "Successfully updated"}


##############################
# Simple non sqlalchemy implementation

def db_connect():
    db = mysql.connector.connect(
        host="localhost",
        user="chadgpt",
        password="chadgpt"
    )
    return db

# Function to get data
def select_query(query):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data

# Function to change data
def execute_query(query):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(query)
    db.commit()
    db.close()

# function to hard reset the database
def reset_database():
	with engine.connect() as conn:
		conn.execute(text("DROP DATABASE IF EXISTS chadgpt"))
		conn.execute(text("CREATE DATABASE chadgpt"))
############################