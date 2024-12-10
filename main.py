# Import Libraries
import os,  pathlib, discord, asyncio, sqlite3, datetime
from discord.ext import commands
from dotenv import load_dotenv # python-dotenv package
from database import DataBase
from globalFunctions import *

# Loading Environment Variables
path = str(pathlib.Path(__file__).parent.resolve())
os.chdir(path)
load_dotenv()

# Discord Initialization
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_GUILD'))
intents = discord.Intents.all()
intents.members = True
description = '''Discord bot'''
bot = commands.Bot(command_prefix=["/","!"], intents=intents, description=description, auto_register=False)
guild = bot.get_guild(GUILD)
onlineMemberIDs = []

# Settings
db = DataBase()

startingCurrency = 1000

@bot.event
async def on_ready():
    await db.setup(bot, GUILD, startingCurrency)
    
    # Sync Commands
    syncedCommands = await bot.tree.sync(guild=None)
    #print(syncedCommands)

    print("Bot is ready")


@bot.event
async def on_message(message):
    print("Message Received")

@bot.listen()
async def on_interaction(interaction):
    print("Interaction Received")

@bot.listen()
async def on_command(ctx):
    print("Command Received from: " + str(ctx.author.id))
    print(messagingUsers)

@bot.listen()
async def on_command_completion(ctx):
    print("Command Finished from: " + str(ctx.author.id))
    messagingUsers.remove(ctx.author.id)
    print(messagingUsers)

async def load():
    for filename in os.listdir('./cogs'):
        if (filename.endswith('.py') and filename != "__init__.py" and filename != "exampleCog.py"):
            print(filename)
            await bot.load_extension(f'cogs.{filename[:-3]}')
    print("Load Done")


# Allowance Functions
allowanceInterval = 60 # seconds per allowance deposit
allowanceAmount = 10 # 10 / min
rentInterval = 60 # seconds per rent charge

def getModulusTime(modulus : int):
    modulusTime = datetime.datetime.now()
    modulusTime -= datetime.timedelta(minutes=modulusTime.minute % modulus, seconds=modulusTime.second, microseconds=modulusTime.microsecond)
    return modulusTime

async def allowance():
    global allowanceTime
    try:
        deltaTime = datetime.datetime.now() - allowanceTime
    except NameError:
        allowanceTime = getModulusTime(allowanceInterval/60)
        deltaTime = datetime.timedelta(seconds=0)
    
    if (deltaTime.total_seconds() > allowanceInterval):
        allowanceTime = getModulusTime(allowanceInterval/60)

        guild = bot.get_guild(GUILD)
        for channel in guild.voice_channels:
            for member in channel.members:
                if (member.id != bot.user.id):
                    await db.changeValue(member.id, allowanceAmount, "balance")


async def loop(seconds : int):
    while True:
        await asyncio.sleep(seconds)
        await allowance()
        #await rent()
        #print("Looping")

async def main():
    await load()
    await bot.start(TOKEN)

if __name__ == "__main__":
    # Start Asyncrounous Loop for realtime updates
    a = asyncio.get_event_loop()
    a.create_task(main())
    a.create_task(loop(1))
    a.run_forever()
