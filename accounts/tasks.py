from integration.unisender import unisender
from marketplace.celery_app import app
from marketplace.errors import SendException


@app.task
def send_simple_code(to: str, data: str, type_message):
    try:
        unisender.send_email(email=to, data=data, type_message=type_message)
    except Exception:
        raise SendException
