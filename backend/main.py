from fastapi import FastAPI
import uvicorn
from autorization_routher import users_router
from games_stats import games_router
from connection_launchers import connection_laucnhers
from games_stats_request import games_request_router

app = FastAPI()
app.include_router(users_router)
app.include_router(games_router)
app.include_router(connection_laucnhers)
app.include_router(games_request_router)

if __name__ == '__main__':
    uvicorn.run(app, host='37.204.200.243')
    
