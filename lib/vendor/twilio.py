import os
from dotenv import load_dotenv
from twilio.rest import Client
from aiolimiter import AsyncLimiter

# Load .env file
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

admin_phone = os.getenv("ADMIN_PHONE")
from_whatsapp_number = f"whatsapp:{os.getenv("TWILIO_WHATSAPP_NUMBER")}"
to_whatsapp_number = f"whatsapp:{admin_phone}"

async def send_whatsapp(msg):
    # Twilio rate limit
    rate_limiter = AsyncLimiter(max_rate=1, time_period=1)  # 1 request per second

    await rate_limiter.acquire()
    client.messages.create(
        body=msg,
        from_=from_whatsapp_number,
        to=to_whatsapp_number,
    )

async def send_sms(msg):
    twilio = os.getenv("TWILIO_VIRTUAL_PHONE")
    client.messages.create(
        from_=twilio,
        to=admin_phone,
        body=msg,
    )
