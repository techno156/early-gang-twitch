# responds to basic commands in chat
# don't fuck with this too much unless you're familiar with twitchio and how it works
# not much documentation here because even i don't know what the fuck this object oriented programming is doing in python

# imports
from urllib.parse import urlencode
import aiosqlite
from twitchio.ext import commands
import base64
from libraries.chatPlays import *
import requests

# setting up variables
chatters = []
timeSinceLastWelcome = time.time()

# reading config
config = configparser.ConfigParser()
config.read(os.path.abspath((os.path.join(directory, "config.ini"))))
spotifyClientID = config.get("spotify", "client id")
spotifyClientSecret = config.get("spotify", "client secret")
spotifyRefreshToken = config.get("spotify", "spotify refresh token")

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
        print("problem getting tokens " + response.json())

class Bot(commands.Bot):

    # sets up bot and connects to twitch
    def __init__(self):
        super().__init__(token = accessToken, prefix="!", initial_channels = [yourChannelName])

    # makes the bot shut the hell up about commands not existing
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)

    # when someone sends a message in chat
    async def event_message(self, message):
        global chatters
        global timeSinceLastWelcome

        # don't take bot messages as real messages
        if message.echo:
            return

        # making controller input
        await asyncio.create_task(controller(message.content))
        chatPlays.timeSinceLastMessage = time.time()
        await self.handle_commands(message)

    # sends list of chat plays controls
    @commands.command()
    async def controls(self, ctx: commands.Context):
        await ctx.send("[bot] (capitalization doesnt matter) up, down, left, right, left+, right+, up+, down+ hold up, hold down, hold left, hold right, a, hold a, mash a, b, hold b, mash b, l, r, start, select, stop, wander, up wander, down wander, left wander, right wander, slight, sleft, slup, slown")

    # sends what's going on
    @commands.command()
    async def what(self, ctx: commands.Context):
        await ctx.send("[bot] chat tries to beat pokemon ruby before dougdoug streams again")

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
        await ctx.send("[bot] !what, !bots, !song, !controls, !vote, !poll, !discord, !watchtime, !bp, !donate, !playlist, !bpShop, !snackFamily")

    # sends a list of sll the different input bots
    @commands.command()
    async def snackFamily(self, ctx: commands.Context):
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
                    print("error refreshing token: " + data)
                    accessToken = None

            # get song
            if accessToken:
                async with session.get("https://api.spotify.com/v1/me/player/currently-playing", headers = {"Authorization": "Bearer " + accessToken}) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['is_playing']:
                            await ctx.send(f"[bot] {data['item']['name']} by {data['item']['artists'][0]['name']}")
                        else:
                            await ctx.send("[bot] no song playing")
                    else:
                        await ctx.send("[bot] can't get song")