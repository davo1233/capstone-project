from src.auth import check_token
from src.database import get_rewards_db, Session,lookup_username_db,add_rewards_db
from fastapi import HTTPException,status

# gets the total reward points of a user
def get_rewards(user_id,token:str,db:Session):
    check_token(token)
    return get_rewards_db(db,user_id)

# adds the reward points retrieved from a task and puts it into the user
def add_rewards(user_id:int,reward:int, token:str, db:Session):
    check_token(token)
    return add_rewards_db(db,reward,user_id)


