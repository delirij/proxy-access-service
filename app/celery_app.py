from celery import Celery

from app.config import settings

# Инициализация Celery
app = Celery("proxi_updater", broker=settings.CELERY_BROKER_URL)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True
)

# Автозагрузка задач
app.autodiscover_tasks(["app.tasks"])