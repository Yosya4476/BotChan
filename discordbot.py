import discord
import traceback
from discord.ext import commands
from os import getenv
from datetime import datetime


intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

# voice_id = 951851320346816653
# text_id = 952068860629090314
text_id = 952047855990882317


# メッセージ受信時に動作する処理 #
@bot.event
async def on_message(message): 
  # embedを設定する
  embed = discord.Embed(title="title",
                          description=message,
                          color=0x112233,
                          timestamp=datetime.now(datetime.timezone.utc))
  embed.set_author(name="Yatta",
                     icon_url="Clear")
    # embedを送信する
  await message.channel.send(embed=embed)
  await bot.process_commands(message)

  
# ボイスチャンネルの入退室時に動作する処理 #
@bot.event
async def on_voice_state_update(member, before, after):
  alert_channel = bot.get_channel(text_id)

  # ボイスチャンネルを入室または退室したかを判定する
  if before.channel is not after.channel:
    
    # ボイスチャンネルに入室したときの処理
    if before.channel is None:
      await alert_channel.send(f"#{after} ですわよ")
      title = f"#{after.channel.name} に入室"
      message = "ボイスチャンネルに入室したよ！"
      color = 0x7289da
      
    # ボイスチャンネルを退室したときの処理
    elif after.channel is None:
      await alert_channel.send(f"#{after} ですわよ")
      title = f"#{before.channel.name} を退室"
      message = "ボイスチャンネルを退室したよ！"
      color = 0xffa500

    # embedを設定する
    embed = discord.Embed(title=title,
                          description=message,
                          color=color,
                          timestamp=datetime.now(datetime.timezone.utc))
    embed.set_author(name=member.name,
                     icon_url=member.avatar_url)
    # embedを送信する
    await alert_channel.send(embed=embed)
   
  await bot.process_commands(member, before, after)

  
# コマンドを入力したときの処理
@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)

