# Importa os códigos HTTP padronizados.
# HTTPStatus.CREATED = 201
# HTTPStatus.OK = 200
# HTTPStatus.CONFLICT = 409
# HTTPStatus.NOT_FOUND = 404
from http import HTTPStatus

# Depends: permite utilizar injeção de dependências no FastAPI.
# FastAPI: cria a aplicação.
# HTTPException: permite retornar erros HTTP personalizados.
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

# select: constrói consultas SQL utilizando a API do SQLAlchemy.
from sqlalchemy import select

# IntegrityError: exceção lançada quando uma operação viola
# alguma restrição de integridade do banco de dados.
from sqlalchemy.exc import IntegrityError

# Session: representa uma sessão de comunicação com o banco de dados.
from sqlalchemy.orm import Session

# Importa a função responsável por fornecer uma sessão do banco.
from fast_zero.pycache.database import get_session

# Importa o modelo que representa a tabela User no banco de dados.
from fast_zero.pycache.models import User

# Importa os schemas responsáveis pela validação e organização dos dados.
from fast_zero.pycache.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_zero.pycache.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

# Cria a aplicação FastAPI.
app = FastAPI()

# ---------------------------------------------------------
# ROTA PRINCIPAL
# ---------------------------------------------------------


# GET: utilizado para consultar informações.
# '/': endereço principal da aplicação.
# status_code: define o código HTTP da resposta.
# response_model: define o formato da resposta utilizando um schema.
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    # Retorna uma mensagem no formato definido pelo schema Message.
    return {'message': 'Seja bem vindo a minha aplicação!'}


# ---------------------------------------------------------
# CRIAR USUÁRIO
# ---------------------------------------------------------


# POST: utilizado para enviar dados e criar um novo registro.
# HTTPStatus.CREATED: retorna o código 201 quando o usuário é criado.
# UserPublic: define quais informações serão retornadas ao cliente.
@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def created_user(
    user: UserSchema,
    session: Session = Depends(get_session),
):
    # Procura um usuário que tenha o mesmo username OU o mesmo email.
    #
    # select(User): prepara uma consulta na tabela User.
    # where(): adiciona condições à consulta.
    # |:3 representa o operador OR entre as condições.
    # session.scalar(): executa a consulta e retorna o primeiro resultado
    # encontrado ou None caso não exista nenhum registro.
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    # Verifica se já existe algum usuário com os dados informados.
    if db_user:
        # Verifica especificamente se o username já está cadastrado.
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

        # Caso o username seja diferente, verifica se o email já existe.
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    # Cria uma instância do modelo User com os dados recebidos.
    # Nesse momento, o registro ainda não foi salvo no banco.
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    # Adiciona o objeto à sessão do SQLAlchemy.
    # O registro fica pendente de gravação.
    session.add(db_user)

    # Confirma a transação e grava os dados no banco de dados.
    session.commit()

    # Atualiza o objeto com os dados persistidos no banco.
    # Útil para obter valores gerados automaticamente, como o ID.
    session.refresh(db_user)

    # Retorna o usuário criado.
    # O response_model UserPublic controla quais campos serão expostos.
    return db_user


# ---------------------------------------------------------
# LISTAR USUÁRIOS
# ---------------------------------------------------------


# GET: consulta os usuários cadastrados.
@app.get('/users/', response_model=UserList)
def read_users(
    # skip: quantidade de registros que serão ignorados.
    # limit: quantidade máxima de registros retornados.
    # Os valores padrão permitem listar os primeiros 100 usuários.
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # select(User): seleciona os registros da tabela User.
    # offset(skip): pula a quantidade de registros informada.
    # limit(limit): limita a quantidade de resultados.
    # session.scalars(): executa a consulta e retorna os objetos encontrados.
    # all(): transforma os resultados em uma lista.
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    # Retorna os usuários dentro da chave 'users'.
    # O formato precisa corresponder ao schema UserList.
    return {'users': users}


# ---------------------------------------------------------
# ATUALIZAR USUÁRIO
# ---------------------------------------------------------


# PUT: utilizado para atualizar os dados de um registro existente.
# {user_id}: parâmetro dinâmico recebido pela URL.
@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        # Atualiza os atributos do objeto encontrado.
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email

        # Persiste as alterações no banco.
        session.commit()

        # Atualiza os dados do objeto após a gravação.
        session.refresh(current_user)

        # Retorna o usuário atualizado.
        return current_user

    except IntegrityError:
        # Ocorre quando a atualização viola uma restrição do banco,
        # como tentar utilizar um username ou email já cadastrado.
        #
        # IMPORTANTE: após um IntegrityError, é necessário executar
        # session.rollback() antes de continuar utilizando a sessão.
        session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


# ---------------------------------------------------------
# EXCLUIR USUÁRIO
# ---------------------------------------------------------


# DELETE: utilizado para remover um registro.
@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    # Marca o objeto para exclusão dentro da sessão.
    session.delete(current_user)

    # Confirma a transação e efetiva a exclusão no banco.
    session.commit()

    # Retorna uma mensagem confirmando a operação.
    return {'message': 'User deleted'}


# ---------------------------------------------------------
# BUSCAR UM USUÁRIO ESPECÍFICO
# ---------------------------------------------------------


# GET: consulta um usuário específico pelo ID.
# Essa rota também pode ser utilizada para estudar a diferença
# entre buscar um único registro e listar vários registros.
@app.get('/users/{user_id}', response_model=UserPublic)
def read_user__exercicio(
    user_id: int,
    session: Session = Depends(get_session),
):
    # Busca o usuário que possui o ID informado.
    db_user = session.scalar(select(User).where(User.id == user_id))

    # Verifica se o usuário foi encontrado.
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    # Retorna os dados do usuário encontrado.
    return db_user


@app.post('/token/', response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    print('1 - Entrou na rota')

    user = session.scalar(select(User).where(User.email == form_data.username))

    print('2 - Consulta realizada')
    print('Usuário encontrado:', user is not None)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    print('3 - Usuário encontrado')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    print('4 - Senha validada')

    access_token = create_access_token({'sub': user.email})

    print('5 - Token criado')

    return {'access_token': access_token, 'token_type': 'Bearer'}
