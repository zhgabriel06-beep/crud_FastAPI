# HTTPStatus fornece constantes para os códigos de resposta HTTP.
# Exemplo: OK = 200, CREATED = 201, NOT_FOUND = 404.
from http import HTTPStatus

# Pytest é utilizado para executar os testes e criar fixtures.
import pytest

# TestClient permite realizar requisições HTTP na aplicação FastAPI
# sem precisar iniciar um servidor.
from fastapi.testclient import TestClient

from fastapi_zero.app import app


# Fixture responsável por criar um cliente de testes.
# Toda função de teste que receber 'client' como parâmetro
# terá acesso automaticamente a esse cliente.
@pytest.fixture
def client():
    return TestClient(app)


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


def test_create_user():
    # Arrange:
    # Cria o cliente para realizar as requisições.
    client = TestClient(app)

    # Act:
    # Envia uma requisição POST para cadastrar um usuário.
    # O parâmetro json envia os dados no formato JSON.
    response = client.post(
        '/users/',
        json={
            'username': 'Gabriel',
            'email': 'Gabriel@gmail.com',
            'password': '3010',
        },
    )

    # Assert:
    # Verifica se o cadastro foi realizado com sucesso.
    # HTTPStatus.CREATED representa o código 201.
    assert response.status_code == HTTPStatus.CREATED

    # Verifica se a API retornou os dados esperados.
    # A senha não deve aparecer na resposta pública do usuário.
    assert response.json() == {
        'id': 1,
        'email': 'Gabriel@gmail.com',
        'username': 'Gabriel',
    }


def test_read_users(client):
    # Act:
    # Faz uma requisição GET para buscar todos os usuários.
    response = client.get('/user/')

    # Assert:
    # Verifica se a requisição foi bem-sucedida (200).
    assert response.status_code == HTTPStatus.OK

    # Verifica se a lista de usuários retornada está correta.
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'email': 'Gabriel@gmail.com',
                'username': 'Gabriel',
            }
        ]
    }


def test_update_user(client):
    # Act:
    # Envia uma requisição PUT para atualizar o usuário de ID 1.
    # PUT normalmente é utilizado para atualizar um recurso.
    response = client.put(
        '/user/1',
        json={
            'username': 'Gabrielly',
            'email': 'Gabrielly@gmail.com',
            'password': '3010',
        },
    )

    # Assert:
    # Verifica se a atualização foi realizada com sucesso.
    assert response.status_code == HTTPStatus.OK

    # Verifica se os dados do usuário foram realmente atualizados.
    assert response.json() == {
        'id': 1,
        'username': 'Gabrielly',
        'email': 'Gabrielly@gmail.com',
    }


def test_update_user2(client):
    # Act:
    # Tenta atualizar um usuário que possui ID 2.
    # Esse usuário não deveria existir.
    response = client.put(
        '/user/2',
        json={
            'username': 'Gabrielly',
            'email': 'Gabrielly@gmail.com',
            'password': '3010',
        },
    )

    # Assert:
    # Verifica se a API retornou 404 (Not Found).
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    # Act:
    # Envia uma requisição DELETE para excluir o usuário de ID 1.
    response = client.delete('/user/1')

    # Assert:
    # Verifica se a exclusão foi realizada com sucesso.
    assert response.status_code == HTTPStatus.OK

    # Verifica se a API retornou os dados do usuário excluído.
    assert response.json() == {
        'username': 'Gabrielly',
        'email': 'Gabrielly@gmail.com',
        'id': 1,
    }


# Teste para verificar o comportamento da API quando
# tentamos excluir um usuário que não existe.
def test_delete_user2(client):
    # Act:
    # Tenta excluir o usuário de ID 2.
    response = client.delete('/user/2')

    # Assert:
    # Espera receber 404 (Not Found).
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_user(client):
    # Act:
    # Tenta acessar um usuário específico utilizando GET.
    response = client.get('/user/1')

    # Assert:
    # Espera receber 405 (Method Not Allowed).
    # Isso significa que a rota existe, mas não permite GET.
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


# Teste para verificar o comportamento de uma requisição
# GET para um usuário inexistente.
def test_read_user2(client):
    # Act:
    # Tenta acessar o usuário de ID 2.
    response = client.get('/user/2')

    # Assert:
    # Também espera 405, pois o método GET não é permitido nessa rota.
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
