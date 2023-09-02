# manages channel point economy and responds to commands relating to it
# don't fuck with this too much unless you're familiar with twitchio and how it works
# also you gotta know how to use sqlite3 so good luck ;)
# not much documentation here because even i don't know what the fuck this object oriented programming shit is doing in python

# imports
import sys
import traceback
import aiohttp
import aiosqlite
import time
import asyncio
from twitchio.ext import commands
from libraries.chatPlays import *
from bots import commandBot
from libraries import chatPlays
import os

# setting up variables
chatters = []
live = False
firstRedeemed = True
activeCodes = []

class Bot(commands.Bot):

    # sets up bot and connects to twitch
    def __init__(self):
        super().__init__(token = commandBot.accessToken, prefix = "!", initial_channels = [commandBot.yourChannelName])

    # makes the bot shut the hell up about commands not existing
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # starts updating database
    async def event_ready(self):
        await self.updateWatchTime()

    # whenever a user joins write their id and entry time into an array and add their id to the database if not there
    async def event_join(self, channel, user):
        global chatters
        user = await commandBot.bot.fetch_users([user.name])
        user = user[0]

        # adds chatter id, watch time start, and uptime start
        if user.id is not None:
            if user.id not in chatters:
                chatters += [[user.id, time.time(), time.time()]]

            # reading database
            try:
                async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                    async with db.execute("SELECT id FROM economy WHERE id=?", (user.id,)) as cursor:
                        result = await cursor.fetchone()

                        # adding id if not in database
                        if not result:
                            await db.execute("INSERT INTO economy (id, watchtime, points) VALUES (?, ?, ?)", (user.id, 0, 0,))
                            await db.commit()
            except:
                print("\033[91mFUCK THERE'S A DOUBLE ID\033[0m")

    # whenever a user leaves add their remaining time to the csv and remove them from the array
    async def event_part(self, user):

        global chatters

        # finding chatter's time
        chatter = None
        for element in chatters:
            if element[0] == user.id:
                chatter = element
                break

        # writing chatter time to file
        if chatter and await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) != []:
            async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (user.id,)) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        await cursor.execute("UPDATE economy SET watchtime=? WHERE id=?", ((float(result[1]) + (time.time() - chatter[1])),  user.id,))
                        await db.commit()

            # removing chatter from active chatter list
            if chatter in chatters:
                chatters.remove(chatter)

    # sends a message with the user's watch time formatted as days, hours, minutes, seconds
    @commands.command()
    async def watchtime(self, ctx: commands.Context):

        # checking own points
        if ctx.message.content == "!watchtime" or ctx.message.content == "!watchtime ":

            async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,)) as cursor:
                    result = await cursor.fetchone()

        # letting whitelisters check others' points
        else:
            if ctx.author.name in commandBot.tokens:
                ctx.message.content = ctx.message.content.replace("!watchtime ", "")
                user = await commandBot.bot.fetch_users([ctx.message.content])
    
                async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                    async with db.execute("SELECT * FROM economy WHERE id=?", (user[0].id,)) as cursor:
                        result = await cursor.fetchone()

        # calculating output
        if result:
            seconds = round(float(result[1]))
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            weeks, days = divmod(days, 7)
            months, weeks = divmod(weeks, 4)
            years, months = divmod(months, 12)
            centuries, years = divmod(years, 100)

            duration = ""
            if centuries > 0:
                duration += str(centuries) + " centuries "
            if years > 0:
                duration += str(years) + " years "
            if months > 0:
                duration += str(months) + " months "
            if weeks > 0:
                duration += str(weeks) + " weeks "
            if days > 0:
                duration += str(days) + " days "
            if hours > 0:
                duration += str(hours) + " hours "
            if minutes > 0:
                duration += str(minutes) + " minutes "
            if seconds > 0:
                duration += str(seconds) + " seconds"
            if duration == "":
                duration += str(seconds) + " seconds"

            # outputting based on command
            if ctx.message.content == "!watchtime" or ctx.message.content == "!watchtime ":
                await ctx.send("[bot] " + ctx.author.name + " has watched " + commandBot.yourChannelName + " for " + duration)
            else:
                await ctx.send("[bot] " + ctx.message.content + " has watched " + commandBot.yourChannelName + " for " + duration)

    # tells the user how many points they have
    @commands.command()
    async def bp(self, ctx: commands.Context):

        # checking own points
        if ctx.message.content == "!bp" or ctx.message.content == "!bp ":

            async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,),) as cursor:
                    result = await cursor.fetchone()

            # sending result if id exists
            if result:
                await ctx.send("[bot] " + ctx.author.name + " has " + str(result[2]) + " basement pesos")

        # letting whitelisters check others' points
        else:
            if ctx.author.name in commandBot.tokens:

                ctx.message.content = ctx.message.content.replace("!bp ", "")
                user = await commandBot.bot.fetch_users([ctx.message.content])
                async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                    async with db.execute("SELECT * FROM economy WHERE id=?", (user[0].id,)) as cursor:
                        result = await cursor.fetchone()

                # sending result if id exists
                if result:
                    await ctx.send("[bot] " + ctx.message.content + " has " + str(result[2]) + " basement pesos")

    # lets users give their points to each other
    @commands.command()
    async def givebp(self, ctx: commands.Context):

        # checks if it's a whitelister so that they can print money
        if ctx.author.name in commandBot.tokens:

            # error handling
            if ctx.message.content == "!givebp" or ctx.message.content == "!givebp ":
                await ctx.send("please include the user and amount your command messages formatted like !giveBP user 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!givebp ", "")
                ctx.message.content = ctx.message.content.split()
                users = await commandBot.bot.fetch_users([ctx.message.content[0]])

                if users[0].id and ctx.message.content[0] not in commandBot.tokens or ctx.author.name == ctx.message.content[0]:
                    async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (users[0].id,)) as cursor:
                            result = await cursor.fetchone()
                            await cursor.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] + int(ctx.message.content[1])), users[0].id, ))
                            await db.commit()

                    await ctx.send("[bot] gave " + ctx.message.content[0] + " " + ctx.message.content[1] + " basement pesos")
                else:
                    await ctx.send("[bot] no bribery")

        # actually transfer money if it's not a whitelister
        else:

            # error handling
            if ctx.message.content == "!givebp" or ctx.message.content == "!givebp ":
                await ctx.send("please include the user and amount your command messages formatted like !giveBP user 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!givebp ", "")
                ctx.message.content = ctx.message.content.split()
                users = await commandBot.bot.fetch_users([ctx.message.content[0]])

                # no stealing >:)
                if int(ctx.message.content[1]) < 0:
                    await ctx.send("[bot] nice try")

                # if both users exist
                elif ctx.author.id and users[0].id:

                    # finding giver and taker
                    async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,)) as cursor:
                            giver = await cursor.fetchone()

                        async with db.execute("SELECT * FROM economy WHERE id=?", (users[0].id,)) as cursor:
                            taker = await cursor.fetchone()

                        # check if giver has enough points
                        if giver[2] <= int(ctx.message.content[1]):
                            await ctx.send("[bot] not enough basement pesos")

                        elif str((ctx.author.name).lower()) == str((ctx.message.content[0]).lower()):
                            await ctx.send("[bot] nice try")

                        # transfer money
                        elif giver and taker:
                            await db.execute("UPDATE economy SET points=? WHERE id=?", ((giver[2] - int(ctx.message.content[1])), ctx.author.id))
                            await db.execute("UPDATE economy SET points=? WHERE id=?", ((taker[2] + int(ctx.message.content[1])), users[0].id))
                            await db.commit()

                            await ctx.send("[bot] " + ctx.author.name + " gave " + ctx.message.content[0] + " " + ctx.message.content[1] + " basement pesos")

                        # error handling
                        else:
                            await ctx.send("[bot] couldn't find at least one user")
                else:
                    await ctx.send("[bot] couldn't find at least one user")

    # lets whitelisters take points
    @commands.command()
    async def bptax(self, ctx: commands.Context):

        # checks if the chatter can do this
        if ctx.author.name in commandBot.tokens:
            # error handling
            if ctx.message.content == "!bptax" or ctx.message.content == "!bptax ":
                await ctx.send("please include the user and amount your command messages formatted like !bpTax user, 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!bptax ", "")
                ctx.message.content = ctx.message.content.split()
                users = await commandBot.bot.fetch_users([ctx.message.content[0]])

                # no negative numbers
                if int(ctx.message.content[1]) < 0:
                    await ctx.send("[bot] nice try")

                # seeing if user exists
                elif users[0].id:
                    async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (users[0].id,)) as cursor:
                            result = await cursor.fetchone()

                        # if user in database
                        if result:
                            await db.execute("UPDATE economy SET points=? WHERE id=?", (result[2] - int(ctx.message.content[1]), users[0].id))
                            await db.commit()
                            await ctx.send("[bot] took from " + ctx.message.content[0] + " " + ctx.message.content[1] + " basement pesos")

    # lists commands available for purchase
    @commands.command()
    async def bpshop(self, ctx: commands.Context):
        await ctx.send("[bot] !shoot (1000), !shootsnack (800), !swapsnack (150), !healsnack (500)")

    # times out user
    @commands.command()
    async def shoot(self, ctx: commands.Context):
        duration = random.randint(10, 60)
        finalId = ""
        user = await commandBot.bot.fetch_users([commandBot.yourChannelName])

        # thread to wait to remod a mod after timing them out
        async def remod(id, duration):
            await asyncio.sleep(duration)
            user = await commandBot.bot.fetch_users([commandBot.yourChannelName])

            modIds = []
            while str(id) not in modIds:
                connected = False
                while not connected:

                    try:
                        async with aiohttp.ClientSession(headers = {"Client-ID": commandBot.clientID, "Authorization": "Bearer " + commandBot.accessToken}) as session:
                            async with session.get("https://api.twitch.tv/helix/users") as response:
                                rateLimit = response.headers.get("Ratelimit-Remaining")
                                if rateLimit != "0":
                                    await session.post("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + str(user[0].id )+ "&user_id=" + id)
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
                    async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": commandBot.clientID, "Authorization": "Bearer " + commandBot.accessToken}) as response:
                        rateLimit = response.headers.get("Ratelimit-Remaining")
                        if rateLimit != "0":
                            async with session.get("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + str(user[0].id), headers={"Authorization": "Bearer " + commandBot.accessToken, "Client-Id": commandBot.clientID}) as response:
                                mod_data = await response.json()
                                connected = True
                        else:
                            await asyncio.sleep(5)
            except:
                await asyncio.sleep(5)

        modIds = [mod.get("user_id") for mod in mod_data.get("data")]

        # if no person named shoot random
        if ctx.message.content == "!shoot":
            # finding user id in database
            async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,)) as cursor:
                    result = await cursor.fetchone()

                # check if user has the money
                if result[2] < 1000 and ctx.author.name not in commandBot.tokens:
                    await ctx.send("[bot] not enough basement pesos")
                else:
                    if ctx.author.name not in commandBot.tokens:
                        await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 1000), ctx.author.id))
                        await db.commit()
                    connected = False
                    while not connected:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": commandBot.clientID, "Authorization": "Bearer " + commandBot.accessToken}) as response:
                                    rateLimit = response.headers.get("Ratelimit-Remaining")
                                    if rateLimit != "0":
                                        async with session.get("https://api.twitch.tv/helix/chat/chatters?broadcaster_id=" + str(user[0].id) + "&moderator_id=" + str(user[0].id), headers = {"Authorization": "Bearer " + commandBot.accessToken, "Client-Id": commandBot.clientID}) as response:
                                            chatters_data = await response.json()
                                            connected = True
                        except:
                            await asyncio.sleep(5)

                    names = [[element.get("user_id"), element.get("user_name")] for element in chatters_data.get("data")]
                    user = names[random.randint(0, len(names) - 1)]

                    # getting item and action
                    async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
                        async with db.execute("SELECT item FROM items ORDER BY RANDOM() LIMIT 1") as cursor:
                            item = str(await cursor.fetchone()).replace("(", "").replace(")", "").replace(",", "")
                            if item[0] == "\'":
                                item = item.replace("\'", "")
                            else:
                                item = item.replace("\"", "")

                        async with db.execute("SELECT action FROM pastTenseActions ORDER BY RANDOM() LIMIT 1") as cursor:
                            pastTenseAction = str(await cursor.fetchone()).replace("(", "").replace(")", "").replace(",","")
                            if pastTenseAction[0] == "\'":
                                pastTenseAction = pastTenseAction.replace("\'", "")
                            else:
                                pastTenseAction = pastTenseAction.replace("\"", "")

                    user = await commandBot.bot.fetch_users([user[1], commandBot.yourChannelName])
                    try:
                        await user[1].timeout_user(commandBot.accessToken, user[1].id, user[0].id, duration, "you got shot")
                    except:
                        pass
                    await ctx.send("[bot] " + ctx.author.name + " " + pastTenseAction + " " + user[0].name + " with " + item)

                    # setting up remod thread if needed
                    if str(user[0].id) in modIds:
                        asyncio.create_task(remod(str(user[0].id), duration))

        # try to shoot the listed person
        else:
            # finding user id in database
            async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
                cursor = await db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,))
                result = await cursor.fetchone()

                # check if the user has the money
                if result[2] < 1000 and ctx.author.name not in commandBot.tokens:
                    await ctx.send("[bot] not enough basement pesos")
                else:
                    if ctx.author.name not in commandBot.tokens:
                        await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 1000), ctx.author.id))
                        await db.commit()

                    dice = random.randint(1, 100)
                    ctx.message.content = (ctx.message.content).replace("!shoot ", "")
                    id = await commandBot.bot.fetch_users([ctx.message.content])
                    id = id[0].id

                    # error handling
                    if id is None:
                        await ctx.send("[bot] couldn't find user")

                    # shooting based on dice
                    else:
                        async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:

                            # getting item and action
                            async with db.execute("SELECT item FROM items ORDER BY RANDOM() LIMIT 1") as cursor:
                                item = str(await cursor.fetchone()).replace("(", "").replace(")", "").replace(",", "")
                                if item[0] == "\'":
                                    item = item.replace("\'", "")
                                else:
                                    item = item.replace("\"", "")

                            async with db.execute("SELECT action FROM pastTenseActions ORDER BY RANDOM() LIMIT 1") as cursor:
                                pastTenseAction = str(await cursor.fetchone()).replace("(", "").replace(")", "").replace(",", "")
                                if pastTenseAction[0] == "\'":
                                    pastTenseAction = pastTenseAction.replace("\'", "")

                            async with db.execute("SELECT action FROM presentTenseActions ORDER BY RANDOM() LIMIT 1") as cursor:
                                presentTenseAction = str(await cursor.fetchone()).replace("(", "").replace(")", "").replace(",", "")
                                if presentTenseAction[0] == "\'":
                                    presentTenseAction = presentTenseAction.replace("\'", "")
                                else:
                                    presentTenseAction = presentTenseAction.replace("\"", "")

                        # 10% chance to shoot yourself
                        if dice > 90:
                            finalId = ctx.author.id
                            await ctx.send("[bot] " + ctx.author.name + " missed and " + item + " bounced into their head")

                        # 65% chance to shoot random
                        elif dice > 25:

                            connected = False
                            while not connected:
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": commandBot.clientID, "Authorization": "Bearer " + commandBot.accessToken}) as response:
                                            rateLimit = response.headers.get("Ratelimit-Remaining")
                                            if rateLimit != "0":
                                                async with session.get("https://api.twitch.tv/helix/chat/chatters?broadcaster_id=" + str(user[0].id) + "&moderator_id=" + str(user[0].id), headers= {"Authorization": "Bearer " + commandBot.accessToken, "Client-Id": commandBot.clientID}) as response:
                                                    response = await response.json()
                                                    connected = True
                                except:
                                    await asyncio.sleep(5)

                            names = [[element.get("user_id"), element.get("user_name")] for element in response.get("data")]
                            chat = names[random.randint(0, len(names) - 1)]
                            finalId = chat[0]
                            await ctx.send("[bot] " + ctx.author.name + " tried to " + presentTenseAction + " " + ctx.message.content + " with " + item + " but they used " + chat[1] + " as a shield")

                        # 25% chance to shoot target
                        else:
                            finalId = id
                            await ctx.send("[bot] " + ctx.author.name + " " + pastTenseAction + " " + ctx.message.content + " with " + item)

                        try:
                            await user[0].timeout_user(commandBot.accessToken, user[0].id, finalId, duration, "you got shot")
                        except:
                            pass
                        
                        if str(finalId) in modIds:
                            asyncio.create_task(remod(str(finalId), duration))

    # disables input bot for 35 to 95 minutes
    @commands.command()
    async def shootsnack(self, ctx: commands.Context):

        # thread to wait to restart input bot
        async def snackWait():
            await asyncio.sleep(random.randint(2100, 5700))
            chatPlays.snackShot = False
            chatPlays.snackHealed = False
            await updateSnatus()

        # finding user id in database
        async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
            async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,)) as cursor:
                result = await cursor.fetchone()

            # check if user has the money
            if result[2] < 800 and ctx.author.name not in commandBot.tokens:
                await ctx.send("[bot] not enough basement pesos")
            else:
                if ctx.author.name not in commandBot.tokens:
                    await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 800), ctx.author.id))
                    await db.commit()

                # getting random action and item
                async with db.execute("SELECT item FROM items ORDER BY RANDOM() LIMIT 1") as cursor:
                    item = await cursor.fetchone()

                item = str(item).replace("(", "").replace(")", "").replace(",", "")
                if item[0] == "\'":
                    item = item.replace("\'", "")
                else:
                    item = item.replace("\"", "")

                async with db.execute("SELECT action FROM pastTenseActions ORDER BY RANDOM() LIMIT 1") as cursor:
                    action = await cursor.fetchone()

                action = str(action).replace("(", "").replace(")", "").replace(",", "")
                if action[0] == "\'":
                    action = action.replace("\'", "")
                else:
                    action = action.replace("\"", "")

                # disabling input bot
                chatPlays.snackShot = True
                chatPlays.snackHealed = False
                await ctx.send("[bot] " + ctx.author.name + " " + action + " " + chatPlays.currentSnack + " snack with " + item)
                if not chatPlays.idleBotStatus:
                    await updateSnatus()
                asyncio.create_task(snackWait())

    # reactivates input bot
    @commands.command()
    async def healsnack(self, ctx: commands.Context):

        async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
            async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,)) as cursor:
                result = await cursor.fetchone()

            # check if user has the money
            if result[2] < 500 and ctx.author.name not in commandBot.tokens:
                await ctx.send("[bot] not enough basement pesos")
            else:
                if ctx.author.name not in commandBot.tokens:
                    await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 500), ctx.author.id))
                    await db.commit()

                # getting random item
                async with db.execute("SELECT item FROM items ORDER BY RANDOM() LIMIT 1") as cursor:
                    item = await cursor.fetchone()

                item = str(item).replace("(", "").replace(")", "").replace(",", "")
                if item[0] == "\'":
                    item = item.replace("\'", "")
                else:
                    item = item.replace("\"", "")

                # enabling bot
                dice = random.randint(1, 100)
                if chatPlays.snackShot and dice < 56:
                    chatPlays.snackHealed = True
                    if not chatPlays.idleBotStatus:
                        await updateSnatus()
                    await ctx.send("[bot] " + ctx.author.name + " healed " + chatPlays.currentSnack + " snack with " + item)
                else:
                    await ctx.send("[bot] " + ctx.author.name + " failed to heal " + chatPlays.currentSnack + " snack with " + item)

    # changes input bot type
    @commands.command()
    async def swapsnack(self, ctx: commands.Context):

        # finding user id in database
        async with aiosqlite.connect(os.path.abspath(os.path.join(commandBot.directory, "chatData.db"))) as db:
            async with db.execute("SELECT * FROM economy WHERE id=?", (ctx.author.id,)) as cursor:
                result = await cursor.fetchone()

            # check if the user has enough money
            if result[2] < 150 and ctx.author.name not in commandBot.tokens:
                await ctx.send("[bot] not enough basement pesos")
            else:
                if ctx.author.name not in commandBot.tokens:
                    await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 150), ctx.author.id))
                    await db.commit()

                commandBot.chatPlays.currentSnack = snacks[random.randint(0, len(snacks) - 1)]
                await ctx.send("[bot] " + chatPlays.currentSnack + " snack was swapped in")
                if not chatPlays.idleBotStatus:
                    await updateSnatus()
    
    # creates a poll and lets chatters vote on who's guilty
    @commands.command()
    async def sue(self, ctx: commands.Context):
        '''if ctx.message.content == "!sue" or ctx.message.content == "!sue ":
                await ctx.send("please include the user and amount your command messages formatted like !sue user 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!givebp ", "")
                ctx.message.content = ctx.message.content.split()
                users = await commandBot.bot.fetch_users([ctx.message.content[0]])'''
        # extract user and amount

        # send poll (and pin it??)

        # wait 30 seconds

        # payout
        pass

    # as soon as bot is logged in constantly check the array and update watch time and points
    async def updateWatchTime(self):
        global chatters
        global live
        global firstRedeemed

        while True:
            await asyncio.sleep(10)

            # when channel goes live reset uptime and !first
            if await commandBot.bot.fetch_streams(user_logins = [commandBot.yourChannelName]) != []:
                if not live:
                    for element in chatters:
                        element[1] = time.time()
                        element[2] = time.time()
                    live = True
                    firstRedeemed = False

                # update database for all users in chat
                for chatter in chatters:
                    async with aiosqlite.connect(os.path.abspath((os.path.join(commandBot.directory, "chatData.db")))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (chatter[0],)) as cursor:
                            result = await cursor.fetchone()

                            # setting points and watchtime
                            if result:
                                if (time.time() - chatter[2]) >= 300:
                                    await db.execute("UPDATE economy SET points=? WHERE id=?", (result[2] + 10, chatter[0]))
                                    chatter[2] = time.time()

                                await db.execute("UPDATE economy SET watchtime=? WHERE id=?", (float(result[1]) + (time.time() - chatter[1]), chatter[0]))
                                chatter[1] = time.time()

                        await db.commit()

            else:
                live = False