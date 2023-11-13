from src.auth import check_token
from src.database import Session, get_user_details, get_user_projects, get_user_connections, lookup_username_db, search_for_user
from fastapi import HTTPException, status

# Edit Name
def get_projects(token: str, db: Session):
    username = check_token(token)
    u_id = lookup_username_db(db, username)
    return get_user_projects(db, u_id)

# Get User Profile
def get_user_profile(token: str, username: str, db: Session):
    owner = check_token(token)
    owner_id = lookup_username_db(db, owner)
    user_id = lookup_username_db(db, username)
    user = get_user_details(db, user_id)
    # connections = get_user_connections(db, owner_id)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if owner_id == user_id:
        return {"access": "self", "user_details": user}
    if not any(c.id == owner_id for c in user.connections):
        return {"access": "disconnected", "user_details": user}
    return {"access": "connected", "user_details": user}

def search_user(token: str, search: str, db: Session):
    check_token(token)
    return search_for_user(db, search)