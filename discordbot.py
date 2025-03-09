import discord
import traceback
from discord.ext import commands
from os import getenv
from datetime import datetime


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)

# voice_id = 951851320346816653
text_id = 952068860629090314


# メッセージ受信時に動作する処理 #
@bot.event
async def on_message(message):   
  if message.content == 'Ping':
    await message.channel.send('Pong!')
  await bot.process_commands(message)

  
# ボイスチャンネルの入退室時に動作する処理 #
@bot.event
async def on_voice_state_update(member, before, after): 
    if (before.channel != after.channel):
        now = datetime.utcnow()
        alert_channel = bot.get_channel(952068860629090314)
        if before.channel is None: 
            msg = f'{now:%m/%d-%H:%M} に {member.name} が {after.channel.name} に参加しました。'
            await alert_channel.send(msg)
        elif after.channel is None: 
            msg = f'{now:%m/%d-%H:%M} に {member.name} が {before.channel.name} から退出しました。'
            await alert_channel.send(msg)
    await bot.process_commands(member, before, after)

  
# コマンドを入力したときの処理
@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)

