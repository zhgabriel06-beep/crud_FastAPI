# Permite criar gerenciadores de contexto personalizados,
# que funcionam com a estrutura 'with'.
from contextlib import contextmanager

# Importa datetime para trabalhar com datas e horários.
from datetime import datetime

import pytest

# Permite testar a aplicação FastAPI sem precisar iniciar um servidor.
from fastapi.testclient import TestClient

# create_engine: cria a conexão com o banco de dados.
# event: permite executar funções em determinados eventos do SQLAlchemy.
from sqlalchemy import create_engine, event

# Session: gerencia as operações com o banco de dados.
from sqlalchemy.orm import Session

from fastapi_zero.app import app

# User: modelo da tabela de usuários.
# table_registry: registro que armazena os metadados das tabelas.
from fastapi_zero.models import User, table_registry


# Fixture que disponibiliza um cliente de testes para a aplicação.
# Assim, podemos fazer requisições HTTP nos testes sem iniciar o servidor.
@pytest.fixture
def cliente():
    return TestClient(app)


# Fixture que cria uma sessão de banco de dados para cada teste.
@pytest.fixture
def session():
    # Cria um banco SQLite em memória.
    # ATENÇÃO: o correto é ':memory:' (com dois-pontos no final).
    # Sem o ':' final, o SQLite cria um arquivo chamado ':memory' no disco.
    engine = create_engine('sqlite:///:memory:')

    # Cria todas as tabelas definidas no table_registry.
    table_registry.metadata.create_all(engine)

    # Abre uma sessão com o banco. O yield entrega a sessão ao teste
    # e pausa a fixture até o teste terminar.
    with Session(engine) as session:
        yield session

    # Depois que o teste termina, remove todas as tabelas.
    table_registry.metadata.drop_all(engine)


# Transforma a função em um gerenciador de contexto,
# permitindo usar: with mock_db_time(User) as time: ...
#
# model: a classe (tabela) que vai receber os listeners. Padrão: User.
# time: a data fixa que será gravada nos campos de data.
@contextmanager
def mock_db_time(model=User, time=datetime(2026, 1, 1)):

    # Hook de INSERT: roda antes de um registro novo ir para o banco.
    # mapper: informações do mapeamento ORM.
    # connection: conexão usada com o banco.
    # target: o objeto que está sendo inserido.
    def fake_time_hook(mapper, connection, target):
        # hasattr evita erro caso o model não tenha o campo.
        # No insert, os DOIS campos recebem a data falsa.
        if hasattr(target, 'created_at'):
            target.created_at = time

    # Hook de UPDATE: roda antes de um registro existente ser alterado.
    # Aqui mexemos SÓ no updated_at: o created_at deve continuar intacto,
    # pois a data de criação não muda quando o registro é atualizado.
    def fake_update_hook(mapper, connection, target):
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    # Registra os listeners no model.
    # before_insert -> dispara antes de cada INSERT.
    # before_update -> dispara antes de cada UPDATE.
    event.listen(model, 'before_insert', fake_time_hook)
    event.listen(model, 'before_update', fake_update_hook)

    try:
        # Entrega a data para quem usa o 'with ... as time'.
        # O código do teste roda neste ponto.
        yield time
    finally:
        # O finally garante a limpeza mesmo se o teste der erro dentro
        # do 'with'. Sem isso, o listener ficaria ativo e contaminaria
        # os outros testes.
        event.remove(model, 'before_insert', fake_time_hook)
        event.remove(model, 'before_update', fake_update_hook)


# Fixture que entrega o gerenciador de contexto aos testes.
# Note que retorna a FUNÇÃO (sem parênteses), não o resultado dela:
# quem chama decide quando abrir o 'with'.
@pytest.fixture
def mock_time():
    return mock_db_time
