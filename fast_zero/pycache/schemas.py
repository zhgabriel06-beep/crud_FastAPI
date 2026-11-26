from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


# Dados recebidos no cadastro
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


# Dados públicos do usuário: não inclui a senha
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


# Representação do usuário armazenado
class UserDB(UserSchema):
    id: int


# Resposta com vários usuários
class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
