from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


# Dados públicos do usuário: não inclui a senha
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


# Dados recebidos no cadastro
class Userschema(BaseModel):
    username: str
    email: EmailStr
    password: str


# Representação do usuário armazenado
class Userdb(Userschema):
    id: int


# Resposta com vários usuários
class Userlist(BaseModel):
    users: list[UserPublic]
