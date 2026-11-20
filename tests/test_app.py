# HTTPStatus fornece constantes para os códigos de resposta HTTP.
# Exemplo: OK = 200, CREATED = 201, NOT_FOUND = 404.
from http import HTTPStatus

# Pytest é utilizado para executar os testes e criar fixtures.
import pytest

# TestClient permite realizar requisições HTTP na aplicação FastAPI
# sem precisar iniciar um servidor.
from fastapi.testclient import TestClient

from fast_zero.app import app
from fast_zero.schemas import UserPublic


def test_root():
    """
    Esse teste segue o padrão AAA:

    A: Arrange - Organizar/preparar o cenário.
    A: Act - Executar a ação que será testada (SUT).
    A: Assert - Verificar se o resultado foi o esperado.

    SUT = System Under Test (sistema sob teste).
    """

    # Arrange:
    # Prepara o cliente que fará as requisições.
    client = TestClient(app)

    # Act:
    # Faz uma requisição GET para a rota principal '/'.
    response = client.get('/')

    # Assert:
    # Verifica se o conteúdo retornado é exatamente o esperado.
    assert response.json() == {'message': 'Seja bem vindo a minha aplicação!'}

    # Verifica se a resposta HTTP foi 200 (OK).
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

    print(response.json())

    assert response.status_code == HTTPStatus.CREATED


def test_read_users(client):
    # Act:
    # Faz uma requisição GET para buscar todos os usuários.
    response = client.get('/users/')

    # Assert:
    # Verifica se a requisição foi bem-sucedida (200).
    assert response.status_code == HTTPStatus.OK

    # Verifica se a lista de usuários retornada está correta.
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_integrity_error(client, user):
    # Inserindo fausto
    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    # Alterando o user das fixture para fausto
    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


# Teste para verificar o comportamento da API quando
# tentamos excluir um usuário que não existe.
def test_delete_user2(client):
    # Act:
    # Tenta excluir o usuário de ID 2.
    response = client.delete('/user/2')

    # Assert:
    # Espera receber 404 (Not Found).
    assert response.status_code == HTTPStatus.NOT_FOUND
