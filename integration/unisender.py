import requests
from django.template.loader import get_template

from marketplace import settings
from marketplace.choices import TypeEmailMessage


class Unisender:
    def __init__(self):
        self.recovery_url = (
            settings.SCHEMA + settings.HOST + settings.EMAIL_RECOVERY_PAGE
        )
        self.api_key = settings.UNISENDER_TOKEN
        self.url = settings.UNISENDER_URL
        self.sender_name = settings.SENDER_NAME
        self.sender_email = settings.SENDER_EMAIL

    @classmethod
    def render_template(cls, template_name, context) -> str:
        template = get_template(f"integration/{template_name}")
        return template.render(context)

    def send_email(self, email, data, type_message=TypeEmailMessage.SUBMITTING_CODE):
        if type_message == TypeEmailMessage.SUBMITTING_CODE:
            body = self.render_template(
                template_name="basic_template.html",
                context={"type": "Hello", "data": data},
            )
            subject = "Confirmation Email"
        else:
            body = self.render_template(
                template_name="basic_recovery_template.html",
                context={"type": "Recover", "data": f"{self.recovery_url}{data}"},
            )
            subject = "Change Password"
        params = {
            "format": "json",
            "api_key": self.api_key,
            "email": email,
            "sender_name": self.sender_name,
            "sender_email": self.sender_email,
            "subject": subject,
            "body": body,
            "list_id": "1",
        }
        response = requests.get(self.url, params=params)
        response.raise_for_status()
        json_response = response.json()
        if "error" in json_response:
            raise Exception(json_response["error"])
        return response.json()


unisender = Unisender()
