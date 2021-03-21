#!/usr/bin/python -u
import os, time, random, datetime, json, asyncio, pickle, requests, discord
from discord.ext import commands

stars = None
locations = {
    0: 'Asgarnia',
    1: 'Karamja/Crandor',
    2: 'Feldip Hills/Isle of Souls',
    3: 'Fossil Island/Mos Le\'Harmless',
    4: 'Fremennik Lands/Lunar Isle',
    5: 'Great Kourend',
    6: 'Kandarin',
    7: 'Kebos Lowlands',
    8: 'Kharidian Desert',
    9: 'Misthalin',
    10: 'Morytania',
    11: 'Piscatoris/Gnome Stronghold',
    12: 'Tirannwn',
    13: 'Wilderness'
}
owner = 119094696487288833
intents = discord.Intents.none()
intents.guilds = True; intents.guild_messages = True
bot = commands.Bot(command_prefix='.', owner_id=owner, intents=intents)

def load(file):
    with open(file, 'rb') as fp:
        data = pickle.load(fp)
        fp.close()
        return data
def save(file, data):
    with open(file, 'wb') as fp:
        pickle.dump(data, fp)
def setup_files(*files):
    for file in files:
        if not os.path.isfile(file):
            if os.path.exists(file): raise Exception('Require file exists as dir')
            f = open(file, 'x')
setup_files('token', 'data')
with open('token', 'r+') as fp:
    if not fp.read():
        token = input('Token: ')
        fp.write(token)
    else:
        fp.seek(0); token = fp.read()
        print('Using existing token')

@bot.event
async def on_ready():
    print(f"I am running on {bot.user.name} with the ID {bot.user.id}")
    await get_stars()
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="stars."))

async def get_stars():
    global stars
    while True:
        print('Stars updated')
        r = requests.get('https://sek.ai/stars/get.php')
        stars = r.json()
        await asyncio.sleep(10)

@bot.command()
async def next(rx):
    i = 0
    while True:
        if stars[i]['minTime'] < int(time.time()):
            i += 1; continue
        break
    next_time = str(datetime.timedelta(seconds=stars[i]['minTime'] - int(time.time()))) + ' ~ ' + str(datetime.timedelta(seconds=stars[i]['maxTime'] - int(time.time())))
    embed=discord.Embed(title='The next star to land is...', color=0x6a001a);
    embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/7/7c/Infernal_pickaxe.png')
    embed.add_field(name='World', value=f"{stars[i]['world']}", inline=True)
    embed.add_field(name='Location', value=f"{locations[stars[i]['location']]}", inline=True)
    embed.add_field(name='ETA', value=f"{next_time}", inline=False)
    await rx.send(embed=embed)

@bot.command()
async def nextwildy(rx):
    i = 0
    while True:
        if stars[i]['minTime'] < int(time.time()):
            i += 1; continue
        if stars[i]['location'] != 13:
            i += 1; continue
        break
    next_time = str(datetime.timedelta(seconds=stars[i]['minTime'] - int(time.time()))) + ' ~ ' + str(datetime.timedelta(seconds=stars[i]['maxTime'] - int(time.time())))
    embed=discord.Embed(title='The next wildy star to land is...', color=0x6a001a);
    embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/a/a1/Skull_(status)_icon.png')
    embed.add_field(name='World', value=f"{stars[i]['world']}", inline=True)
    embed.add_field(name='ETA', value=f"{next_time}", inline=False)
    await rx.send(embed=embed)

bot.run(token)
