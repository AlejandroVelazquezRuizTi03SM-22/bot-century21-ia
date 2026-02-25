import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"❌ Falta variable de entorno: {name}")
    return value

SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_KEY = get_env("SUPABASE_KEY")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

TWILIO_ACCOUNT_SID = get_env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_env("TWILIO_AUTH_TOKEN")