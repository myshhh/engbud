from fastapi import FastAPI
import uvicorn
from autorization_routher import users_router


app = FastAPI()
app.include_router(users_router)


if __name__ == '__main__':
    uvicorn.run(app, host='5.228.37.238')