import os
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings:
    POLYGON_BASE_URL: str = os.environ.get("POLYGON_BASE_URL")
    POLYGON_API_KEY: str = os.environ.get("POLYGON_API_KEY")

    DATABASE_URI: str = os.environ.get("DATABASE_URI")
    DATABASE_NAME: str = os.environ.get("DATABASE_NAME")
    TTL_EXPIRES: int = os.environ.get("TTL_EXPIRES", 45 * 24 * 60 * 60)  # 45 in seconds

    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND")

    CELERY_BEAT_SCHEDULE = {
        'parse-stock-data-every-hour': {
            'task': 'app.celery.stocks_tasks.parse_stock_data',
            'schedule': crontab(minute="0", hour='*'),
        },
    }


