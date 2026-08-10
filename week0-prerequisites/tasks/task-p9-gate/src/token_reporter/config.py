from os import getenv

from dotenv import load_dotenv

load_dotenv()

APP_NAME = getenv("APP_NAME")
TOKEN_PRICE = getenv("TOKEN_PRICE")