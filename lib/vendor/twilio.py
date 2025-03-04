import os
from dotenv import load_dotenv
from twilio.rest import Client
from aiolimiter import AsyncLimiter

# Load .env file
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

from_whatsapp_number = f"whatsapp:{os.getenv("WHATSAPP_FROM_NUMBER")}"
to_whatsapp_number = f"whatsapp:{os.getenv("WHATSAPP_TO_NUMBER")}"

async def send_whatsapp(msg):
    # Twilio rate limit
    rate_limiter = AsyncLimiter(max_rate=1, time_period=1)  # 1 request per second

    await rate_limiter.acquire()
    message = client.messages.create(
        body=msg,
        from_=from_whatsapp_number,
        to=to_whatsapp_number,
    )

    print(message.sid)


def send_sms(msg):
    message = client.messages.create(
        from_=from_whatsapp_number,
        to=[to_whatsapp_number ],
        body=msg,
    )

    print(message.sid)
