from dotenv import load_dotenv
import os
import requests

load_dotenv()

def send_simple_message(subject, message):
        return requests.post(
                os.getenv('MAIL_ENDPOINT'),
                auth=("api", os.getenv('MAIL_API_KEY')),
                data={"from": os.getenv('MAIL_FROM'),
                        "to": os.getenv('MAIL_TO'),
                        "subject": subject,
                        "text": message})
