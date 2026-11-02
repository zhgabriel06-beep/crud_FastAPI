from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fastapi_zero.schemas import (
    Message,
    Userdb,
    Userlist,
    UserPublic,
    Userschema,
)

app = FastAPI(title='Minha API BALA!')
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Seja bem vindo a minha aplicação!'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
def create_user(user: Userschema):
    user_with_id = Userdb(
        **user.model_dump(),
        id=len(database) + 1,
    )

    database.append(user_with_id)

    return user_with_id


@app.get('/user/', status_code=HTTPStatus.OK, response_model=Userlist)
def read_users():
    return {'users': database}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int, user: Userschema):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NO_CONTENT, detail='User not found...'
        )
    return user_id


@app.put(
    '/user/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def update_user(user_id: int, user: Userschema):
    # Verifica se o usuário existe
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found...'
        )

    # Cria o usuário atualizado
    user_with_id = Userdb(
        **user.model_dump(),
        id=user_id,
    )

    # Substitui o usuário antigo
    database[user_id - 1] = user_with_id

    # Retorna o usuário atualizado
    return user_with_id


@app.delete(
    '/user/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found...')
    else:
        return database.pop(user_id - 1)
