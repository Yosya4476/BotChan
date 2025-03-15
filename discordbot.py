import io
import os
import base64
import json

from modal import Stub, web_endpoint
import modal

stub = Stub("generate_image")


@stub.function(
    image=modal.Image.debian_slim().pip_install("torch", "diffusers[torch]", "transformers", "ftfy", "accelerate"),
    secrets=[modal.Secret.from_name("huggingface-secret")],
    gpu="t4",
)

@web_endpoint()
def run_stable_diffusion(prompt: str, num_images: int):
    import torch
    from torch import autocast
    from diffusers import StableDiffusionPipeline


    # 画像生成AIの設定
    load_dotenv();
    MODEL_ID = os.getenv('MODEL_ID')
    DEVICE = os.getenv('DEVICE')

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        use_auth_token=os.environ["HF_TOKEN"],
    ).to(torch_device=DEVICE, torch_dtype=torch.float16)

    # 生成された画像のBase64データを格納するための辞書
    base64_images_dict = {}

    for i in range(num_images):

      image = pipe(prompt=prompt, width=512, height=512, 
                   num_inference_steps=10, guidance_scale=8).images[0]

    buf = io.BytesIO()

    image.save(buf, format="PNG")


    base64_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    base64_images_dict[f"image{i+1}"] = base64_data

    buf.close()

    # img_bytes = buf.getvalue()

    return json.dumps(base64_images_dict)


import discord
from dotenv import load_dotenv
import traceback
from discord.ext import commands
from os import getenv
from datetime import datetime, timezone
import requests


# Botの設定
intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

# voice_id = 951851320346816653
# text_id = 952068860629090314
text_id = 952047855990882317


# メッセージ受信時に動作する処理 #
@bot.event
async def on_message(message): 
  if message.content == "Ping":
    await message.channel.send("Pong!")
      # embedを設定する
  await bot.process_commands(message)

  
# ボイスチャンネルの入退室時に動作する処理 #
@bot.event
async def on_voice_state_update(member, before, after):
  alert_channel = bot.get_channel(text_id)

  # ボイスチャンネルを入室または退室したかを判定する
  if before.channel is not after.channel:
    
    # ボイスチャンネルに入室したときの処理
    if before.channel is None:
      title = f"{after.channel.name}に入室"
      message = f"{member}がボイスチャンネルに入室したよ！"
      color = 0x7289da
      
    # ボイスチャンネルを退室したときの処理
    elif after.channel is None:
      title = f"{before.channel.name}から退室"
      message = f"{member}がボイスチャンネルを退室したよ！"
      color = 0xffa500

    # embedを設定する
    embed = discord.Embed(title=title,
                          description=message,
                          color=color,
                          timestamp=datetime.now(timezone.utc))
    embed.set_author(name=member.name,
                     icon_url=member.avatar.url)
    # embedを送信する
    await alert_channel.send(embed=embed)
   
  await bot.process_commands(member, before, after)

  
# コマンドを入力したときの処理
@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)


@bot.command()
async def img(
            self,
            ctx,
            prompt: str
    ):
        try:
            response = requests.get(self.endpoint + "generate_image",
                                    params={"prompt": prompt, "num_images": 4})  # 生成枚数は4枚固定
        except requests.RequestException as e:
            self.log_util.log_command_execution(f"Failed to send request: {e}", prompt)
            await ctx.followup.send("リクエストの送信中にエラーが発生しました")
            return

        # 前提として、response.textにはBase64エンコードされた画像データのリストが含まれていると仮定します。
        if response.status_code == 200:
            try:
                # 余分なエスケープシーケンスを解決する
                parsed_str = response.text.encode().decode('unicode_escape')

                # 最初と最後のダブルクォートを削除し、エスケープされたダブルクォートも除去する
                json_str = parsed_str.strip('"').replace('\\"', '"')

                # 文字列をJSONオブジェクトに変換する
                images_dict = json.loads(json_str)

                files = []

                # 辞書の各キー（画像）に対して繰り返し処理
                for key, base64_image in images_dict.items():
                    # Base64文字列をバイナリデータにデコード
                    image_data = base64.b64decode(base64_image)
                    # バイナリデータをファイルライクオブジェクトに変換
                    image_stream = io.BytesIO(image_data)
                    image_stream.seek(0)
                    # discord.Fileオブジェクトを作成し、リストに追加
                    files.append(discord.File(image_stream, filename=f"{key}.png"))

                # メッセージとともに画像を送信（最大10個のファイルを添付可能）
                await ctx.followup.send(f"画像を生成しました！\n"
                                        f"```{prompt}```", files=files)

            except json.JSONDecodeError:
                await ctx.followup.send("エラー: JSONの解析に失敗しました。")
            except Exception as e:
                await ctx.followup.send(f"予期せぬエラーが発生しました: {e}")
        else:
            await ctx.followup.send(
                f"サーバーからのレスポンスが200 OKではありません。ステータスコード: {response.status_code}")

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)



