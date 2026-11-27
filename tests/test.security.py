from jwt import decode

from fast_zero.security import create_access_token
from fast_zero.settings import settings


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)
    decoded = decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    assert decoded['test'] == data['test']
    assert 'exp' in decoded
