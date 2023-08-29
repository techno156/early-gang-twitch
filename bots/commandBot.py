# responds to basic commands in chat
# don't fuck with this too much unless you're familiar with twitchio and how it works
# not much documentation here because even i don't know what the fuck this object oriented programming is doing in python

# imports
from urllib.parse import urlencode
import aiohttp
from twitchio.ext import commands
import base64
import requests
import asyncio
from obswebsocket import obsws
from obswebsocket import requests as obwsrequests
from libraries.chatPlays import *

# setting up variables
whiteListers = ["dougdoug", "parkzer", "gwrbull", "sna1l_boy", "jaytsoul", "purpledalek", "ramcicle", "fratriarch"]
chatters = []

# setting directory if file is ran correctly
directory = ""
if os.path.exists(os.path.abspath(os.path.join("files"))):
    directory = os.path.abspath(os.path.join("files"))

# finding the file because i'm too fucking lazy to teach people how to use the terminal plus BLOCK OF TEXT SCARY AAAAAAAAAAAH
else:

    # setting up loading message
    dotCount = 0
    lastUpdate = time.time()
    print("\033[1K\rloading", end = "", flush = True)

    # checking file by file
    for root, dirs, files in os.walk("\\"):

        # creating loading message
        if time.time() - lastUpdate > .5:
            if dotCount != 0:
                print(".", end="", flush=True)
            else:
                print("\033[1K\rloading", end = "", flush = True)
            dotCount = 0 if dotCount == 3 else dotCount + 1
            lastUpdate = time.time()

        # checking if file matches
        if "early-gang-twitch-main\\files\\config.ini" in os.path.abspath(os.path.join(root, "config.ini")):
            directory = os.path.abspath(os.path.join(root))

# printing on ready statement
if directory == "":
    print("\033[1K:\033[31m\rfuck it\033[0m")
else:
    print("\033[1K:\033[36m\rfuck it we ball\033[0m")

# reading config
config = configparser.ConfigParser()
config.read(os.path.abspath((os.path.join(directory, "config.ini"))))
clientID = config.get("twitch", "client id")
accessToken = config.get("twitch", "access token")
streamerChannelName = config.get("twitch", "streamer channel name")
yourChannelName = config.get("twitch", "your channel name")
spotifyClientID = config.get("spotify", "client id")
spotifyClientSecret = config.get("spotify", "client secret")
spotifyRefreshToken = config.get("spotify", "spotify refresh token")
websocketPassword = config.get("obs", "websocket server password")

ws = obsws("localhost", 4444, websocketPassword)

