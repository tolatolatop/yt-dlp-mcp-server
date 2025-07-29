import os
from dotenv import load_dotenv

load_dotenv('.env.test')

USER_PROXY_URL = os.getenv("USER_PROXY_URL")
