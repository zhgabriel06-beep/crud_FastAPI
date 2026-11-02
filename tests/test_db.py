# asdict() converte um objeto dataclass em um dicionário Python.
from dataclasses import asdict

# select() permite construir consultas SQL utilizando SQLAlchemy.
from sqlalchemy import select

# Importa o modelo User, que representa a tabela de usuários.
from fastapi_zero.models import User


def test_create_user(session, mock_db_time):

    # Utiliza o gerenciador de contexto para controlar a data/hora
    # utilizada durante a criação do usuário.
    #
    # A variável 'time' recebe a data definida no mock_db_time.
    with mock_db_time(User) as time:
        # Cria uma instância do modelo User.
        # ** permite passar os valores como argumentos nomeados.
        user = User(
            username='Gabriel',
            email='zhgabriel06@gmail.com',
            password='secret',
        )

        # Adiciona o usuário à sessão do banco de dados.
        # Nesse momento, ele ainda não foi necessariamente salvo.
        session.add(user)

        # Confirma a transação e persiste os dados no banco.
        session.commit()

        # Realiza uma consulta no banco procurando um usuário
        # cujo username seja igual a 'Gabriel'.
        #
        # select(User): seleciona registros do modelo User.
        # where(): adiciona uma condição à consulta.
        # session.scalar(): executa a consulta e retorna
        # o primeiro resultado encontrado.
        user = session.scalar(select(User).where(User.username == 'Gabriel'))

        # asdict() transforma o objeto User em um dicionário.
        # O assert compara esse dicionário com o resultado esperado.
        assert asdict(user) == {
            'id': 1,
            'username': 'Gabriel',
            'email': 'zhgabriel06@gmail.com',
            'password': 'secret',
            # Verifica se a data de criação corresponde
            # à data controlada pelo mock_db_time.
            'create_at': time,
        }
