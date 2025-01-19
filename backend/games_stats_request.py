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
    columns = ['monday_1', 'tuesday_1', 'wednesday_1', 'thursday_1', 'friday_1', 'saturday_1', 'sunday_1',
               'monday_2', 'tuesday_2', 'wednesday_2', 'thursday_2', 'friday_2', 'saturday_2', 'sunday_2',
               'monday_3', 'tuesday_3', 'wednesday_3', 'thursday_3', 'friday_3', 'saturday_3', 'sunday_3',
               'monday_4', 'tuesday_4', 'wednesday_4','thursday_4', 'friday_4', 'saturday_4', 'sunday_4']
    
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
                games_for_user[i].append({'game': j['game_name'], 'time': (j["now minutes"] - j["start minutes"])})
            responce.append(games_for_user)
            
    return responce