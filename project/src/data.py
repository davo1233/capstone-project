import datetime
import enum
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, create_engine, Date, DateTime, Enum, Float, ForeignKey, \
    Integer, JSON, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from typing import List, Optional, Union

# Setup
engine = create_engine('mysql+mysqlconnector://chadgpt:chadgpt@localhost/chadgpt')
Base = declarative_base()


''' ===================== ENUM TYPES ===================== '''

'''
TaskState: Represents the state of tasks
'''
class TaskState(enum.Enum):
    Not_Started = 0
    In_Progress = 1
    Blocked = 2
    Completed = 3

'''
PriorityLvl: Represents the priority level of
each task
'''
class PriorityLvl(enum.Enum):
    Low = 0
    Normal = 1
    High = 2
    Very_High = 3

'''
TaskFilter: Represents what search criteria is
being used to filter tasks
'''
class TaskFilter(enum.Enum):
    Time_Created = 0
    Deadline = 1
    Assigned_Taskmaster = 2
    State = 3
    ID = 4
    Name = 5


''' ===================== FAST API CLASSES ===================== '''

class BadgeIn(BaseModel):
    name:str
    description:str

class ConnectionRequestIn(BaseModel):
    sender_id: int
    receiver_id: int

class NotificationIn(BaseModel):
    user_id: int
    message:str
    type:str
    type_id:int
    title:str

class ProjectIn(BaseModel): 
    title: Union[str, None] = None

class TaskIn(BaseModel):
    # Inputs for task related methods
    assignee: Union[int, None] = None
    title: Union[str, None] = None
    dscrptn: Union[str, None] = None
    reward: int 
    status: str = TaskState.Not_Started.name
    importance: str = PriorityLvl.Normal.name
    deadline: Union[datetime.date, None] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserIn(BaseModel):
    username: Union[str, None] = None
    email: Union[str, None] = None
    firstname: Union[str, None] = None
    lastname: Union[str, None] = None
    password: Union[str, None] = None


''' ===================== MYSQL TABLE CLASSES ===================== '''

'''
SQL Table Schema:
  Classes to define SQL table schemas.
  Tables are sorted in alphabetical order.
'''
class AntReward(Base):
    __tablename__ = 'ant_rewards'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    # Relationships
    users = relationship( 
        'User', 
        # secondary = 'users_rewards',
        back_populates='rewards',
        foreign_keys=[user_id],
        )

class Badge(Base):
    __tablename__ = 'badges'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(200))
    # Relationships
    users = relationship(
        'User',
        secondary = 'user_badges',
        back_populates = 'badges'
    )

class ConnectionRequest(Base):
    __tablename__ = 'connectionRequests'
    connection_id = Column(Integer,primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    # Relationships
    sender = relationship(
        'User', 
        back_populates='sent_requests',
        foreign_keys=[sender_id]
    )
    receiver = relationship(
        'User', 
        back_populates='incoming_requests',
        foreign_keys=[receiver_id]
    )

# Labels Table - a reusable text tag to additionally filter on
class Label(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'))

    # Relationships
    tasks = relationship(
        'Task',
        back_populates='labels'
    )

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = (Column(String(50)))
    type_id = (Column(Integer))
    message = Column(String(500))
    date_created = Column(DateTime, nullable = False)
    viewed = Column(Boolean)

# Projects Table
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    # Relationships
    users = relationship(
        'User',  
        secondary='user_projects',
        back_populates='projects'
    )
    tasks = relationship(
        'Task',
        back_populates='project'
    )


# Task class for mysql
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    title = Column(String(50),nullable=False)
    description = Column(String(200))
    assignee = Column(Integer, ForeignKey('users.id'))
    reward = Column(Integer)
    status = Column(Enum(TaskState), nullable=False)
    due_date = Column(Date)
    created_datetime = Column(DateTime, nullable = False)
    updated_datetime = Column(DateTime, nullable = False, default = datetime.datetime.now, onupdate=datetime.datetime.now)
    reporter = Column(Integer, ForeignKey('users.id'), nullable=False)
    importance = Column(Enum(PriorityLvl))
    # Relationships
    project = relationship(
        'Project',
        back_populates='tasks'
    )
    assigned_user = relationship(
        'User',
        back_populates='assigned_tasks',
        foreign_keys=assignee
    )
    labels = relationship('Label', back_populates='tasks')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(50))
    password = Column(String(200))
    firstname = Column(String(50))
    lastname = Column(String(50))

    # Relationships
    projects = relationship(
        'Project', 
        secondary='user_projects',
        back_populates='users'
    )
    connections = relationship(
        'User', 
        secondary='connections',
        primaryjoin='User.id==connections.c.user_id',
        secondaryjoin='User.id==connections.c.friend_id',
    )
    sent_requests = relationship(
        'ConnectionRequest', 
        back_populates='sender',
        foreign_keys='ConnectionRequest.sender_id'
    )
    incoming_requests = relationship(
        'ConnectionRequest', 
        back_populates='receiver',
        foreign_keys='ConnectionRequest.receiver_id'
    )
    rewards = relationship(
        'AntReward', 
        secondary='user_rewards', 
        back_populates='users'
    )
    badges = relationship(
        'Badge',
        secondary = 'user_badges',
        back_populates = 'users'
    )

    assigned_tasks = relationship('Task', back_populates='assigned_user', foreign_keys='Task.assignee')


'''
Association Tables:
  These classes have been made to connect up
  related tables. (SEE TABLES BELOW). The 
  classes establish which columns in which
  tables are referencing each other.
'''
class ProjectTasks(Base):
     __tablename__ = 'project_tasks'
     project = Column(Integer, ForeignKey("projects.id"), primary_key=True)
     task = Column(Integer, ForeignKey("tasks.id"), primary_key=True)

user_projects = Table('user_projects', Base.metadata,
    Column('user', Integer, ForeignKey("users.id"), primary_key=True),
    Column('project', Integer, ForeignKey("projects.id"), primary_key=True)
)

connections = Table('connections', Base.metadata,
    Column('user_id', Integer, ForeignKey("users.id"), primary_key=True),
    Column("friend_id", Integer, ForeignKey("users.id"), primary_key=True)
)

user_rewards = Table('user_rewards', Base.metadata,
    Column('user', Integer, ForeignKey("users.id"), primary_key=True),
    Column('ant_rewards', Integer, ForeignKey("ant_rewards.id"), primary_key=True)
)

user_badges =Table('user_badges', Base.metadata,
    Column('user_id', Integer, ForeignKey("users.id"), primary_key=True),
    Column('badge_id', Integer, ForeignKey("badges.id"), primary_key=True)
)




Base.metadata.create_all(engine)

def run_databases():
    Base.metadata.create_all(engine)

