import os
from datetime import datetime, timezone

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'test-secret-key-only-for-tests'
os.environ['ALGORITHM'] = 'HS256'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '7'

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models.task import Task
from app.config import settings
from app.security import create_token


@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)

    @event.listens_for(engine, 'connect')
    def enable_foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def override_db():
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client, factory
    app.dependency_overrides.clear()
    engine.dispose()


def register(client, name='alice'):
    response = client.post('/users/', json={'username': name, 'email': f'{name}@example.com', 'password': 'password123'})
    assert response.status_code == 201
    user = response.json()
    assert 'password' not in user
    response = client.post('/auth/login', json={'email': user['email'], 'password': 'password123'})
    assert response.status_code == 200
    return user, {'Authorization': f"Bearer {response.json()['access_token']}"}


def test_user_permissions(client):
    api, _ = client
    alice, auth = register(api)
    bob, _ = register(api, 'bob')
    assert api.get('/users/').status_code == 401
    assert api.get('/users/', headers=auth).json() == [alice]
    assert api.get(f"/users/{bob['id']}", headers=auth).status_code == 403
    assert api.put(f"/users/{bob['id']}", headers=auth, json={'username': 'changed', 'email': 'changed@example.com'}).status_code == 403
    assert api.delete(f"/users/{bob['id']}", headers=auth).status_code == 403


def test_task_update_persistence_and_isolation(client):
    api, _ = client
    _, auth = register(api)
    _, other_auth = register(api, 'bob')
    response = api.post('/tasks/', headers=auth, json={'title': 'Original', 'descricao': 'description'})
    assert response.status_code == 201
    url = f"/tasks/{response.json()['id']}"
    assert api.put(url, headers=auth, json={'title': 'Updated', 'concluida': True, 'descricao': None}).status_code == 200
    task = api.get(url, headers=auth).json()
    assert (task['title'], task['concluida'], task['descricao']) == ('Updated', True, None)
    assert api.get(url, headers=other_auth).status_code == 404
    assert api.put(url, headers=other_auth, json={'title': 'stolen'}).status_code == 404
    assert api.delete(url, headers=other_auth).status_code == 404
    assert api.get('/tasks/', headers=other_auth).json() == []
    assert api.put(url, headers=auth, json={'titulo': 'wrong'}).status_code == 422
    assert api.put(url, headers=auth, json={'title': None}).status_code == 422
    assert api.put(url, headers=auth, json={'concluida': None}).status_code == 422


def test_delete_account_removes_tasks(client):
    api, factory = client
    user, auth = register(api)
    api.post('/tasks/', headers=auth, json={'title': 'Task'})
    response = api.delete(f"/users/{user['id']}", headers=auth)
    assert response.status_code == 204
    assert response.content == b''
    with factory() as session:
        assert session.query(Task).count() == 0
    assert api.get('/tasks/', headers=auth).status_code == 401


def test_duplicate_email_and_recovery(client):
    api, _ = client
    alice, auth = register(api)
    bob, _ = register(api, 'bob')
    response = api.put(f"/users/{alice['id']}", headers=auth, json={'username': 'alice', 'email': bob['email']})
    assert response.status_code == 409
    assert api.get(f"/users/{alice['id']}", headers=auth).json()['email'] == alice['email']
    assert api.post('/users/', json={'username': 'another', 'email': alice['email'], 'password': 'password123'}).status_code == 409


def test_login_errors_are_uniform(client):
    api, _ = client
    register(api)
    missing = api.post('/auth/login', json={'email': 'missing@example.com', 'password': 'wrong'})
    wrong = api.post('/auth/login', json={'email': 'alice@example.com', 'password': 'wrong'})
    assert missing.status_code == wrong.status_code == 401
    assert missing.json() == wrong.json()
    assert missing.headers['www-authenticate'] == wrong.headers['www-authenticate'] == 'Bearer'


@pytest.mark.parametrize('subject', ['abc', '-1', '0', '999999999999999999999999', '²'])
def test_invalid_token_subject(client, subject):
    api, _ = client
    token = create_token({'sub': subject})
    assert api.get('/tasks/', headers={'Authorization': f'Bearer {token}'}).status_code == 401


def test_token_expiration_uses_settings():
    before = datetime.now(timezone.utc).timestamp()
    token = create_token({'sub': '1'})
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert 419 <= payload['exp'] - before <= 421


def test_validation_and_pagination(client):
    api, _ = client
    _, auth = register(api)
    for data in ({'title': ''}, {'title': '   '}, {'title': 'x' * 151}, {'title': 'valid', 'descricao': 'x' * 351}, {'title': 'valid', 'concluida': None}):
        assert api.post('/tasks/', headers=auth, json=data).status_code == 422
    for title in ('first', 'second', 'third'):
        assert api.post('/tasks/', headers=auth, json={'title': title}).status_code == 201
    page = api.get('/tasks/?offset=1&limit=1', headers=auth)
    assert [task['title'] for task in page.json()] == ['second']
    assert api.get('/tasks/?limit=101', headers=auth).status_code == 422
    assert api.get('/tasks/?offset=-1', headers=auth).status_code == 422
