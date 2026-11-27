from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    session: T_Session,
    user: UserSchema,
):
    # Procura um usuário que tenha o mesmo email.
    #
    # select(User): prepara uma consulta na tabela User.
    # where(): adiciona uma condição à consulta.
    # session.scalar(): executa a consulta e retorna o primeiro resultado
    # encontrado ou None caso não exista nenhum registro.
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    # Verifica se o email já está cadastrado.
    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email or Username already exists',
        )

    # Cria uma instância do modelo User.
    # A senha é armazenada como hash, nunca em texto puro.
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    # Adiciona o objeto à sessão do SQLAlchemy.
    session.add(db_user)

    try:
        # Confirma a transação e grava os dados no banco.
        session.commit()

        # Atualiza o objeto com os dados persistidos.
        session.refresh(db_user)

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )

    return db_user


# GET: consulta os usuários cadastrados.
@router.get('/', response_model=UserList)
def read_users(
    current_user: T_CurrentUser,
    session: T_Session,
    skip: int = 0,
    limit: int = 100,
):
    # Ignora os registros indicados em skip e limita os resultados.
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


# PUT: atualiza os dados de um usuário existente.
@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    session: T_Session,
    current_user: T_CurrentUser,
    user_id: int,
    user: UserSchema,
):
    # Verifica se o usuário autenticado é o dono da conta.
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    # Atualiza os atributos do usuário.
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email

    try:
        # Persiste as alterações no banco.
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        # Desfaz a transação em caso de conflito.
        session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )


# DELETE: remove um usuário.
@router.delete('/{user_id}', response_model=Message)
def delete_user(
    session: T_Session,
    current_user: T_CurrentUser,
    user_id: int,
):
    # Verifica se o usuário autenticado é o dono da conta.
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    # Marca o objeto para exclusão.
    session.delete(current_user)

    # Confirma a exclusão no banco.
    session.commit()

    return {'message': 'User deleted'}


# GET: consulta um usuário específico pelo ID.
@router.get('/{user_id}', response_model=UserPublic)
def read_user(
    session: T_Session,
    user_id: int,
):
    # Busca o usuário pelo ID informado.
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    return db_user
