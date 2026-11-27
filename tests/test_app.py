# HTTPStatus fornece constantes para os códigos de resposta HTTP.
# Exemplo: OK = 200, CREATED = 201, NOT_FOUND = 404.
from http import HTTPStatus

# Pytest é utilizado para executar os testes e criar fixtures.
# TestClient permite realizar requisições HTTP na aplicação FastAPI
# sem precisar iniciar um servidor.
from fastapi.testclient import TestClient

from fast_zero.app import app


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
