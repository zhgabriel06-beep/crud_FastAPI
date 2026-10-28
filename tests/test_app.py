import email
from http import HTTPStatus
from urllib import response

import pytest
from fastapi.testclient import TestClient

from fastapi_zero.app import app


@pytest.fixture
def cliente():
    return TestClient(app)


def test_root():
    """
    Esse test tem 3 etapas (AAA)
    A: Arrange - Organiza
    A: Act. - Executa a coisa (o SUT)
    A: Assert - Garanta que A é A
    """
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get('/')
    # Assert
    assert response.json() == {'message': 'Olá mundo'}
    assert response.status_code == HTTPStatus.OK


def test_create_user():
    client = TestClient(app)

    response = client.post(
        '/users/',
        json={
            'username': 'Gabriel',
            'email': 'Gabriel@gmail.com',
            'password': '3010',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'Gabriel@gmail.com',
        'username': 'Gabriel',
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {'id': 1, 'email': 'Gabriel@gmail.com', 'username': 'Gabriel'}
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={'username': 'Gabrielly', 'email': 'Gabrielly@gmail.com'},
    )
    assert response.status_code == HTTPStatus.OK
