import pymysql as pymy
from classes import UserModel, UserModelUpdate
from httpexceptions import registered_user, inc_user_or_pas
from secr import USER_DATA_BASE, PASSWORD_DATA_BASE, DB_NAME, HOST_NAME
from sh_ps import decrypt, encrypt
from fastapi import APIRouter

users_router = APIRouter(prefix='/users', tags=['registration and authorization'])

DB_CONFIG = {
    'user': USER_DATA_BASE,
    'password': PASSWORD_DATA_BASE,
    'host': HOST_NAME,
    'database': DB_NAME
}

CONN = pymy.connect(**DB_CONFIG)


def get_user(usern: str):
    with CONN.cursor() as cur:
        cur.execute("SELECT password FROM users WHERE name = %s", usern)
        a = cur.fetchone()
        return a[0] if a else None



@users_router.post('/reg')
def register(usermodel: UserModel):
    try:
        with CONN.cursor() as con:
            con.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (usermodel.usern, encrypt(usermodel.pas)))
            CONN.commit()
    except pymy.IntegrityError:
        raise registered_user
    else:
        return {'responce': 'User registered successfully'}


@users_router.post('/authorization')
def authorization(usermodel: UserModel):
    ans = get_user(usermodel.usern)
    if ans is None:
        raise inc_user_or_pas
    elif decrypt(ans) == usermodel.pas:
        return {'responce': 'success'}
    raise inc_user_or_pas


@users_router.patch("/update")
def update_user(user: UserModelUpdate):
    try:
        with CONN.cursor() as cur:
            cur.execute('UPDATE users SET name = %s, password = %s WHERE name = %s', (user.newusern, encrypt(user.newpas), user.usern))
            CONN.commit()
    except pymy.IntegrityError:
        raise registered_user
    else:
        return {'responce': 'Name Changed'}