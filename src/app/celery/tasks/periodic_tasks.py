from celery.schedules import crontab

from app.celery import celery_app
from app.celery.tasks.stocks_tasks import parse_stock_data_task


def get_periodic_tasks():  # TODO: getting from DB or config_file
    return [
        {
            "task_name": "parse_stock_data",
            "crontab": {"minute": "6", "hour": "*", "day_of_week": "*", "day_of_month": "*", "month_of_year": "*"},
        },
    ]


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    periodic_tasks = get_periodic_tasks()

    for task in periodic_tasks:
        crondict = task.get("crontab")
        celery_app.add_periodic_task(
            crontab(
                minute=crondict["minute"],
                hour=crondict["hour"],
                day_of_week=crondict["day_of_week"],
                day_of_month=crondict["day_of_month"],
                month_of_year=crondict["month_of_year"],
            ),
            parse_stock_data_task.s(task["task_name"]),
            name=task["task_name"],
        )
