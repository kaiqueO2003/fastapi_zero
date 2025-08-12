from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_root_deve_retornar_ola_mundo(client):
    response = client.get('/')

    assert response.json() == {'message': 'Olá mundo!'}
    assert response.status_code == HTTPStatus.OK


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


def test_update_not_found(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'aa',
            'email': 'aaa@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Não encontrado'}


def test_delete_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Não encontrado'}


def test_read_user_by_id(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/{}'.format(user.id))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_by_id_not_found(client):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Não encontrado'}


def teste_get_token(client, user):
    response = client.post(
        '/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
