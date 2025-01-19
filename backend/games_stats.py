from steam_web_api import Steam

import pymysql as pymy
from classes import SteamModel
from httpexceptions import uncregistered_user
from secr import USER_DATA_BASE, PASSWORD_DATA_BASE, DB_NAME, HOST_NAME
from fastapi import APIRouter
from datetime import datetime
from secr import STEAM_KEY
import json


games_router = APIRouter(prefix='/stats', tags=['games stats'])

DB_CONFIG = {
    'user': USER_DATA_BASE,
    'password': PASSWORD_DATA_BASE,
    'host': HOST_NAME,
    'database': DB_NAME
}

CONN = pymy.connect(**DB_CONFIG)
steam = Steam(STEAM_KEY)


def check_time_for_null_steam(day_time, id, time_year, time_month, time_week, time_day):
    with CONN.cursor() as cur:
        cur.execute(f'SELECT {day_time} from games_steam_stats WHERE steam_id = %s', id)
        a = cur.fetchone()[0]
    if a is None:
        lol = {'games': []}
        games = steam.users.get_user_recently_played_games(id)['games']
        
        for i in games:
            name = i['name']
            all_time = i['playtime_forever']
            lol['games'].append({"game_name": name, "start minutes": all_time, "now minutes": all_time, "now time": f"{time_year}:{time_month}:{time_week}:{time_day}"})

        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET {day_time} = %s WHERE steam_id = %s', (json.dumps(lol), id))
                CONN.commit()
                

def check_time_for_new_results_steam(day, id, time_year, time_month, time_week, time_day):
    with CONN.cursor() as cur:
        cur.execute(f'SELECT {day} from games_steam_stats WHERE steam_id = %s', id)
        games = json.loads(cur.fetchone()[0])['games']
        time = games[0]['now time']
        t_year, t_month, t_week, t_day = time.split(':')
    if t_month == time_month:
        lol = {'games': []}
        games_now = steam.users.get_user_recently_played_games(id)['games']
        
        for i, j in zip(games_now, games):
            name = i['name']
            all_time = i['playtime_forever']
            start_time = j['start minutes']
            lol['games'].append({"game_name": name, "start minutes": start_time, "now minutes": all_time, "now time": f"{time_year}:{time_month}:{time_week}:{time_day}"})

        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET {day} = %s WHERE steam_id = %s', (json.dumps(lol), id))
                CONN.commit()
    else:
        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET monday_1 = NULL, tuesday_1 = NULL, wednesday_1 = NULL, thursday_1 = NULL, friday_1 = NULL, saturday_1 = NULL, sunday_1 = NULL,\
                                                           monday_2 = NULL, tuesday_2 = NULL, wednesday_2 = NULL, thursday_2 = NULL, friday_2 = NULL, saturday_2 = NULL, sunday_2 = NULL,\
                                                           monday_3 = NULL, tuesday_3 = NULL, wednesday_3 = NULL, thursday_3 = NULL, friday_3 = NULL, saturday_3 = NULL, sunday_3 = NULL,\
                                                           monday_4 = NULL, tuesday_4 = NULL, wednesday_4 = NULL, thursday_4 = NULL, friday_4 = NULL, saturday_4 = NULL, sunday_4 = NULL\
                                                           WHERE steam_id = %s', id)
                CONN.commit()
        

@games_router.post("/games")
def games_stats(model: SteamModel):  
    time_year = datetime.now().year
    time_month = datetime.now().month
    time_week = datetime.now().isocalendar().week
    time_day = datetime.weekday(datetime.now())

    days = [
        ['monday_1', 'tuesday_1', 'wednesday_1', 'thursday_1', 'friday_1', 'saturday_1', 'sunday_1'],
        ['monday_2', 'tuesday_2', 'wednesday_2', 'thursday_2', 'friday_2', 'saturday_2', 'sunday_2'],
        ['monday_3', 'tuesday_3', 'wednesday_3', 'thursday_3', 'friday_3', 'saturday_3', 'sunday_3'],
        ['monday_4', 'tuesday_4', 'wednesday_4', 'thursday_4', 'friday_4', 'saturday_4', 'sunday_4']]
    
    if model.steam_id: 
        check_time_for_null_steam(days[time_week - 1][time_day], model.steam_id, time_year, time_month, time_week, time_day)
        check_time_for_new_results_steam(days[time_week - 1][time_day], model.steam_id, time_year, time_month + 2, time_week, time_day)
        check_time_for_null_steam(days[time_week - 1][time_day], model.steam_id, time_year, time_month, time_week, time_day)
        
        return {'responce': 'time changed'}
    else:
        raise uncregistered_user
