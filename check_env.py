from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).resolve().parent / ".env"
loaded = load_dotenv(dotenv_path=env_path)

token = os.getenv("TOKEN")
dify_api_key = os.getenv("DIFY_API_KEY")
dify_key_alt = os.getenv("DIFY_KEY")

print("dotenv loaded:", loaded, f"({env_path})")
print("TOKEN:", bool(token))
print("DIFY_API_KEY:", bool(dify_api_key))
print("DIFY_KEY:", bool(dify_key_alt))
print("Effective DIFY key present:", bool(dify_api_key or dify_key_alt))