# if you don't have a refresh token
if spotifyRefreshToken == "":

    # getting code from user
    print(f'authorize this script by going to:\n{"https://accounts.spotify.com/authorize" + "?" + urlencode({"client_id": spotifyClientID, "response_type": "code", "redirect_uri": "http://localhost:8888/callback", "scope": "user-read-currently-playing user-modify-playback-state"})}')
    authorizationCode = input("enter the authorization code found in the redirected url after \"code=\": ")

    # gets access token and refresh token using the code
    response = requests.post("https://accounts.spotify.com/api/token", auth = (spotifyClientID, spotifyClientSecret), data = {"grant_type": "authorization_code", "code": authorizationCode, "redirect_uri": "http://localhost:8888/callback"})

    # writes refresh token to info file for future use
    if 'refresh_token' in response.json():
        with open(os.path.abspath((os.path.join(directory, "config.ini"))), 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith("spotify refresh token ="):
                    lines[i] = "spotify refresh token = " + response.json()["refresh_token"] + "\n"
                    break
            with open(os.path.abspath((os.path.join(directory, "config.ini"))), "w") as file:
                file.writelines(lines)
    else:
        print("\033[91mSPOTIFY FUCKED UP\033[0m")

class Bot(commands.Bot):

    # sets up bot and connects to twitch
    def __init__(self):
        super().__init__(token = accessToken, prefix="!", initial_channels = [yourChannelName])

    # makes the bot shut the hell up about commands not existing
    async def event_command_error(self, cxt, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)

    # when someone sends a message in chat
    async def event_message(self, message):
        global chatters

        # don't take bot messages as real messages
        if message.echo:
            return
        
        if "deez nuts" in message.content.lower() or "D:\\ eez nuts" in message.content.lower():
            duration = random.choice([420, 69])
            user = await bot.fetch_users([yourChannelName])
            
            # thread to wait to remod a mod after timing them out
            async def remod(id, duration):
                await asyncio.sleep(duration)
                user = await bot.fetch_users([yourChannelName])

                modIds = []
                while str(id) not in modIds:
                    connected = False
                    while not connected:
                        try:
                            async with aiohttp.ClientSession(headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as session:
                                async with session.get("https://api.twitch.tv/helix/users") as response:
                                    rateLimit = response.headers.get("Ratelimit-Remaining")
                                    if rateLimit != "0":
                                        await session.post("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + str(user[0].id) + "&user_id=" + id)
                                        async with session.get("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + str(user[0].id)) as response:
                                            modIds = []
                                            for mod in (await response.json()).get("data"):
                                                modIds.append(str(mod.get("user_id")))
                                            connected = True
                                    else:
                                        await asyncio.sleep(5)
                        except:
                            await asyncio.sleep(5)

            # getting mod ids
            connected = False
            while not connected:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get("https://api.twitch.tv/helix/users", headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                            rateLimit = response.headers.get("Ratelimit-Remaining")
                            if rateLimit != "0":
                                async with session.get("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + str(user[0].id), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID}) as response:
                                    mod_data = await response.json()
                                    connected = True
                            else:
                                await asyncio.sleep(5)
                except:
                    await asyncio.sleep(5)
            modIds = [mod.get("user_id") for mod in mod_data.get("data")]

            # timing out
            try:
                await user[0].timeout_user(accessToken, user[0].id, message.author.id, duration, "GOTTEM")
            except:
                pass

            # setting up remod thread
            if str(message.author.id) in modIds:
                asyncio.create_task(remod(str(message.author.id), duration))

        # making controller input
        await asyncio.create_task(controller(message.content))
        await self.handle_commands(message)

    # sends list of chat plays controls
    @commands.command()
    async def controls(self, ctx: commands.Context):
        await ctx.send("[bot] (capitalization doesnt matter) up, down, left, right, shoot, cheat")

    # sends what's going on
    @commands.command()
    async def what(self, ctx: commands.Context):
        await ctx.send("[bot] chat tries to beat douggle before dougdoug streams again")

    # sends dougdoug channel link
    @commands.command()
    async def dougdoug(self, ctx: commands.Context):
        await ctx.send("[bot] https://www.twitch.tv/dougdoug")

    # sends a list of all the bots
    @commands.command()
    async def bots(self, ctx: commands.Context):
        await ctx.send("[bot] input bot, aka chris snack, presses a random button every minute or so, idle bot steals your controller if you leave it alone for five minutes, and theres a 5% chance of your own input being completely random or the opposite")

    # sends a list of commands
    @commands.command()
    async def menu(self, ctx: commands.Context):
        await ctx.send("[bot] !what, !bots, !song, !controls, !vote, !poll, !discord, !watchtime, !bp, !donate, !playlist, !bpshop, !snackfamily")

    # sends a list of sll the different input bots
    @commands.command()
    async def snackfamily(self, ctx: commands.Context):
        await ctx.send("[bot] sleepy, chris, burst, silly, cautious, sonic")

    # sends link to discord
    @commands.command()
    async def discord(self, ctx: commands.Context):
        await ctx.send("[bot] https://discord.gg/cnrvMKfacy")

    # sends link to tiltify page
    @commands.command()
    async def donate(self, ctx: commands.Context):
        await ctx.send("[bot] https://tiltify.com/@early-gang/profile")

    # sends link to stream music playlist
    @commands.command()
    async def playlist(self, ctx: commands.Context):
        await ctx.send("[bot] https://open.spotify.com/playlist/2zBtOh6PAFBGCnlA7oSsEm?si=4a576dfd1c534357")

    # allows mods to start stream
    @commands.command()
    async def startstream(self, ctx: commands.Context):
        if ctx.author.name in whiteListers:
             ws.call(obwsrequests.StartStreaming())
    
    # allows mods to stop stream
    @commands.command()
    async def stopstream(self, ctx: commands.Context):
        if ctx.author.name in whiteListers:
            ws.call(obwsrequests.StopStreaming())
    
    # allows mods to raid
    @commands.command()
    async def raid(self, ctx: commands.Context):
        if ctx.author.name in whiteListers:
            ctx.message.content = ctx.message.content.replace("!raid ", "")
            users = await bot.fetch_users([yourChannelName, ctx.message.content])
            print(users)
            await users[0].start_raid(accessToken, users[1].id)

    # sends a message with the currently playing song
    @commands.command()
    async def song(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:

            # create access token
            async with session.post("https://accounts.spotify.com/api/token", headers={"Authorization": "Basic " + base64.b64encode(f"{spotifyClientID}:{spotifyClientSecret}".encode()).decode()}, data={"grant_type": "refresh_token", "refresh_token": spotifyRefreshToken}) as response:
                data = await response.json()
                if "access_token" in data:
                    accessToken = data["access_token"]
                else:
                    print("\033[91mSPOTIFY FUCKED UP\033[0m")
                    accessToken = None

            # get song
            if accessToken:
                async with session.get("https://api.spotify.com/v1/me/player/currently-playing", headers = {"Authorization": "Bearer " + accessToken}) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["is_playing"]:
                            await ctx.send("[bot] " + data["item"]["name"] + " by " + data["item"]["artists"][0]["name"])
                        else:
                            await ctx.send("[bot] no song playing")
                    else:
                        await ctx.send("[bot] can't get song")

bot = Bot()