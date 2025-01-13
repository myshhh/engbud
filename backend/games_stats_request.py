from steam_web_api import Steam

import pymysql as pymy
from secr import USER_DATA_BASE, PASSWORD_DATA_BASE, DB_NAME, HOST_NAME
from fastapi import APIRouter
from secr import STEAM_KEY
import json


games_request_router = APIRouter(prefix='/stats_request', tags=['games stats request'])

DB_CONFIG = {
    'user': USER_DATA_BASE,
    'password': PASSWORD_DATA_BASE,
    'host': HOST_NAME,
    'database': DB_NAME
}

CONN = pymy.connect(**DB_CONFIG)
steam = Steam(STEAM_KEY)


@games_request_router.get('/steam')
def steam_request(steam_id):
    games = []
    responce = []
    columns = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "fweek", "sweek", "tweek", "foweek"]
    for i in steam.users.get_user_recently_played_games(steam_id)['games']:
        games.append({'game': i["name"], 'time': 0})
    for i in columns:
        with CONN.cursor() as cur:
            cur.execute(f'SELECT {i} FROM games_steam_stats WHERE steam_id = %s', steam_id)
            ans = cur.fetchone()[0]
        if ans is None:
            responce.append({i: games})
        else:
            games_for_user = {i: []}
            for j in json.loads(ans)['games']:
                games_for_user[i].append({'game': j['game_name'], 'time': j["now minutes"] - j["start minutes"]})
            responce.append(games_for_user)
            
    return responce