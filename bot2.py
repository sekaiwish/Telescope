#!/usr/bin/python -u
import os, time, json, asyncio, requests, discord
from discord.ext import commands

owner = 119094696487288833
intents = discord.Intents.none()
intents.guild_messages = True
bot = commands.Bot(command_prefix='.', owner_id=owner, intents=intents)

last_timestamp = 0

def setup_files(*files):
    for file in files:
        if not os.path.isfile(file):
            if os.path.exists(file): raise Exception('Require file exists as dir')
            f = open(file, 'x')
setup_files('.token', '.webhook')
with open('.token', 'r+') as fp:
    if not fp.read():
        token = input('Token: ')
        fp.write(token)
    else:
        fp.seek(0); token = fp.read()
        print('Using existing token')
with open('.webhook', 'r+') as fp:
    if not fp.read():
        webhook = input('Webhook URL: ')
        fp.write(webhook)
    else:
        fp.seek(0); webhook = fp.read()
        print('Using existing webhook')

async def get_stars():
    global last_timestamp
    while True:
        r = requests.get('http://127.0.0.1:8000/messages')
        try:
            stars = r.json()
        except json.decoder.JSONDecodeError:
            stars = []
        temp_timestamp = 0
        for star in stars:
            new_timestamp = int(star['timestamp'])
            if new_timestamp > last_timestamp:
                world = star['world']
                tier = star['tier']
                location = star['location']
                data = {'content': f'`w{world}` `t{tier}` `{location}`', 'username': star['sender']}
                requests.post(webhook, json=data)
                if new_timestamp > temp_timestamp: temp_timestamp = new_timestamp
        if temp_timestamp > last_timestamp: last_timestamp = temp_timestamp
        await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f'Logged into {bot.user.name}#{bot.user.discriminator} ({bot.user.id})')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='stars.'))
    await get_stars()

bot.run(token)
