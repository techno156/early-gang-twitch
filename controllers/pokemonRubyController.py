# imports
import time
import random
import asyncio
from libraries import chatPlays
timeSinceLastMessage = time.time()

# Move definitions

# Move dictionary
#We want to centralise our controls for easy configuration later
controls = { 
    "up": "W",
    "down": "S",
    "left": "A",
    "right": "D",
    "a": "L", #A crew taking Ls (LUL|D:) [choose appropriate reaction as desired]
    "b": "K",
    "start": "U",
    "select": "P"
}

# Get the keycodes for the corresponding controls. Set them up in a dict, because we have to use them later anyway, and they shouldn't change
controlKeyCodes = { 
    "up": chatPlays.keyCodes.get(controls["up"]), #Fetch the keys from the control dictionary (above)
    "down": chatPlays.keyCodes.get(controls["down"]),
    "left": chatPlays.keyCodes.get(controls["left"]),
    "right": chatPlays.keyCodes.get(controls["right"]),
    "a": chatPlays.keyCodes.get(controls["a"]), 
    "b": chatPlays.keyCodes.get(controls["b"]),
    "start": chatPlays.keyCodes.get(controls["start"]),
    "select": chatPlays.keyCodes.get(controls["select"])
}

pressedKeys = { # Keep a record of what key is being pressed
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "a": False,
    "b": False,
    "start": False,
    "select": False
}
####

# Press, Mash and Hold Master Commands
## It's easier if we just have the few functions that handle the basic... functions
async def press(buttonTime, key): #Command to press the given amount of time. Holding just means we press for longer
    pressedKeys[key] = True
    await chatPlays.holdAndReleaseKey(controlKeyCodes[key], buttonTime)
    pressedKeys[key] = False

async def mash(pressTime, key): #Command to mash the given keys for the amount of time
    maxMashTime = 2 #Set up the maximum amount of time that Twitch chat can have a control be mashed for
    pressInterval = 0.3 #how long between presses
    for i in range(0, maxMashTime, pressTime + pressInterval): #Mash timer loop
        await press(pressTime, controlKeyCodes[key])
        await asyncio.sleep(pressInterval) #Take a break and release the key

# Wander command
## Set up the commands for wandering about
async def wander(holdTime, direction=None, moveCount=4): #Default of 4 random moves per wander, as set in old code
    for i in range(moveCount): #Repeat for the number of given moves
        if not direction: #No direction defined, so we're wandering in random directions
            allowedMovements = ("up", "down", "left", "right") #Set what directions we're allowed to move ahead of time
            #dice = random.randint(0, len(allowedMovements)) #Pick a direction. Python indexing starts at 0. Set random to the number of movements we're allowed
            #await press(allowedMovements[dice], holdTime) 
            await press(holdTime, random.choice(allowedMovements)) #Turns out that we can just use python's random to pick the move for us
        else: #We're wandering in some vague direction        
            allowedMovements = allowedUD = ("left", "right") #Default wandering directions for moving up/down. We do have to pick one or the other
            if direction in ("left", "right"):
                allowedMovements = ("up", "down") #If it's one of the other ones, then we switch the allowed movements up
            dice = random.randint(1, 10)
            if (dice <= 4): #Move in the desired direction 40% of the time
                await press(holdTime, direction)
            else:
                await press(holdTime, random.choice(allowedMovements)) #Move in one of the other two directions instead

# Stop movements
## Stop moving, darn you! 
async def stop(): 
    activeKeys = [key for key, value in pressedKeys if value is True] # Get the keys that are currently being pressed. It's easier to pressing every possible combination
    for key in activeKeys:
        await chatPlays.releaseKey(controlKeyCodes[key]) #Release the relevant key

# Old Move Definitions
async def a(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("L"), pressTime)

async def holdA(holdTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("L"), holdTime)

async def mashA(pressTime):
    mashTime = 0
    while mashTime <= 2:
        await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("L"), pressTime)
        mashTime += pressTime + .3
        await asyncio.sleep(.3)

async def b(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("K"), pressTime)

