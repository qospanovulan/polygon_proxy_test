from fastapi import FastAPI

from .di import init_dependencies, database, mongo_client, init_db
from .routers import init_routers

app = FastAPI()

def create_app() -> FastAPI:
    init_routers(app)
    init_dependencies(app, database=database, mongo_client=mongo_client)

    return app

@app.on_event("startup")
async def on_startup():
    await init_db(database)