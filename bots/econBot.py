# manages channel point economy and responds to commands relating to it
# don't fuck with this too much unless you're familiar with twitchio and how it works
# also you gotta know how to use sqlite3 so good luck ;)
# not much documentation here because even i don't know what the fuck this object oriented programming shit is doing in python

# imports
from datetime import datetime, timezone
import aiosqlite
from twitchio.ext import commands
from libraries.chatPlays import *

# setting up variables
chatters = []
live = False
firstRedeemed = True
activeCodes = []

class Bot(commands.Bot):

    # sets up bot and connects to twitch
    def __init__(self):
        super().__init__(token = accessToken, prefix = "!", initial_channels = [yourChannelName])

    # makes the bot shut the hell up about commands not existing
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)

    # starts updating database
    async def event_ready(self):
        await self.updateWatchTime()

    # whenever a user joins write their id and entry time into an array and add their id to the database if not there
    async def event_join(self, channel, user):
        global chatters

        # adds chatter id, watch time start, and uptime start
        if await getBroadcasterId(user.name) is not None:
            if await getBroadcasterId(user.name) not in chatters:
                chatters += [[await getBroadcasterId(user.name), time.time(), time.time()]]

            # reading database
            try:
                async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                    async with db.execute("SELECT id FROM economy WHERE id=?", (await getBroadcasterId(user.name),)) as cursor:
                        result = await cursor.fetchone()

                        # adding id if not in database
                        if not result:
                            await db.execute("INSERT INTO economy (id, watchtime, points) VALUES (?, ?, ?)", (await getBroadcasterId(user.name), 0, 0,))
                            await db.commit()
            except:
                print("FUCK THERE'S A DOUBLE ID")

    # whenever a user leaves add their remaining time to the csv and remove them from the array
    async def event_part(self, user):

        global chatters

        # finding chatter's time
        chatter = None
        for element in chatters:
            if element[0] == await getBroadcasterId(user.name):
                chatter = element
                break

        # writing chatter time to file
        if chatter and await isLive(yourChannelName):
            async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(user.name),)) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        await cursor.execute("UPDATE economy SET watchtime=? WHERE id=?", ((float(result[1]) + (time.time() - chatter[1])), await getBroadcasterId(user.name)))
                        await db.commit()

            # removing chatter from active chatter list
            if chatter in chatters:
                chatters.remove(chatter)

    # sends a message with the user's watch time formatted as days, hours, minutes, seconds
    @commands.command()
    async def watchtime(self, ctx: commands.Context):

        # checking own points
        if ctx.message.content == "!watchtime" or ctx.message.content == "!watchtime ":

            async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                    result = await cursor.fetchone()

        # letting whitelisters check others' points
        else:
            if ctx.author.name in whiteListers:
                ctx.message.content = ctx.message.content.replace("!watchtime ", "")
                async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                    async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.message.content),)) as cursor:
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
                await ctx.send("[bot] " + ctx.author.name + " has watched " + yourChannelName + " for " + duration)
            else:
                await ctx.send("[bot] " + ctx.message.content + " has watched " + yourChannelName + " for " + duration)

    # tells the user how many points they have
    @commands.command()
    async def bp(self, ctx: commands.Context):

        # checking own points
        if ctx.message.content == "!bp" or ctx.message.content == "!bp ":

            async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                    result = await cursor.fetchone()

            # sending result if id exists
            if result:
                await ctx.send("[bot] " + ctx.author.name + " has " + str(result[2]) + " basement pesos")

        # letting whitelisters check others' points
        else:
            if ctx.author.name in whiteListers:

                ctx.message.content = ctx.message.content.replace("!bp ", "")
                async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                    async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.message.content),)) as cursor:
                        result = await cursor.fetchone()

                # sending result if id exists
                if result:
                    await ctx.send("[bot] " + ctx.message.content + " has " + str(result[2]) + " basement pesos")

    # first user to redeem this gets points but those afterward lose points
    @commands.command()
    async def first(self, ctx: commands.Context):

        global firstRedeemed

        if await isLive(yourChannelName):

            # calculate points gained/loss
            connected = False
            while not connected:
                try:
                    async with aiohttp.ClientSession() as session:
                        response = await session.get("https://api.twitch.tv/helix/users", headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken})
                        rateLimit = response.headers.get("Ratelimit-Remaining")
                        if rateLimit != "0":
                            userResponse = await session.get(f"https://api.twitch.tv/helix/users?login={yourChannelName}", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken})
                            userResponseData = await userResponse.json()
                            streamResponse = await session.get("https://api.twitch.tv/helix/streams?user_id=" + userResponseData.get("data")[0].get("id"), headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken})
                            streamResponseData = await streamResponse.json()
                            connected = True
                        else:
                            await asyncio.sleep(5)
                except:
                    await asyncio.sleep(5)

            # in case uptime is 0
            try:
                points = round(1000 / ((datetime.now(timezone.utc) - datetime.fromisoformat(streamResponseData.get("data")[0].get("started_at")[:-1]).replace(tzinfo=timezone.utc)).total_seconds())) if round(1000 / ((datetime.now(timezone.utc) - datetime.fromisoformat(streamResponseData.get("data")[0].get("started_at")[:-1]).replace(tzinfo=timezone.utc)).total_seconds())) > 100 else 100
            except:
                points = 1000

            # searching database for id
            async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                    result = await cursor.fetchone()

                    # updating points
                    if result:

                        # if first !first, give points
                        if not firstRedeemed:
                            await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] + points), await getBroadcasterId(ctx.author.name)))

                            await ctx.send("[bot] " + ctx.author.name + " is first " + ctx.author.name + " gained " + str(points) + " basement pesos")
                            firstRedeemed = True

                        # if not first !first, take points
                        else:
                            if result[2] > 100:
                                await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - points), await getBroadcasterId(ctx.author.name)))
                            else:
                                await db.execute("UPDATE economy SET points=? WHERE id=?", (0, await getBroadcasterId(ctx.author.name)))
                            await ctx.send("[bot] " + ctx.author.name + " is not first " + ctx.author.name + " lost " + str(points) + " basement pesos")
                        await db.commit()

    # lets users give their points to each other
    @commands.command()
    async def giveBp(self, ctx: commands.Context):

        # checks if it's a whitelister so that they can print money
        if ctx.author.name in whiteListers:

            # error handling
            if ctx.message.content == "!giveBp" or ctx.message.content == "!giveBp ":
                await ctx.send("please include the user and amount your command messages formatted like !giveBP user, 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!giveBp ", "")
                ctx.message.content = ctx.message.content.split(", ")

                if await getBroadcasterId(ctx.message.content[0]) and ctx.message.content[0] not in whiteListers or ctx.author.name == ctx.message.content[0]:
                    async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.message.content[0]),)) as cursor:
                            result = await cursor.fetchone()
                            await cursor.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] + int(ctx.message.content[1])), await getBroadcasterId(ctx.message.content[0])))
                            await db.commit()

                    await ctx.send("[bot] gave " + ctx.message.content[0] + " " + ctx.message.content[1] + " basement pesos")
                else:
                    await ctx.send("[bot] no bribery")

        # actually transfer money if it's not a whitelister
        else:

            # error handling
            if ctx.message.content == "!giveBp" or ctx.message.content == "!giveBp ":
                await ctx.send("please include the user and amount your command messages formatted like !giveBP user, 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!giveBp ", "")
                ctx.message.content = ctx.message.content.split(", ")

                # no stealing >:)
                if int(ctx.message.content[1]) < 0:
                    await ctx.send("[bot] nice try")

                # if both users exist
                elif await getBroadcasterId(ctx.author.name) and await getBroadcasterId(ctx.message.content[0]):

                    # finding giver and taker
                    async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                            giver = await cursor.fetchone()

                        async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.message.content[0]),)) as cursor:
                            taker = await cursor.fetchone()

                        # check if giver has enough points
                        if giver[2] <= int(ctx.message.content[1]):
                            await ctx.send("[bot] not enough basement pesos")

                        elif str((ctx.author.name).lower()) == str((ctx.message.content[0]).lower()):
                            await ctx.send("[bot] nice try")

                        # transfer money
                        elif giver and taker:

                            await cursor.execute("UPDATE economy SET points=? WHERE id=?", ((giver[2] - int(ctx.message.content[1])), await getBroadcasterId(ctx.author.name)))
                            await cursor.execute("UPDATE economy SET points=? WHERE id=?", ((taker[2] + int(ctx.message.content[1])), await getBroadcasterId(ctx.message.content[0])))
                            await db.commit()

                            await ctx.send("[bot] " + ctx.author.name + " gave " + ctx.message.content[0] + " " + ctx.message.content[1] + " basement pesos")

                        # error handling
                        else:
                            await ctx.send("[bot] couldn't find at least one user")
                else:
                    await ctx.send("[bot] couldn't find at least one user")

    # lets whitelisters take points
    @commands.command()
    async def bpTax(self, ctx: commands.Context):

        # checks if the chatter can do this
        if ctx.author.name in whiteListers:
            # error handling
            if ctx.message.content == "!bpTax" or ctx.message.content == "!bpTax ":
                await ctx.send("please include the user and amount your command messages formatted like !bpTax user, 100")

            # finding and updating the appropriate points
            else:
                ctx.message.content = ctx.message.content.replace("!bpTax ", "")
                ctx.message.content = ctx.message.content.split(", ")

                # no negative numbers
                if int(ctx.message.content[1]) < 0:
                    await ctx.send("[bot] nice try")

                # seeing if user exists
                elif await getBroadcasterId(ctx.message.content[0]):
                    async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
                        async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.message.content[0]),)) as cursor:
                            result = await cursor.fetchone()

                        # if user in database
                        if result:
                            await db.execute("UPDATE economy SET points=? WHERE id=?", (result[2] - int(ctx.message.content[1]), await getBroadcasterId(ctx.message.content[0])))
                            await db.commit()
                            await ctx.send("[bot] took from " + ctx.message.content[0] + " " + ctx.message.content[1] + " basement pesos")

    # lists commands available for purchase
    @commands.command()
    async def bpShop(self, ctx: commands.Context):
        await ctx.send("[bot] !shoot (1000), !shootSnack (800), !swapSnack (150), !healSnack (500)")

    # times out user
    @commands.command()
    async def shoot(self, ctx: commands.Context):
        duration = random.randint(10, 60)
        finalId = ""

        # thread to wait to remod a mod after timing them out
        async def remod(id, duration):
            await asyncio.sleep(duration)

            modIds = []
            while str(id) not in modIds:
                connected = False
                while not connected:

                    try:
                        async with aiohttp.ClientSession(headers = {"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as session:
                            async with session.get("https://api.twitch.tv/helix/users") as response:
                                rateLimit = response.headers.get("Ratelimit-Remaining")
                                if rateLimit != "0":
                                    await session.post("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&user_id=" + id)
                                    async with session.get("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + await getBroadcasterId(yourChannelName)) as response:
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
                    async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                        rateLimit = response.headers.get("Ratelimit-Remaining")
                        if rateLimit != "0":
                            async with session.get("https://api.twitch.tv/helix/moderation/moderators?broadcaster_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID}) as response:
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
            async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
                async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                    result = await cursor.fetchone()

                # check if user has the money
                if result[2] < 1000 and ctx.author.name not in whiteListers:
                    await ctx.send("[bot] not enough basement pesos")
                else:
                    if ctx.author.name not in whiteListers:
                        await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 1000), await getBroadcasterId(ctx.author.name)))
                        await db.commit()

                    connected = False
                    while not connected:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                                    rateLimit = response.headers.get("Ratelimit-Remaining")
                                    if rateLimit != "0":
                                        async with session.get("https://api.twitch.tv/helix/chat/chatters?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&moderator_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " +accessToken, "Client-Id": clientID}) as response:
                                            chatters_data = await response.json()
                                            connected = True
                        except:
                            await asyncio.sleep(5)

                    names = [[element.get("user_id"), element.get("user_name")] for element in chatters_data.get("data")]
                    user = names[random.randint(0, len(names) - 1)]

                    # getting item and action
                    async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
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

                    connected = False
                    while not connected:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                                    rateLimit = response.headers.get("Ratelimit-Remaining")
                                    if rateLimit != "0":
                                        async with session.post("https://api.twitch.tv/helix/moderation/bans?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&moderator_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID, "Content-Type": "application/json"}, json={"data": {"user_id": user[0], "reason": "you got shot", "duration": duration}}) as response:
                                            await ctx.send("[bot] " + ctx.author.name + " " + pastTenseAction + " " + user[1] + " with " + item)
                                            connected = True
                        except:
                            await asyncio.sleep(5)

                        # setting up remod thread if needed
                    if user[0] in modIds:
                        asyncio.create_task(remod(user[0], duration))

        # try to shoot the listed person
        else:
            # finding user id in database
            async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
                cursor = await db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),))
                result = await cursor.fetchone()

                # check if the user has the money
                if result[2] < 1000 and ctx.author.name not in whiteListers:
                    await ctx.send("[bot] not enough basement pesos")
                else:
                    if ctx.author.name not in whiteListers:
                        await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 1000), await getBroadcasterId(ctx.author.name)))
                        await db.commit()

                    dice = random.randint(1, 100)
                    ctx.message.content = (ctx.message.content).replace("!shoot ", "")
                    id = await getBroadcasterId(ctx.message.content)

                    # error handling
                    if id is None:
                        await ctx.send("[bot] couldn't find user")

                    # shooting based on dice
                    else:
                        async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:

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
                            connected = False
                            while not connected:
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                                            rateLimit = response.headers.get("Ratelimit-Remaining")
                                            if rateLimit != "0":
                                                async with session.post("https://api.twitch.tv/helix/moderation/bans?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&moderator_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID, "Content-Type": "application/json"}, json={"data": {"user_id": await getBroadcasterId(ctx.author.name), "reason": "you got shot", "duration": duration}}) as response:
                                                    finalId = await getBroadcasterId(ctx.author.name)
                                                    await ctx.send("[bot] " + ctx.author.name + " missed and " + item + " bounced into their head")
                                                    connected = True
                                except:
                                    await asyncio.sleep(5)

                        # 65% chance to shoot random
                        elif dice > 25:

                            connected = False
                            while not connected:
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                                            rateLimit = response.headers.get("Ratelimit-Remaining")
                                            if rateLimit != "0":
                                                async with session.get("https://api.twitch.tv/helix/chat/chatters?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&moderator_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID}) as response:
                                                    response = await response.json()
                                                    connected = True
                                except:
                                    await asyncio.sleep(5)

                            names = [[element.get("user_id"), element.get("user_name")] for element in response.get("data")]
                            user = names[random.randint(0, len(names) - 1)]

                            connected = False
                            while not connected:
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                                            rateLimit = response.headers.get("Ratelimit-Remaining")
                                            if rateLimit != "0":
                                                async with session.post("https://api.twitch.tv/helix/moderation/bans?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&moderator_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID, "Content-Type": "application/json"}, json={"data": {"user_id": user[0], "reason": "you got shot", "duration": duration}}) as response:
                                                    finalId = user[0]
                                                    await ctx.send("[bot] " + ctx.author.name + " tried to " + presentTenseAction + " " + ctx.message.content + " with " + item + " but they used " + user[1] + " as a shield")
                                                    connected = True
                                except:
                                    await asyncio.sleep(5)

                        # 25% chance to shoot target
                        else:
                            connected = False
                            while not connected:
                                try:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get("https://api.twitch.tv/helix/users", headers={"Client-ID": clientID, "Authorization": "Bearer " + accessToken}) as response:
                                            rateLimit = response.headers.get("Ratelimit-Remaining")
                                            if rateLimit != "0":
                                                async with session.post("https://api.twitch.tv/helix/moderation/bans?broadcaster_id=" + await getBroadcasterId(yourChannelName) + "&moderator_id=" + await getBroadcasterId(yourChannelName), headers={"Authorization": "Bearer " + accessToken, "Client-Id": clientID, "Content-Type": "application/json"}, json={"data": {"user_id": id, "reason": "you got shot", "duration": duration}}) as response:
                                                    finalId = id
                                                    await ctx.send("[bot] " + ctx.author.name + " " + pastTenseAction + " " + ctx.message.content + " with " + item)
                                                    connected = True
                                            else:
                                                await asyncio.sleep(5)
                                except:
                                    await asyncio.sleep(5)

                        if finalId in modIds:
                            asyncio.create_task(remod(finalId, duration))

    # disables input bot for 35 to 95 minutes
    @commands.command()
    async def shootSnack(self, ctx: commands.Context):

        # thread to wait to restart input bot
        async def snackWait():
            await asyncio.sleep(random.randint(2100, 5700))
            chatPlays.snackShot = False
            chatPlays.snackHealed = False
            await updateSnatus()

        # finding user id in database
        async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
            async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                result = await cursor.fetchone()

            # check if user has the money
            if result[2] < 800 and ctx.author.name not in whiteListers:
                await ctx.send("[bot] not enough basement pesos")
            else:
                if ctx.author.name not in whiteListers:
                    await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 800), await getBroadcasterId(ctx.author.name)))
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
    async def healSnack(self, ctx: commands.Context):

        async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
            async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                result = await cursor.fetchone()

            # check if user has the money
            if result[2] < 500 and ctx.author.name not in whiteListers:
                await ctx.send("[bot] not enough basement pesos")
            else:
                if ctx.author.name not in whiteListers:
                    await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 500), await getBroadcasterId(ctx.author.name)))
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
    async def swapSnack(self, ctx: commands.Context):

        # finding user id in database
        async with aiosqlite.connect(os.path.abspath(os.path.join(directory, "chatData.db"))) as db:
            async with db.execute("SELECT * FROM economy WHERE id=?", (await getBroadcasterId(ctx.author.name),)) as cursor:
                result = await cursor.fetchone()

            # check if the user has enough money
            if result[2] < 150 and ctx.author.name not in whiteListers:
                await ctx.send("[bot] not enough basement pesos")
            else:
                if ctx.author.name not in whiteListers:
                    await db.execute("UPDATE economy SET points=? WHERE id=?", ((result[2] - 150), await getBroadcasterId(ctx.author.name)))
                    await db.commit()

                chatPlays.currentSnack = snacks[random.randint(0, len(snacks) - 1)]
                await ctx.send("[bot] " + chatPlays.currentSnack + " snack was swapped in")
                if not chatPlays.idleBotStatus:
                    await updateSnatus()

    # as soon as bot is logged in constantly check the array and update watch time and points
    async def updateWatchTime(self):
        global chatters
        global live
        global firstRedeemed

        while True:
            await asyncio.sleep(10)

            # when channel goes live reset uptime and !first
            if await isLive(yourChannelName):
                if not live:
                    for element in chatters:
                        element[1] = time.time()
                        element[2] = time.time()
                    live = True
                    firstRedeemed = False

                # update database for all users in chat
                for chatter in chatters:
                    async with aiosqlite.connect(os.path.abspath((os.path.join(directory, "chatData.db")))) as db:
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