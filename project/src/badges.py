from src.auth import check_token
from src.data import Badge, BadgeIn
from src.database import Session,lookup_username_db,get_badges, create_badges_db
from fastapi import HTTPException

def get_badge(username:str,token:str,db:Session):
    check_token(token)
    user_id = lookup_username_db(db,username)
    return get_badges(db,user_id)


