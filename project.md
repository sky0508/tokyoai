import os                                               # OS機能へのアクセスを提供するモジュールをインポート
import discord                                          # discord APIを利用するためのモジュールをインポート
from discord.ext import commands                        # discordのコマンド拡張機能をインポート
from dotenv import load_dotenv                          # .envファイルから環境変数をロードするためのモジュールをインポート
import aiohttp                                          # 非同期HTTPリクエストを行うためのモジュール

# 環境変数をロード
load_dotenv()                                           # .envファイルから環境変数をロード
# botのアクセストークン
TOKEN = os.getenv("TOKEN")                              # Discord botのトークンを環境変数から取得
DIFY_KEY = os.getenv("DIFY_API_KEY")                    # DIFY APIのキーを環境変数から取得

# 必要なIntentsを設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)  # コマンドプレフィックスを'!'に設定したBotクライアントを作成

@client.command()                                       # コマンドデコレータを使用してchat関数をコマンドとして登録
async def chat(ctx, *, query: str):                     # chatコマンドの非同期関数定義
    url = 'http://localhost/v1/chat-messages'           # APIのURLを設定
    headers = {                                         # HTTPリクエストヘッダを設定
        'Authorization': f'Bearer {DIFY_KEY}',          # 認証用のBearerトークンを設定
        'Content-Type': 'application/json'              # コンテンツタイプをJSONに設定
    }
    data = {                                            # POSTリクエストのボディデータを設定
        'query': query,                                 # ユーザーからのクエリ
        'response_mode': 'blocking',                    # レスポンスモードをblockingに設定
        'user': 'user_identifier',                      # ユーザー識別子
        'conversation_id': '',                          # 会話ID（空の場合は設定なし）
        'inputs': {}                                    # APIが要求する追加のパラメータ
    }
    
    async with aiohttp.ClientSession() as session:      # 非同期HTTPセッションを開始
        async with session.post(url, headers=headers, json=data) as response:  # POSTリクエストを非同期で送信
            if response.status == 200:                  # HTTPステータスコードが200の場合
                json_response = await response.json()   # レスポンスのJSONを非同期で読み込み
                answer = json_response.get('answer', 'No answer provided.')  # JSONからanswerを取得、なければデフォルトメッセージ
                await ctx.send(answer)                  # Discordチャンネルに回答を送信
            else:                                       # HTTPステータスコードが200以外の場合
                error_message = await response.text()  # エラーメッセージの内容を取得
                await ctx.send(f'APIエラー: {response.status}, メッセージ: {error_message}')  # エラーメッセージを送信

client.run(TOKEN)                                       # Discordクライアントを実行

