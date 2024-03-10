import random
import string

from marketplace import settings


def generate_code():
    return "".join(random.choice(string.digits) for _ in settings.SMS_CODE_LENGTH)