async def holdB():
    await chatPlays.holdKey(chatPlays.keyCodes.get("K"))

async def mashB(pressTime):
    mashTime = 0
    while mashTime <= 2:
        await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("K"), pressTime)
        mashTime += pressTime + .3
        await asyncio.sleep(.3)

async def select(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("P"), pressTime)

async def start(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("U"), pressTime)

async def wander(times, holdTime):
    for i in range(times):
        dice = random.randint(1, 4)
        match dice:
            case 1:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
            case 2:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)
            case 3:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)
            case 4:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)

async def upWander(holdTime):
    for i in range(4):
        dice = random.randint(1, 10)
        if dice == 1 or dice == 2 or dice == 3 or dice == 4:
            await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
        else:
            dice = random.randint(1, 2)
            if dice == 1:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
            else:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)

async def downWander(holdTime):
    for i in range(4):
        dice = random.randint(1, 10)
        if dice == 1 or dice == 2 or dice == 3 or dice == 4:
            await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)
        else:
            dice = random.randint(1, 2)
            if dice == 1:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
            else:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)

async def leftWander(holdTime):
    for i in range(4):
        dice = random.randint(1, 10)
        if dice == 1 or dice == 2 or dice == 3 or dice == 4:
            await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)
        else:
            dice = random.randint(1, 2)
            if dice == 1:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
            else:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)

async def rightWander(holdTime):
    for i in range(4):
        dice = random.randint(1, 10)
        if dice == 1 or dice == 2 or dice == 3 or dice == 4:
            await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
        else:
            dice = random.randint(1, 2)
            if dice == 1:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
            else:
                await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)

async def holdUp(holdTime):
    dice = random.randint(1, 100)
    if dice == 1:
        for i in range(8):
            dice = random.randint(1, 4)
            match dice:
                case 1:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
                case 2:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)
                case 3:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)
                case 4:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
    else:
        await chatPlays.releaseKey(chatPlays.keyCodes.get("S"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("A"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("D"))
        await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)

async def holdDown(holdTime):
    dice = random.randint(1, 100)
    if dice == 1:
        for i in range(8):
            dice = random.randint(1, 4)
            match dice:
                case 1:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
                case 2:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)
                case 3:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)
                case 4:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
    else:
        await chatPlays.releaseKey(chatPlays.keyCodes.get("W"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("A"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("D"))
        await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)

async def holdLeft(holdTime):
    dice = random.randint(1, 100)
    if dice == 1:
        for i in range(8):
            dice = random.randint(1, 4)
            match dice:
                case 1:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
                case 2:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)
                case 3:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)
                case 4:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
    else:
        await chatPlays.releaseKey(chatPlays.keyCodes.get("D"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("S"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("W"))
        await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)

async def holdRight(holdTime):
    dice = random.randint(1, 100)
    if dice == 1:
        for i in range(8):
            dice = random.randint(1, 4)
            match dice:
                case 1:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)
                case 2:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)
                case 3:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)
                case 4:
                    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)
    else:
        await chatPlays.releaseKey(chatPlays.keyCodes.get("A"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("W"))
        await chatPlays.releaseKey(chatPlays.keyCodes.get("S"))
        await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)

async def slightUp(lightPressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), lightPressTime)

async def slightDown(lightPressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), lightPressTime)

async def slightLeft(lightPressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), lightPressTime)

async def slightRight(lightPressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), lightPressTime)

async def up(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), pressTime)

async def down(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), pressTime)

async def left(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), pressTime)

async def right(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), pressTime)

