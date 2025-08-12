from http import HTTPStatus

from fastapi_zero.schemas import UserPublic
from fastapi_zero.security import create_acess_token


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED


def test_create_user_username_already_registered(client):
    response1 = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice1@example.com',
            'password': 'secret',
        },
    )
    assert response1.status_code == HTTPStatus.CREATED

    response2 = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice2@example.com',
            'password': 'secret',
        },
    )
    assert response2.status_code == HTTPStatus.CONFLICT
    assert 'username' in response2.json()['detail'].lower()


def test_create_user_email_already_registered(client):
    response1 = client.post(
        '/users/',
        json={
            'username': 'lucas',
            'email': 'lucas@example.com',
            'password': 'secret',
        },
    )
    assert response1.status_code == HTTPStatus.CREATED

    response2 = client.post(
        '/users/',
        json={
            'username': 'lucas1',
            'email': 'lucas@example.com',
            'password': 'secret',
        },
    )
    assert response2.status_code == HTTPStatus.CONFLICT
    assert 'email' in response2.json()['detail'].lower()


def test_jwt_valid_token_user_not_found(client):
    token = create_acess_token({'sub': 'naoexiste@example.com'})

    # Tentar acessar uma rota que exige autenticação
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials'
    }


def test_read_user(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secret',
            'id': user.id,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'user delete'}


def test_update_not_found(client, token, other_user):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'aa',
            'email': 'aaa@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissão'}


def test_delete_not_found(client, token, other_user):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissão'}


def test_read_user_by_id(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_by_id_not_found(client, other_user, token):
    response = client.get(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissão'}
