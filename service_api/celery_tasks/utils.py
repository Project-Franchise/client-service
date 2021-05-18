"""
Celery config module
"""
from celery import Celery
from celery.schedules import crontab

from ..constants import CRONTAB_FILLING_DB_WITH_REALTIES_SCHEDULE


def setup_periodic_tasks(sender, **kwargs):
    """
    Setup periodic task for filling DB with Realties.
    Should be used in  `on_after_configure.connect`
    """
    from .tasks import fill_db_with_realties, update_realties
    sender.add_periodic_task(
        crontab(**CRONTAB_FILLING_DB_WITH_REALTIES_SCHEDULE), fill_db_with_realties.s(), name="db-filling"
    )
    sender.add_periodic_task(
        crontab(**CRONTAB_FILLING_DB_WITH_REALTIES_SCHEDULE), update_realties.s(), name="update-all-records"
    )


def make_celery(flask_app):
    """
    Initialize and configure celery app.
    :param flask_app: instance of flask app
    :returns: celery app instance
    """
    broker_url, backend_url = flask_app.config.get("CELERY_BROKER_URL"), flask_app.config.get("CELERY_BACKEND_URL")

    celery_app = Celery("service_api",
                        backend=backend_url or "redis://127.0.0.1:6379/0",
                        broker=broker_url or "redis://127.0.0.1:6379/0")
    celery_app.conf.update(flask_app.config)
    # celery_app.control.purge()

    celery_app.autodiscover_tasks(["service_api"])
    celery_app.on_after_configure.connect(setup_periodic_tasks)

    return celery_app