async def stop():
    await chatPlays.releaseKey(chatPlays.keyCodes.get("K"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("V"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("Q"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("E"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("L"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("I"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("O"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("T"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("G"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("W"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("A"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("S"))
    await chatPlays.releaseKey(chatPlays.keyCodes.get("D"))

# Bot controls

# makes inputs when no one has typed in chat for a while
async def idleBot():

    # checks if idle bot is supposed to be on and if no one has chatted
    while chatPlays.idleBotPlaying:
        if timeSinceLastMessage <= (time.time() - 5 * 60):
            botPressTime = (random.randint(1, 12) / 10)
            botHoldTime = (random.randint(1, 100) / 10)

            # tell obs to show idle bot is active
            if not chatPlays.idleBotStatus:
                chatPlays.idleBotStatus = True
                await chatPlays.updateSnatus()

            # time between inputs
            await asyncio.sleep(random.randint(1, 10) / 10)

            # 25% chance of non directionals
            dice = random.randint(1, 4)
            if dice == 1:
                allowedKeys = ("a", "b", "select", "start") # Create a tuple of non-directional keys to press
                await press(botPressTime, random.choice(allowedKeys)) #Randomly choose one and press it
            # 75% chance of directionals
            else:
                dice = random.randint(1, 5)
                if (dice == 5): #20% chance of hold-wandering, otherwise, go for a normal wander
                    await wander(botHoldTime)
                else:
                    await wander(botPressTime, moveCount=1) #choose one random directional move, and go that way for a little bit

        # tell obs idle bot is inactive
        else:
            if chatPlays.idleBotStatus:
                chatPlays.idleBotStatus = False
                await chatPlays.updateSnatus()
            await asyncio.sleep(5)

# makes inputs every so often
async def inputBot():
    # Set up the bot movement function
    ## Most of the bots use the same movement coed, so we can just tie it back to the one function for ease of use/changing later.
    async def botMoves(botPressTime, botHoldTime):
        botChoice = random.randint(1,17) #Choose whether we move directionally, non-directionally, or wander.
        coin = bool(random.getrandbits(1)) #Flip a coin. Randomly get a single bit, and squish into boolean, since this is faster. Set within scope, since we're only running one of these, it's fine.
        buttonTime =  botPressTime if coin is True else botHoldTime #default to a press, or else we hold
        match botChoice: #Match the move probabilities of the original code
            case i if botChoice <=8: #we're moving directionally
                await wander(buttonTime, moveCount=1) #Move in a single random direction
            case i if botChoice in range(9, 16): #We're not pushing directional buttons this time
                allowedButtons = ("a", "b", "start", "select") #No directions allowed
                nextMove = random.choice(allowedButtons)
                if nextMove in ("a", "b"): #We're only allowed to hold down A and B 
                    await press(buttonTime, nextMove) #We've already set whether to hold or press, now we just choose a button and go
                else:
                    await press(botPressTime, nextMove)
            case _: #We're not doing directions, so time for a long wander in 2 dirctions
                await wander(botHoldTime, moveCount=2) #change botHoldTime to buttonTime if we want to randomise the wander length

    # checks if conditions are right
    while chatPlays.inputBotPlaying:
        if not chatPlays.snackShot or chatPlays.snackHealed:
            botPressTime = (random.randint(1, 12) / 10)
            botHoldTime = (random.randint(1, 100) / 10)
            lightPressTime = (random.randint(1, 3) / 400)

            # sleepy snack controls
            if chatPlays.currentSnack == "sleepy":

                # time between inputs
                await asyncio.sleep(random.randint(60, 720))

                # 5% chance of no action
                dice = random.randint(1, 100)
                if dice < 96:
                    await botMoves(botPressTime, botHoldTime)

            # chris snack controls
            elif chatPlays.currentSnack == "chris":

                # time between inputs
                await asyncio.sleep(random.randint(10, 120))

                # 33% chance of no action
                dice = random.randint(1, 3)
                if dice != 1:
                    await botMoves(botPressTime, botHoldTime)

            # burst snack controls
            elif chatPlays.currentSnack == "burst":

                # time between inputs
                await asyncio.sleep(random.randint(300, 900))

                # 10% chance of no action
                dice = random.randint(1, 10)
                if dice != 1:
                    for i in range(5):
                        await botMoves(botPressTime, botHoldTime)

            # silly snack controls
            elif chatPlays.currentSnack == "silly":

                # time between inputs
                await asyncio.sleep(random.randint(10, 80))

                # 33% chance of no action
                dice = random.randint(1, 3)
                if dice != 1:
                    dice = random.randint(1, 9)
                    if dice < 9: #Keep original probabilities for movement. We should move 8 of 9 times.
                        coin = bool(random.getrandbits(1)) #Flip a coin for move, or wander
                        if coin: #if coin is true, we move
                            buttonTime = botPressTime if bool(random.getrandbits(1)) is True else botHoldTime #Flip coin to decide whether to press or hold
                            await wander(buttonTime, moveCount=1) # Pick a random direction, and go that way
                    else:
                        await wander(botHoldTime, moveCount=2) 

            # cautious snack controls
            elif chatPlays.currentSnack == "cautious":

                # time between inputs
                await asyncio.sleep(random.randint(10, 120))

                # 20% chance of no action
                dice = random.randint(1, 5)
                if dice != 1:
                    dice = random.randint(1, 6) #Rare time that the dice is actually a 6-sided die 
                    if dice <= 4:
                        await wander(lightPressTime, moveCount=1) #We're moving, but only slightly
                    else: 
                        coin = bool(random.getrandbits(1)) #Flip a coin for move or b 
                        if coin:
                            await press(botPressTime, "b")
                        else:
                            await mash(botPressTime, "b")

            # sonic snack controls
            elif chatPlays.currentSnack == "sonic":

                # time between inputs
                await asyncio.sleep(random.randint(20, 60))

                # 10% chance of no action
                dice = random.randint(1, 10)
                if dice != 1:
                    dice = random.randint(1, 11)
                    match dice:
                        case i if dice in range(1, 8): #If we're in here, we're moving, one way or the other 
                            coin = bool(random.getrandbits(1)) #Flip a coin on whether it's a wandering in a given direction, or a slight movement
                            if coin: #We're wandering in a direction
                                allowedMovements = ("up", "down", "left", "right") #Set the directions for wandering
                                await wander(botHoldTime, random.choice(allowedMovements)) #Wander in that direction
                            else: # Only slight movements, please
                                await wander(lightPressTime, moveCount=1)
                        case 9: 
                            await mash(botPressTime, "a")
                        case 10: 
                            await mash(botPressTime, "b")
                        case _:
                            await wander(botHoldTime)
        else:
            await asyncio.sleep(5)

# chat controls
async def controller(message):

    # makes sure chat is playing
    if chatPlays.chatPlaying is True:
        global timeSinceLastMessage
        timeSinceLastMessage = time.time()

        # setting up variables
        pressTime = (random.randint(1, 3) / 10)
        lightPressTime = (random.randint(1, 3) / 400)
        holdTime = random.randint(5, 10)
        message = message.lower()

        # making inputs
        if message == "a":
            await a(pressTime)
        elif "hold a" in message:
            await holdA(holdTime)
        elif "mash a" in message:
            await mashA(pressTime)
        elif message == "b":
            await b(pressTime)
        elif "hold b" in message:
            await holdB()
        elif "mash b" in message:
            await mashB(pressTime)
        elif "select" in message:
            await select(pressTime)
        elif "start" in message:
            await start(pressTime)
        elif "up wander" in message:
            await upWander(holdTime)
        elif "down wander" in message:
            await downWander(holdTime)
        elif "left wander" in message:
            await leftWander(holdTime)
        elif "right wander" in message:
            await rightWander(holdTime)
        elif "wander" in message:
            await wander(4, holdTime)
        elif "hold up" in message:
            await holdUp(holdTime)
        elif "hold down" in message:
            await holdDown(holdTime)
        elif "hold left" in message:
            await holdLeft(holdTime)
        elif "hold right" in message:
            await holdRight(holdTime)
        elif "slup" in message:
            await slightUp(lightPressTime)
        elif "slown" in message:
            await slightDown(lightPressTime)
        elif "sleft" in message:
            await slightLeft(lightPressTime)
        elif "slight" in message:
            await slightRight(lightPressTime)
        elif "up" in message:
            await up(pressTime)
        elif "down" in message:
            await down(pressTime)
        elif "left" in message:
            await left(pressTime)
        elif "right" in message:
            await right(pressTime)
        elif "stop" in message:
            await stop()

