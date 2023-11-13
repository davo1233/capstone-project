import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from fastapi.testclient import TestClient
from fastapi import Depends
from .. import main
from unittest.mock import MagicMock
from src.database import get_db, Session,reset_database
from src.data import UserIn, run_databases
import re
from jose import jwt
SECRET_KEY = "ChadGPT"
ALGORITHM = "HS256"

# warning: these tests reset the database every time a test suite is run 
client = TestClient(main.app)
# tests the register function
def test_register():
    reset_database()
    run_databases()
    response = client.post(
        '/register',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'firstname': 'Test',
            'lastname': 'User',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    decoded_token = jwt.decode(token,SECRET_KEY)
    assert 'sub' in decoded_token
    assert 'exp' in decoded_token
    assert response.json().get('token_type') == 'bearer'

def test_register_twice():
    reset_database()
    run_databases()
    response = client.post(
        '/register',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'firstname': 'Test',
            'lastname': 'User',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    response = client.post(
        '/register',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'firstname': 'Test',
            'lastname': 'User',
            'password': 'test'
        }
    )
    assert response.status_code == 400
    assert response.json().get('detail') == 'Username already registered'

def create_users():
    response = client.post(
        '/register',
        json={
            'username': 'test2',
            'email': 'test2@test.com',
            'firstname': 'Test2',
            'lastname': 'User2',
            'password': 'test2'
        }
    )
    assert response.status_code == 200

    response = client.post(
    '/register',
        json={
            'username': 'test3',
            'email': 'test3@test.com',
            'firstname': 'Test3',
            'lastname': 'User3',
            'password': 'test3'
        }
    )
    assert response.status_code == 200
    response = client.post(
        '/register',
        json={
            'username': 'test4',
            'email': 'test4@test.com',
            'firstname': 'Test4',
            'lastname': 'Use4r',
            'password': 'test4'
        }
    )
    assert response.status_code == 200

def test_login():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200

def test_login_incorrect_password():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test1'
        }
    )
    assert response.status_code == 401
    assert response.json().get('detail') == 'Incorrect username or password'

def test_login_incorrect_username():
    response = client.post(
        '/login',
        json={
            'username': 'test1',
            'password': 'test'
        }
    )
    assert response.status_code == 401
    assert response.json().get('detail') == 'Incorrect username or password'


def test_profile():
    create_users()
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    profile_resp = client.get(
        '/profile',
        params={"token": token, "username": 'test'}
    )
    profile_resp.status_code == 200
    assert profile_resp.json().get("access") == "self" 
    assert profile_resp.json().get("user_details") is not None 
    user_details = profile_resp.json().get("user_details")
    assert user_details["lastname"] == "User"
    assert user_details["username"] == "test"
    assert user_details["email"] == "test@test.com"
    assert user_details["firstname"] == "Test"
    assert user_details["projects"] == []
    assert user_details["connections"] == []

def test_invalid_token_profile():
    profile_resp = client.get(
        '/profile',
        params={"token": 'your mum', "username": 'test'}
    )
    profile_resp.status_code = 401
    profile_resp.json().get('detail') == "Invalid access token - please re-login"

def test_invalid_username_profile():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    profile_resp = client.get(
        '/profile',
        params={"token": token, "username": 'test1'}
    )
    profile_resp.status_code = 404
    profile_resp.json().get('detail') == "User does not exist"

def test_disconnected_profile_lookup():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    profile_resp = client.get(
        '/profile',
        params={"token": token, "username": 'test2'}
    )
    assert profile_resp.status_code == 200
    assert profile_resp.json().get('access') == 'disconnected'

def test_create_connectiont():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    request_resp = client.post(
        '/connections/requests',
        json={
            'sender_token': token,
            'receiver_username': 'test2'
        }

    )
    assert request_resp.status_code == 200
    request_resp.json().get('details') == 'Connection request initiated'

def test_accept_connection_request():
    # Login and create a connection request
    login_response = client.post(
        '/login',
        json={
            'username': 'test2',
            'password': 'test2'
        }
    )
    assert login_response.status_code == 200
    token = login_response.json().get('access_token')
    incoming_connection_response = client.get(
        '/connections/requests/incoming',
        params={"token":token}
    )
    assert incoming_connection_response.status_code == 200
    
    connection_id = incoming_connection_response.json()[0]['connection_id']

    # Accept the connection request
    accept_response = client.put(
        f'/connections/requests/{connection_id}/accept',
        json={
            'token': token,
            'connection_id':connection_id,
        }
    )
    assert accept_response.status_code == 200
    assert accept_response.json().get('message') == 'Connection request accepted'

def test_create_connection_reject():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    request_resp = client.post(
        '/connections/requests',
        json={
            'sender_token': token,
            'receiver_username': 'test3'
        }
    )
    assert request_resp.status_code == 200
    request_resp.json().get('details') == 'Connection request initiated'
    response_test3 = client.post(
        '/login',
        json={
            'username': 'test3',
            'password': 'test3'
        }
    )
    token_test3 = response_test3.json().get('access_token')
    incoming_connection_response = client.get(
        '/connections/requests/incoming',
        params={"token":token_test3}
    )
    assert incoming_connection_response.status_code == 200
    connection_id = incoming_connection_response.json()[0]['connection_id']
     # Accept the connection request
    reject_response = client.request("DELETE", f'/connections/requests/{connection_id}/decline',
        json={
            'token': token_test3,
            'connection_id':connection_id
        }
    )
    assert reject_response.status_code == 200
    assert reject_response.json().get('message') == 'Connection request rejected'


def test_create_connection_request_connection_exists():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    request_resp = client.post(
        '/connections/requests',
        json={
            'sender_token': token,
            'receiver_username': 'test2'
        }

    )
    assert request_resp.status_code == 400
    assert request_resp.json().get('detail') == "Friend has already been added"


def test_create_connection_request_same_sender_receiver():
    response = client.post(
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    assert response.status_code == 200
    token = response.json().get('access_token')
    request_resp = client.post(
        '/connections/requests',
        json={
            'sender_token': token,
            'receiver_username': 'test'
        }

    )
    assert request_resp.status_code == 400
    assert request_resp.json().get('detail') == "Cannot have the same sender and receiver id"

def test_create_project_and_add_users():
    response = client.post( 
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    token = response.json().get('access_token')
    project_resp = client.post(
        '/project/create',
        json={
            'token': token,
            'title': 'test'
        }
    )
    assert project_resp.status_code == 200
    assert isinstance(project_resp.json(), int)
    p_id = project_resp.json()
    response_get_projects = client.get( 
        '/user/projects',
        params={
            'token': token,
            'p_id': p_id
        }
    )
    assert response_get_projects.status_code == 200
    resp_get_potential_users_proj = client.get( 
        f'/project/{p_id}/users/addable',
        params={
            'token': token,
            'project_id': p_id
        }
    )
    assert resp_get_potential_users_proj.status_code == 200
    assert len(resp_get_potential_users_proj.json()) > 0
    add_user = client.put( 
        '/project_{project_id}/users/add',
        json={
            'token': token,
            'project': p_id
        }
    )
    add_user.status_code == 200


def get_project_not_exist():
    response = client.post( 
        '/login',
        json={
            'username': 'test',
            'password': 'test'
        }
    )
    token = response.json().get('access_token')
    resp_get_projects = client.get( 
        '/user/projects',
        params={
            'token': token,
            'p_id': 69
        }
    )
    assert resp_get_projects.status_code == 404


   

   

   

      















