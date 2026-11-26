# HTTPStatus fornece constantes para os códigos de resposta HTTP.
# Exemplo: OK = 200, CREATED = 201, NOT_FOUND = 404.
from http import HTTPStatus
from urllib import response

# Pytest é utilizado para executar os testes e criar fixtures.
# TestClient permite realizar requisições HTTP na aplicação FastAPI
# sem precisar iniciar um servidor.
from fastapi.testclient import TestClient

from fast_zero.pycache.app import app
from fast_zero.pycache.schemas import UserPublic


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


def test_read_users(client, token):
    # Act:
    # Faz uma requisição GET para buscar todos os usuários.
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    # Assert:
    # Verifica se a requisição foi bem-sucedida (200).
    assert response.status_code == HTTPStatus.OK

    # Verifica se a lista de usuários retornada está correta.
    assert response.json() == {
        'users': [{'id': 1, 'username': 'Teste', 'email': 'Teste@teste.com'}],
    }


def test_update_user(client, user, token):
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
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


def test_update_integrity_error(client, user, token):
    # Inserindo fausto
    client.post(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    # Alterando o usuário para fausto
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

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


def test_get_token(client, user):
    response = client.post(
        '/token/',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
