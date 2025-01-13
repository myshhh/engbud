from steam_web_api import Steam

import pymysql as pymy
from classes import SteamModel
from httpexceptions import inv_steam_id, too_long_id, registered_user
from secr import USER_DATA_BASE, PASSWORD_DATA_BASE, DB_NAME, HOST_NAME
from fastapi import APIRouter
from secr import STEAM_KEY

connection_laucnhers = APIRouter(prefix='/connection_launchers', tags=['connection_launcher'])

DB_CONFIG = {
    'user': USER_DATA_BASE,
    'password': PASSWORD_DATA_BASE,
    'host': HOST_NAME,
    'database': DB_NAME
}

CONN = pymy.connect(**DB_CONFIG)
steam = Steam(STEAM_KEY)


@connection_laucnhers.post('/reg_steam')
def register_steam(model: SteamModel):
    ans = steam.users.get_user_details(model.steam_id)
    if ans['player'] is None:
        raise inv_steam_id
    try:
        with CONN.cursor() as cur:
            cur.execute("UPDATE games_steam_stats SET steam_id = %s WHERE users_id = %s", (model.steam_id, model.id))
            CONN.commit()
    except pymy.err.DataError:
        raise too_long_id
    except pymy.err.IntegrityError:
        raise registered_user
    else:
        return {'responce': 'success'}


