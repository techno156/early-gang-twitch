# functions for doing stream stuff remotely/semi-remotely 

# imports
import configparser
import os
import time

import aiohttp
import asyncio

# setting up variables
whiteListers = ["dougdoug", "parkzer", "gwrbull", "sna1l_boy", "fratriarch", "jaytsoul", "purpledalek", "ramcicle"]

# setting directory if file is ran correctly
directory = ""
if os.path.exists(os.path.abspath(os.path.join("files"))):
    directory = os.path.abspath(os.path.join("files"))

# finding the file because im too fucking lazy to teach people how to use the terminal plus BLOCK OF TEXT SCARY AAAAAAAAAAAH
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
    print("\033[1K:\033[31m\rAAAA FUCK THERE'S NO FILES FOLDER AAAAAAAAAAAAAAAAA\033[0m")
else:
    print("\033[1K:\033[36m\rfuck it we ball\033[0m")

# reading config
config = configparser.ConfigParser()
config.read(os.path.abspath((os.path.join(directory, "config.ini"))))
clientID = config.get("twitch", "client id")
accessToken = config.get("twitch", "access token")
streamerChannelName = config.get("twitch", "streamer channel name")
yourChannelName = config.get("twitch", "your channel name")

# checks if a channel is live then returns true if they are, false if not, and none if an error occurs
async def isLive(channelName):

    # asking twitch for the information
    try:
        async with aiohttp.ClientSession(headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as session:
            async with session.get("https://api.twitch.tv/helix/users") as response:
                rateLimit = response.headers.get("Ratelimit-Remaining")
                if rateLimit != "0":
                    async with session.get("https://api.twitch.tv/helix/streams?user_login=" + channelName) as streamResponse:
                        if streamResponse.status == 200:
                            data = await streamResponse.json()
                            return True if data["data"] else False
                        else:
                            print("\033[91mTWITCH FUCKED UP\033[0m" )
                            return None
                # trying again
                else:
                    await asyncio.sleep(5)
                    await isLive(channelName)
    except:
        await asyncio.sleep(5)
        await isLive(channelName)

# looks up the id corresponding to a channel name
# needed for initiating raids
async def getBroadcasterId(channelName):

    # asking twitch for the id
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get("https://api.twitch.tv/helix/users", headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken})
            rateLimit = response.headers.get("Ratelimit-Remaining")
            if rateLimit != "0":
                response = await session.get("https://api.twitch.tv/helix/users?login=" + channelName, headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken})

                if response.status == 200:
                    data = await response.json()
                    if data["data"]:
                        broadcasterId = data["data"][0]["id"]
                        return broadcasterId

                    # error handling
                    else:
                        print("\033[91mTWITCH FUCKED UP\033[0m")

                # more error handling
                else:
                    await asyncio.sleep(5)
                    return await getBroadcasterId(channelName)
    except:
        await asyncio.sleep(5)
        return await getBroadcasterId(channelName)

# starts a raid from your channel to another
async def raid(raiderChannelName, raideeChannelName):

    # asking twitch to start raid
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                rateLimit = response.headers.get("Ratelimit-Remaining")
                if rateLimit != "0":
                    if await getBroadcasterId(raiderChannelName) and await getBroadcasterId(raideeChannelName):
                        async with session.post("https://api.twitch.tv/helix/raids", headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID}, params={"from_broadcaster_id": await getBroadcasterId(raiderChannelName), "to_broadcaster_id": await getBroadcasterId(raideeChannelName)}) as raid_response:
                            if raid_response.status != 200:
                                print("\033[91mTWITCH FUCKED UP\033[0m")

                    # trying again
                    else:
                        await raid(raiderChannelName, raideeChannelName)
                else:
                    await asyncio.sleep(5)
                    await raid(raiderChannelName, raideeChannelName)
    except:
        await asyncio.sleep(5)
        await raid(raiderChannelName, raideeChannelName)