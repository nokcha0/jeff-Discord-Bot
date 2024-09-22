import discord, random
import asyncio
import aiohttp, io
import wolframalpha
import pytz

import play_lichess
from play_lichess.constants import Variant

from datetime import datetime
from discord import Activity, ActivityType, Status
from discord.ext import tasks
from discord.ext import commands
from googletrans import Translator   # pip install googletrans==3.1.0a0
                                     # USE THE ALPHA VERSION

from alive import alive
from reddit import get_image

from dotenv import load_dotenv       # .env
import os

load_dotenv()

#--------------------------------------VARIABLES------------------------------

TOKEN = os.getenv("DISCORD_TOKEN")

help_command = commands.DefaultHelpCommand(no_category="Here, get some help from jeff")

intents = discord.Intents.all()

client = commands.Bot(command_prefix=['jeff '], case_insensitive=True, intents=intents, help_command=help_command)

wolfram_client = wolframalpha.Client(os.getenv("WOLFRAM_APP_ID"))

montreal_tz = pytz.timezone('America/Montreal')

#---------------------------------INITIALIZE-------------------------------------

@client.event
async def on_ready():
    print('{0.user} is alive'.format(client))
    await client.change_presence(status=Status.idle, activity=Activity(type=ActivityType.watching, name="you"))


#------------------------------COMMANDS----------------------------------

                                                                #Lichess Link
@client.command(brief="Generate Lichess Link", description="""
clock_limit (default) = 600
clock_increment (default) = 3

Variants:
STANDARD (default)
CRAZYHOUSE
CHESS960
KING_OF_THE_HILL
THREE_CHECK
ANTICHESS
ATOMIC
HORDE
RACING_KINGS
                """, aliases=['lichess'])      
async def chess(ctx, clim=600, cinc=3, gametype="STANDARD"):
    
    if gametype.upper() == "STANDARD":
        variant = Variant.STANDARD
    elif gametype.upper() == "CRAZYHOUSE":
        variant = Variant.CRAZYHOUSE
    elif gametype.upper() == "CHESS960":
        variant = Variant.CHESS960
    elif gametype.upper() == "KING_OF_THE_HILL":
        variant = Variant.KING_OF_THE_HILL
    elif gametype.upper() == "THREE_CHECK":
        variant = Variant.THREE_CHECK
    elif gametype.upper() == "ANTICHESS":
        variant = Variant.ANTICHESS
    elif gametype.upper() == "ATOMIC":
        variant = Variant.ATOMIC
    elif gametype.upper() == "HORDE":
        variant = Variant.HORDE
    elif gametype.upper() == "RACING_KINGS":
        variant = Variant.RACING_KINGS
    else:
        variant = Variant.STANDARD  # Default to STANDARD if no match is found

    await ctx.send(f'Selected Variant: {variant}')

    try:
        match = play_lichess.create(
            minutes=clim, 
            increment=cinc, 
            variant=variant
        )
        await ctx.send(f"Chess Game Link: {match.link}")
    except Exception as e:
      await ctx.send(f'Error: {str(e)}')


@client.command(brief="Math Solver.", aliases=['m'])  
async def math(ctx, *, query):
    try:
        res = await wolfram_client.query(query)

        result = None
        for pod in res.pods:
            if pod.primary:
                result = pod.subpods[0].plaintext
                break
        if result:
            embed = discord.Embed(title=f"Query: {query}", color=discord.Color.random())
            embed.add_field(name="Result", value=result, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No results found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

                                                              # Translate
@client.command(brief="Google Translate.", description="""    
    'ch': 'chinese (simplified)',
    'cht': 'chinese (traditional)',
    'en': 'english',
    'fr': 'french',
    'ge': 'german',
    'gr': 'greek',
    'he': 'hebrew',
    'hi': 'hindi',
    'hu': 'hungarian',
    'it': 'italian',
    'ja': 'japanese',
    'ko': 'korean',
    'la': 'latin',
    'pe': 'persian',
    'po': 'polish',
    'pu': 'punjabi',
    'ru': 'russian',
    'sp': 'spanish',
    'tu': 'turkish'""", aliases=['trans', 'tr'])  
async def translate(ctx, lang='en', *, text):
    try:
      translator = Translator()
      
      if lang in ['ch', 'cn', 'chinese']:
        lang = 'zh-cn'
      elif lang in ['cht', 'cnt', 'chineset']:
        lang = 'zh-tw'
      elif lang in ['gr', 'greek']:
        lang = 'el'
      elif lang in ['ge', 'german']:
        lang = 'de'
      elif lang in ['pu', 'punjabi']:
        lang = 'pa'
      elif lang in ['tu', 'turkish']:
        lang = 'tr'
      elif lang in ['pe', 'persian']:
        lang = 'fa'
      elif lang in ['sp', 'spanish']:
        lang = 'es'
      elif lang in ['po', 'polish']:
        lang = 'pl'
      
      translation = translator.translate(text, dest=lang)
      await ctx.send(translation.text)
    except ValueError as e:
      await ctx.send(f'Error: {str(e)}')


@client.command(brief="Status checking", aliases=['stat'])  # Status
async def status(ctx):
    await ctx.send('alive')

@client.command(brief="Images subreddit", aliases=['red'])    # Reddit
async def reddit(ctx):
    image_url, post_title, embed_color = await get_image()
    embed = discord.Embed(title=post_title, color=discord.Color(embed_color))
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)

