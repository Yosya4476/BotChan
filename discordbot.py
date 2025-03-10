import discord
from dotenv import load_dotenv
import os
import traceback
from discord.ext import commands
from os import getenv
from datetime import datetime, timezone
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

# 画像生成AIの設定
load_dotenv();
MODEL_ID = os.getenv('MODEL_ID')
DEVICE = os.getenv('DEVICE')
HUGGINGFACE_TOKEN = os.getenv('HAGGINGFACE_TOKEN')

pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, revision="fp16", torch_dtype=torch.float16, use_auth_token=HUGGINGFACE_TOKEN)
pipe.to(DEVICE)

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

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)

@bot.command()
async def img(ctx, *args):
  alert_channel = bot.get_channel(text_id)

  prompt = ' '.join(args)
  with autocast(DEVICE):
    # 画像を生成する
    image = pipe(prompt, guidance_scale=7.5)["images"][0]
    image.save("output.png")

  with open('output.png', 'rb') as f:
    picture = discord.File(f)
    await alert_channel.send(file=picture)


