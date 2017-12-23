from __future__ import unicode_literals

from harper.settings import secrets
from twilio.rest import Client
import os, json, logging

NOT_CONFIGURED_MESSAGE = """
    Cannot initialize Twilio messaging platform. Required variables TWILIO_ACCOUNT_SID, or TWILIO_AUTH_TOKEN or TWILIO_NUMBER are missing
    """

logger = logging.getLogger(__name__)
def load_contacts():
    return secrets.CONTACT_LIST

def load_twilio_config():
    twilio_account_sid = secrets.TWILIO_CONFIG["ACCOUNT_SID"]
    twilio_auth_token = secrets.TWILIO_CONFIG["AUTH_TOKEN"]
    twilio_phone_number = secrets.TWILIO_CONFIG["PHONE_NUMBER"]

    if not all ([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        logger.error(NOT_CONFIGURED_MESSAGE)
        raise NameError(NOT_CONFIGURED_MESSAGE)

    return (twilio_phone_number, twilio_account_sid, twilio_auth_token)


class MessageClient(object):
    def __init__(self):
        (twilio_phone_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()

        self.twilio_phone_number = twilio_phone_number
        self.twilio_client = Client(twilio_account_sid, twilio_auth_token)

    def send_message(self, body, to):
        self.twilio_client.messages.create(
            body=body,
            to=to,
            from_=self.twilio_phone_number,
        )


def broadcast_message(message):
    contacts = load_contacts()
    client = MessageClient()

    for contact in contacts:
        client.send_message(message, contact["phone_number"])

    return None
