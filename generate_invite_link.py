import os
from dotenv import load_dotenv
import base64

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Extract Application ID from the token
app_id = base64.b64decode(BOT_TOKEN.split('.')[0] + '==').decode('utf-8')

permissions = 380104722496

# Generate invite URL
invite_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={permissions}&scope=bot"

print(invite_url)
