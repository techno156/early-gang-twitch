# imports
import asyncio
import traceback
from obswebsocket import obsws
from obswebsocket import requests as obwsrequests
from libraries.chatPlays import *
from bots import commandBot, econBot, pollBot

# main code loop
async def main():

    # setting up
    commandBot.ws.connect()
    await updateSnatus()

    # so you don't have to restart stream
    if await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) != []:
        await startChatPlays()
        await startAutoSave()
        await startInputBot()
        await startIdleBot()

    # infinite loop to check stream statuses
    while True:

        # if streamer goes live
        if await commandBot.bot.fetch_streams(user_logins = [commandBot.streamerChannelName]) != [] and await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) != []:

            # shut down everything
            if chatPlaying:
                await stopChatPlays()
            if autoSaving:
                await stopAutoSave()
            if inputBotPlaying:
                await stopInputBot()
            if idleBotPlaying:
                await stopIdleBot()

            # end stream
            if await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) != []:
                users = await commandBot.bot.fetch_users([commandBot.yourChannelName, commandBot.streamerChannelName])
                await users[0].start_raid(commandBot.accessToken, users[1].id)
                commandBot.ws.call(obwsrequests.StopStreaming())


        # if streamer goes offline
        elif await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) == [] and await commandBot.bot.fetch_streams(user_logins = [commandBot.streamerChannelName]) == []:

            # start stream
            if await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) == []:
                commandBot.ws.call(obwsrequests.StartStreaming())
            if not chatPlaying:
                await startChatPlays()
            if not autoSaving:
                await startAutoSave()
            if not inputBotPlaying:
                await startInputBot()
            if not idleBotPlaying:
                await startIdleBot()

        await asyncio.sleep(3)

# running command bot for inputs
async def setup():
    await asyncio.gather(commandBot.Bot().start(), econBot.Bot().start(), pollBot.Bot().start(), main())

# don't touch this
try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.run_forever()
except Exception as e:
    print(e)
    traceback.print_exc()