from celery import Celery

from app.adapters.motor_mongodb.gateway import MotorGateway
from app.adapters.polygon_api.gateway import PolygonGateway
from app.main.di import settings, database

celery_app = Celery(
    'app',
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=['app.celery.tasks.stocks_tasks']
)

celery_app.conf.update(
    result_expires=3600,
)

api_gateway = PolygonGateway(settings.POLYGON_BASE_URL)
db = MotorGateway(database=database, session=None)
