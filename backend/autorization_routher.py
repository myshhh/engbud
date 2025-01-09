import pymysql as pymy
from classes import UserModel, UserModelUpdate, TokenModel, UserModelReg
from httpexceptions import registered_user, inc_user_or_pas, inv_ref_tk, exp_token, credentials_exception
from secr import SECRET_KEY, ALGORITHM, TOKEN_EXPIRE_MINUTES, USER_DATA_BASE, PASSWORD_DATA_BASE, DB_NAME, HOST_NAME
from sh_ps import decrypt, encrypt
from fastapi import APIRouter
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import timedelta, datetime

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


def create_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta if expires_delta else timedelta(days=7))
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)


@users_router.post('/reg')
def register(usermodel: UserModelReg):
    try:
        with CONN.cursor() as cur:
            cur.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (usermodel.usern, encrypt(usermodel.pas)))
            CONN.commit()
    except pymy.IntegrityError:
        raise registered_user
    else:
        with CONN.cursor() as cur:
            cur.execute('SELECT users_id FROM users WHERE name = %s', usermodel.usern)
            id = cur.fetchone()[0]
            return {'responce': id}


@users_router.post('/authorization')
def authorization(usermodel: UserModel):
    ans = get_user(usermodel.usern)
    if ans is None:
        raise inc_user_or_pas
    elif decrypt(ans) == usermodel.pas:
        token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        token = create_token(data={"sub": usermodel.id}, expires_delta=token_expires)
        return {"token": token, "token_type": "bearer"}
    raise inc_user_or_pas


@users_router.post("/refresh_token")
def refresh_token(tokenmodel: TokenModel):
    try:
        payload = jwt.decode(tokenmodel.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise inv_ref_tk
        token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        new_token = create_token(data={"sub": username}, expires_delta=token_expires)
        return {"token": new_token, "token_type": "bearer"}
    except JWTError:
        raise inv_ref_tk


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


@users_router.get("/me")
def read_users_me(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        if id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise exp_token
    except JWTError:
        raise credentials_exception
    return {"id": id}