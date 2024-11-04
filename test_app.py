import pytest
from app import app, db
from models import User, Account
from flask_jwt_extended import create_access_token
from config import Config 



@pytest.fixture(scope='module')
def test_client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope='module')
def admin_user():
    admin = User(username="admin_user")
    admin.set_password("adminpass")
    admin.role = "admin"
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture(scope='module')
def normal_user():
    user = User(username="test_user")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return user

def get_headers(user):
    token = create_access_token(identity=user.id)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def test_signup(test_client):
    response = test_client.post('/signup', json={
        "username": "new_user",
        "password": "newpass"
    })
    assert response.status_code == 201
    assert response.json["message"] == "User created successfully"

def test_login(test_client, normal_user):
    response = test_client.post('/login', json={
        "username": "test_user",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json

def test_profile(test_client, normal_user):
    headers = get_headers(normal_user)
    response = test_client.get('/profile', headers=headers)
    assert response.status_code == 200
    assert response.json["username"] == "test_user"

def test_add_account_as_admin(test_client, admin_user):
    headers = get_headers(admin_user)
    response = test_client.post('/accounts', headers=headers, json={
        "name": "Test Account",
        "email": "testaccount@example.com",
        "contact_number": "1234567890"
    })
    assert response.status_code == 201
    assert response.json["message"] == "Account created successfully"

def test_update_account_as_admin(test_client, admin_user):
    headers = get_headers(admin_user)
    account = Account.query.first()
    response = test_client.put(f'/accounts/{account.id}', headers=headers, json={
        "name": "Updated Account",
        "email": "updated@example.com"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Account updated successfully"

def test_get_account(test_client, admin_user):
    headers = get_headers(admin_user)
    response = test_client.get('/accounts', headers=headers)
    assert response.status_code == 200
    assert "accounts" in response.json

def test_delete_account(test_client, admin_user):
    headers = get_headers(admin_user)
    account = Account.query.first()
    response = test_client.delete(f'/accounts/{account.id}', headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Account deleted successfully"

def test_update_user_role_as_super_admin(test_client, admin_user):
    headers = {'Authorization': Config.SU_ADMIN_ID, 'Content-Type': 'application/json'}
    response = test_client.patch(f'/user/{admin_user.id}', headers=headers, json={
        "role": "client"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User role updated to client successfully"
