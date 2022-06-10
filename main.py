from fastapi import FastAPI

from routes.authroutes import auth_router
from routes.frames import frames_router

app = FastAPI()
app.include_router(frames_router)
app.include_router(auth_router)
