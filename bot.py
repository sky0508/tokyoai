import os
import ssl
import certifi
from pathlib import Path

# Discord 等のライブラリを読み込む前に証明書の場所を指定
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp

# 環境変数をロード
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# SSL 証明書のパスを `certifi` に統一（macOS/Python 3.13 の検証失敗対策）
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

raw_token = os.getenv("TOKEN", "")
TOKEN = raw_token.strip().strip('"').strip("'")
if TOKEN.startswith("Bot "):
    TOKEN = TOKEN[4:].strip()

# DIFY_API_KEY と DIFY_KEY の両対応
raw_dify = os.getenv("DIFY_API_KEY") or os.getenv("DIFY_KEY") or ""
DIFY_KEY = raw_dify.strip().strip('"').strip("'")
# Dify API ベースURL（未設定ならクラウド）
API_BASE = os.getenv("DIFY_API_BASE", "https://api.dify.ai/v1")

# 必要なIntentsを設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

# ユーザーごとの会話ID管理（メモリ上）
user_conversation_id = {}

@client.command()
async def chat(ctx, *, query: str):
    url = f'{API_BASE}/chat-messages'
    headers = {
        'Authorization': f'Bearer {DIFY_KEY}',
        'Content-Type': 'application/json'
    }
    conversation_id = user_conversation_id.get(str(ctx.author.id), '')
    data = {
        'query': query,
        'response_mode': 'blocking',
        'user': str(ctx.author.id),
        'conversation_id': conversation_id,
        'inputs': {}
    }
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=headers, json=data, timeout=120) as response:
            if response.status == 200:
                json_response = await response.json()
                # 会話IDを保持
                conv_id = json_response.get('conversation_id')
                if conv_id:
                    user_conversation_id[str(ctx.author.id)] = conv_id
                answer = json_response.get('answer', 'No answer provided.')
                await ctx.send(answer)
            else:
                error_message = await response.text()
                await ctx.send(f'APIエラー: {response.status}, メッセージ: {error_message}')

@client.command()
async def reset(ctx):
    """会話履歴（conversation_id）をリセット"""
    user_conversation_id.pop(str(ctx.author.id), None)
    await ctx.send('会話履歴をリセットしました。')

client.run(TOKEN)
