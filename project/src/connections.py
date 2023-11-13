from src.auth import check_token
from src.database import Session,lookup_username_db,get_user_connections,\
    get_potential_connections, create_connection_db, accept_connection_db,\
    reject_connection_db, connection_id_exists,find_receiver_id,check_friend,\
    get_incoming_connections,get_outgoing_connections  
from src.data import ConnectionRequestIn
from fastapi import HTTPException,status

def get_connections(token:str, username:str, db: Session):
    check_token(token)
    if username is None:
        raise HTTPException(status_code=404, detail="Username not found")
    user_id = lookup_username_db(db, username)
    return get_user_connections(db,user_id)

def potential_connections(token:str, db:Session):
    username = check_token(token)
    if username is None:
        raise HTTPException(status_code=404, detail="Username not found")
    return get_potential_connections(db,username)

def create_connection(request: dict, db: Session):
    sender_username = check_token(request.get("sender_token"))
    if sender_username is None:
        raise HTTPException(status_code=404, detail="Username not found")
    sender_id = lookup_username_db(db, sender_username)
    receiver_id = lookup_username_db(db, request.get("receiver_username"))
    if sender_id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot have the same sender and receiver id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if check_friend(db, sender_id, receiver_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend has already been added",
            headers={"WWW.Authenticate" : "Bearer"}
        )
    connection_request = ConnectionRequestIn(**{"sender_id" : sender_id, "receiver_id" : receiver_id})
    return create_connection_db(db, connection_request)

def incoming_connection_requests(token:str,db:Session):
    username = check_token(token)
    if username is None:
        raise HTTPException(status_code=404, detail="Username not found")
    return get_incoming_connections(db,username)

def outgoing_connection_requests(token:str,db:Session):
    username = check_token(token)
    if username is None:
        raise HTTPException(status_code=404, detail="Username not found")
    return get_outgoing_connections(db,username)


#check if the connection request exists and then accepts and adds to conn table
def accept_connection(connection_id:int,token:str,db:Session):
    username = check_token(token)
    receiver_id = find_receiver_id(db,connection_id)
    if check_valid_receiver_user(receiver_id,username,db) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to accept or reject this request",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if connection_id_exists(db,connection_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection id not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return accept_connection_db(db,connection_id)

#reject a connection from the receiver end
def reject_connection(connection_id:int,token:str, db:Session):
    username = check_token(token)
    receiver_id = find_receiver_id(db,connection_id)
    if check_valid_receiver_user(receiver_id,username,db) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to accept or reject this request",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if connection_id_exists(db,connection_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection id not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return reject_connection_db(db,connection_id)

# returns validity of the receiving user
def check_valid_receiver_user(receiver_id:int, username:int,db:Session):
    token_id = lookup_username_db(db,username)
    if token_id == receiver_id:
        return True
    else:
        return False