@client.command(brief="Who just deleted a message?")      # Snipe
async def snipe(ctx):
    global snipe_message_content, snipe_message_author, snipe_message_channel, snipe_message_attachments
    if snipe_message_content is None:
        await ctx.channel.send("There is nothing to snipe")
        return

    embed = discord.Embed(description=snipe_message_content, color=discord.Color.random())
    embed.set_author(name=f"{snipe_message_author.name} sent:")
    embed.set_footer(text=f"#{snipe_message_channel.name} | You cannot escape jeff.")

    if snipe_message_attachments:
        embed.set_image(url=snipe_message_attachments[0])

    await ctx.channel.send(embed=embed)


@client.command(brief="jeff decides for you.")   # Choose
async def choose(ctx, *, options):
    if len(options) < 2:
        await ctx.send("Not enough choices")
    else:
      options_list = options.split(",")
      chosen_option = random.choice(options_list)
      await ctx.send(f"jeff chooses {chosen_option.strip()}")


@client.command(brief="latency")  # Latency
async def latency(ctx):
  latency = client.latency
  await ctx.send(f"Latency: {latency}")


@client.command(brief="Repeating argument x, for y number of times")  # Repeating arg.
async def repeat(ctx, argument: str, times: int):
    for i in range(times):
        await ctx.send(argument)

  
@client.command(brief="Changing the user's server name")  # Change Nick scrapped from channel 971882706331926558
async def change(ctx):
    try:
        channel = client.get_channel(971882706331926558)
        if channel is None:
            await ctx.send("Failed to get the channel.")
            return
        nicknames = []
        async for message in channel.history(limit=None):
            if message.author != client.user:
                nicknames.append(message.content)
        member = ctx.guild.get_member(688182572467093504)
        if member is None:
            await ctx.send("Failed to get the member.")
            return
        current_nickname = member.nick or member.name
        new_nickname = current_nickname
        while new_nickname == current_nickname:
            new_nickname = random.choice(nicknames)
        await member.edit(nick=new_nickname)
        await ctx.send(f'Changed to {new_nickname}.')
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


@client.command(brief="Changing Profile Pic", aliases=['pp'])    #Change Profile Pic
async def profilepic(ctx):
    try:
        url, title, color = await get_image()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Failed to download image from {url}")
                    return
                image_bytes = await resp.read()
        image = io.BytesIO(image_bytes)
        await client.user.edit(avatar=image.getvalue())
        await ctx.send(f"Changed profile picture to [ {title} ] ({url}).")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


# -------------------------------------EVENTS------------------------

snipe_message_content = None
snipe_message_author = None
snipe_message_channel = None
snipe_message_attachments = []

@client.event        # Upon message deletion
async def on_message_delete(message):
    global snipe_message_content, snipe_message_author, snipe_message_channel, snipe_message_attachments
    snipe_message_content = message.content
    snipe_message_author = message.author
    snipe_message_channel = message.channel
    snipe_message_attachments = [attachment.url for attachment in message.attachments if attachment.url.endswith(('jpg', 'jpeg', 'png', 'gif'))]


@client.event        # Upon Member Join
async def on_member_join(member):
    general_channel = client.get_channel(649297818699169805)  
    welcome_message = f"{member.mention} has just joined the server"
    await general_channel.send(welcome_message)

                #VC CHECK
voice_channel_id = 697798692958109746 #Arg
target_channel_id = 712674217480683563 #Announcement
target_role_id = 1106591530296279190 #VCNotif
users_in_channel = set()

@client.event    #VC notify
async def on_voice_state_update(member, before, after):
    voice_channel = client.get_channel(voice_channel_id)
    
    if before.channel != voice_channel and after.channel == voice_channel:
        if len(voice_channel.members) == 1:
            target_channel = client.get_channel(target_channel_id)
            target_role = discord.utils.get(member.guild.roles, id=target_role_id)

            if target_channel is not None and target_role is not None:
                await target_channel.send(f'{target_role.mention} someone just joined vc at {datetime.now(montreal_tz).strftime("%I:%M %p")}')

    if before.channel == voice_channel and after.channel != voice_channel:
          if len(voice_channel.members) == 0:
            target_channel = client.get_channel(target_channel_id)
            if target_channel is not None:
                await target_channel.send(f'Everybody left vc at {datetime.now(montreal_tz).strftime("%I:%M %p")}')

  

alive()
client.run(TOKEN)
