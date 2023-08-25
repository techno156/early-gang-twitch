# imports
import asyncio
import traceback
from libraries.charityDonoTTS import *
from libraries.chatPlays import *
from bots import commandBot, econBot, pollBot

# main code loop
async def main():

    # setting up
    ws.connect()
    await updateSnatus()

    # so you don't have to restart stream
    if await bot.fetch_streams(user_logins = [yourChannelName]) != []:
        await startTTS()
        await startChatPlays()
        await startAutoSave()
        await startInputBot()
        await startIdleBot()

    # infinite loop to check stream statuses
    while True:

        # if streamer goes live
        if await bot.fetch_streams(user_logins = [streamerChannelName]) != [] and await bot.fetch_streams(user_logins = [yourChannelName]) != []:

            # shut down everything
            if ttsOn:
                await stopTTS()
            if chatPlaying:
                await stopChatPlays()
            if autoSaving:
                await stopAutoSave()
            if inputBotPlaying:
                await stopInputBot()
            if idleBotPlaying:
                await stopIdleBot()

            # end stream
            if await bot.fetch_streams(user_logins = [yourChannelName]) != []:
                users = await commandBot.bot.fetch_users([yourChannelName, streamerChannelName])
                await users[0].start_raid(accessToken, users[1].id)
                ws.call(obwsrequests.StopStreaming())


        # if streamer goes offline
        elif await bot.fetch_streams(user_logins = [yourChannelName]) == [] and await bot.fetch_streams(user_logins = [streamerChannelName]) == []:

            # start stream
            if await bot.fetch_streams(user_logins = [yourChannelName]) == []:
                ws.call(obwsrequests.StartStreaming())
            if not ttsOn:
                await startTTS()
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