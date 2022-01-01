#!/usr/bin/python -u
import os, time, bisect, datetime, json, asyncio, requests, discord
from discord.ext import commands

stars = None
last_message = {}
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
worlds = {
    324: 'PVP',
    325: 'PVP',
    337: 'PVP',
    349: 'TL2000',
    353: 'TL1250',
    361: 'TL2000',
    363: 'TL2200',
    364: 'TL1250',
    365: 'HR',
    366: 'TL1500',
    373: 'TL1750',
    391: 'TL1750',
    392: 'PVP',
    396: 'TL2000',
    415: 'TL2200',
    416: 'TL1500',
    420: 'TL1500',
    428: 'TL2000',
    429: 'TL1250',
    447: 'TL1250',
    448: 'TL1500',
    449: 'TL1750',
    450: 'TL2200',
    467: 'TL1750',
    526: 'TL2200',
    527: 'TL2000',
    528: 'TL1500',
    529: 'TL1250',
    533: 'HR'
}
group_name = {
    1: 'Group 1 (302-334)',
    2: 'Group 2 (336-370)',
    3: 'Group 3 (373-450)',
    4: 'Group 4 (463-496)',
    5: 'Group 5 (505-535)'
}
owner = 119094696487288833
intents = discord.Intents.none()
intents.guild_messages = True
bot = commands.Bot(command_prefix='.', owner_id=owner, intents=intents)

def setup_files(*files):
    for file in files:
        if not os.path.isfile(file):
            if os.path.exists(file): raise Exception('Require file exists as dir')
            f = open(file, 'x')
setup_files('.token')
with open('.token', 'r+') as fp:
    if not fp.read():
        token = input('Token: ')
        fp.write(token)
    else:
        fp.seek(0); token = fp.read()
        print('Using existing token')

def get_world(world):
    if world in worlds: world = f'{world} ({worlds[world]})'
    return str(world)

@bot.command()
async def scout(rx):
    groups = [[] for _ in range(5)]
    sorting = [336, 373, 463, 505, 600]
    all = 'All scouted!'
    for star in sorted(stars, key=lambda k: k['world']):
        if star['maxTime'] < int(time.time()):
            world = star['world']
            index = bisect.bisect(sorting, world)
            groups[index].append(world)
    embed=discord.Embed(title='List of unscouted worlds', color=0x6a001a);
    embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/5/5d/Mahogany_telescope_icon.png')
    i = 0
    for group in groups:
        i += 1
        embed.add_field(name=group_name[i], value=f"{', '.join(get_world(w) for w in group) if group else all}", inline=True)
    await rx.send(embed=embed)

@bot.command()
async def next(rx, limit=1):
    if limit > 3: limit = 3
    global last_message
    await rx.message.delete()
    if rx.guild.id in last_message:
        try: await last_message[rx.guild.id].delete()
        except discord.errors.NotFound: pass
    next_stars = []
    for star in stars:
        if star['minTime'] < int(time.time()): continue
        next_stars.append(star)
        if len(next_stars) == limit: break
    if len(next_stars) > 1:
        embed=discord.Embed(title=f'The next {len(next_stars)} stars to land are...', color=0x6a001a);
        for star in next_stars:
            star_time = str(datetime.timedelta(seconds=star['minTime'] - int(time.time()))) + ' ~ ' + str(datetime.timedelta(seconds=star['maxTime'] - int(time.time())))
            world = get_world(star['world'])
            embed.add_field(name=f"W{world} - {locations[star['location']]}", value=star_time, inline=True)
    else:
        next_time = str(datetime.timedelta(seconds=next_stars[0]['minTime'] - int(time.time()))) + ' ~ ' + str(datetime.timedelta(seconds=next_stars[0]['maxTime'] - int(time.time())))
        embed=discord.Embed(title='The next star to land is...', color=0x6a001a);
        world = get_world(next_stars[0]['world'])
        embed.add_field(name='World', value=world, inline=True)
        embed.add_field(name='Location', value=locations[next_stars[0]['location']], inline=True)
        embed.add_field(name='ETA', value=next_time, inline=False)
    embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/7/7c/Infernal_pickaxe.png')
    last_message[rx.guild.id] = await rx.send(embed=embed)

@bot.command()
async def nextwildy(rx, limit=1):
    if limit > 18: limit = 18
    next_stars = []
    for star in stars:
        if star['minTime'] < int(time.time()): continue
        if star['location'] != 13: continue
        next_stars.append(star)
        if len(next_stars) == limit: break
    if len(next_stars) > 1:
        embed=discord.Embed(title=f'The next {len(next_stars)} wildy stars to land are...', color=0x6a001a);
        for star in next_stars:
            star_time = str(datetime.timedelta(seconds=star['minTime'] - int(time.time()))) + ' ~ ' + str(datetime.timedelta(seconds=star['maxTime'] - int(time.time())))
            world = get_world(star['world'])
            embed.add_field(name=f'W{world}', value=star_time, inline=True)
    else:
        next_time = str(datetime.timedelta(seconds=next_stars[0]['minTime'] - int(time.time()))) + ' ~ ' + str(datetime.timedelta(seconds=next_stars[0]['maxTime'] - int(time.time())))
        embed=discord.Embed(title='The next wildy star to land is...', color=0x6a001a);
        world = get_world(next_stars[0]['world'])
        embed.add_field(name='World', value=world, inline=True)
        embed.add_field(name='ETA', value=next_time, inline=False)
    embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/a/a1/Skull_(status)_icon.png')
    await rx.send(embed=embed)

async def get_stars():
    global stars
    while True:
        r = requests.get('https://sek.ai/stars/get.php?p=all')
        try:
            stars = r.json()
        except json.decoder.JSONDecodeError:
            stars = []
        await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f'Logged into {bot.user.name}#{bot.user.discriminator} ({bot.user.id})')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='stars.'))
    await get_stars()

bot.run(token)
