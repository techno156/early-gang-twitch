# imports
import asyncio
import traceback
import aiofile
import os
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

                # start raid
                users = await commandBot.bot.fetch_users([commandBot.yourChannelName, commandBot.streamerChannelName])
                await users[0].start_raid(commandBot.accessToken, users[1].id)
                
                # display timer
                commandBot.ws.call(obwsrequests.SetSceneItemProperties(item = "raid status", visible = True))

                # update timer
                clock =  [1, 30]
                while clock != [0, 0]:
                    if clock[1] < 10:
                        ws.call(obwsrequests.SetTextGDIPlusProperties(source = "raid indicator", text = ("RAID INCOMING\n" + str(clock[0]) + ":0" + str(clock[1]))))
                    else:
                        ws.call(obwsrequests.SetTextGDIPlusProperties(source = "raid indicator", text = ("RAID INCOMING\n" + str(clock[0]) + ":" + str(clock[1]))))

                    if clock[1] == 0:
                        clock[1] = 59
                        clock[0] -= 1
                    else:
                        clock[1] -= 1
                    await asyncio.sleep(1)

                # stop raid and hide timer
                commandBot.ws.call(obwsrequests.StopStreaming())
                commandBot.ws.call(obwsrequests.SetSceneItemProperties(item = "raid status", visible = False))


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