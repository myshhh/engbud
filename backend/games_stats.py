from steam_web_api import Steam

import pymysql as pymy
from classes import LaunchersModel
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

def check_time_for_null_day_steam(day, id, time_year, time_month, time_week, time_day):
    with CONN.cursor() as cur:
        cur.execute(f'SELECT {day} from games_steam_stats WHERE steam_id = %s', id)
        a = cur.fetchone()[0]
    if a is None:
        lol = {'games': []}
        games = steam.users.get_user_recently_played_games(id)['games']
        
        for i in games:
            name = i['name']
            all_time = i['playtime_forever']
            lol['games'].append({"game_name": name, "start minutes": all_time, "now minutes": all_time, "now time": f"{time_year}:{time_month}:{time_week}:{time_day}"})

        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET {day} = %s WHERE steam_id = %s', (json.dumps(lol), id))
                CONN.commit()


def check_time_for_null_week_steam(week, id, time_year, time_month, time_week, time_day):
    with CONN.cursor() as cur:
        cur.execute(f'SELECT {week} from games_steam_stats WHERE steam_id = %s', id)
        a = cur.fetchone()[0]
    if a is None:
        lol = {'games': []}
        games = steam.users.get_user_recently_played_games(id)['games']
        
        for i in games:
            name = i['name']
            all_time = i['playtime_forever']
            lol['games'].append({"game_name": name, "start minutes": all_time, "now minutes": all_time, "now time": f"{time_year}:{time_month}:{time_week}:{time_day}"})

        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET {week} = %s WHERE steam_id = %s', (json.dumps(lol), id))
                CONN.commit()
                

def check_time_for_new_results_day_steam(day, id, time_year, time_month, time_week, time_day):
    with CONN.cursor() as cur:
        cur.execute(f'SELECT {day} from games_steam_stats WHERE steam_id = %s', id)
        games = json.loads(cur.fetchone()[0])['games']
        time = games[0]['now time']
    if time == f"{time_year}:{time_month}:{time_week}:{time_day}":
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
                cur.execute(f'UPDATE games_steam_stats SET monday = NULL, tuesday = NULL, wednesday = NULL, thursday = NULL, friday = NULL, saturday = NULL, sunday = NULL WHERE steam_id = %s', id)
                CONN.commit()


def check_time_for_new_results_week_steam(week, id, time_year, time_month, time_week, time_day):
    with CONN.cursor() as cur:
        cur.execute(f'SELECT {week} from games_steam_stats WHERE steam_id = %s', id)
        games = json.loads(cur.fetchone()[0])['games']
        time = games[0]['now time']
        y, m, w, d = time.split(':')
    if f'{y}:{m}:{w}' == f"{time_year}:{time_month}:{time_week}":
        lol = {'games': []}
        games_now = steam.users.get_user_recently_played_games(id)['games']
        
        for i, j in zip(games_now, games):
            name = i['name']
            all_time = i['playtime_forever']
            start_time = j['start minutes']
            lol['games'].append({"game_name": name, "start minutes": start_time, "now minutes": all_time, "now time": f"{time_year}:{time_month}:{time_week}:{time_day}"})

        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET {week} = %s WHERE steam_id = %s', (json.dumps(lol), id))
                CONN.commit()
    else:
        with CONN.cursor() as cur:
                cur.execute(f'UPDATE games_steam_stats SET monday = NULL, tuesday = NULL, wednesday = NULL,\
                                                           thursday = NULL, friday = NULL, saturday = NULL,\
                                                           sunday = NULL, fweek = NULL, sweek = NULL,\
                                                           tweek = NULL, foweek = NULL WHERE steam_id = %s', id)
                CONN.commit()
        

@games_router.post("/games")
def games_stats(model: LaunchersModel):  
    time_year = datetime.now().year
    time_month = datetime.now().month
    time_week = datetime.now().isocalendar().week
    time_day = datetime.weekday(datetime.now()) + 1
    days = {1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday', 7: 'sunday'}
    weeks = {1: 'fweek', 2: 'sweek', 3: 'tweek', 4: 'foweek'}
    
    if any([model.steam_id, model.epicgames_id]): 
        if model.steam_id is not None:
            check_time_for_null_day_steam(days[time_day], model.steam_id, time_year, time_month, time_week, time_day)
            check_time_for_null_week_steam(weeks[time_week], model.steam_id, time_year, time_month, time_week, time_day)
            check_time_for_new_results_day_steam(days[time_day], model.steam_id, time_year, time_month, time_week, time_day)
            check_time_for_new_results_week_steam(weeks[time_week], model.steam_id, time_year, time_month, time_week, time_day)
            check_time_for_null_day_steam(days[time_day], model.steam_id, time_year, time_month, time_week, time_day)
            check_time_for_null_week_steam(weeks[time_week], model.steam_id, time_year, time_month, time_week, time_day)
        
        return {'responce': 'time changed'}
    else:
        raise uncregistered_user
