# imports
import time
import random
import asyncio
from libraries import chatPlays
timeSinceLastMessage = time.time()

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
                dice = random.randint(1, 4)
                match dice:
                    case 1:
                        await a(botPressTime)
                    case 2:
                        await b(botPressTime)
                    case 3:
                        await select(botPressTime)
                    case 4:
                        await start(botPressTime)

            # 75% chance of directionals
            else:
                dice = random.randint(1, 5)
                match dice:
                    case 1:
                        await up(botPressTime)
                    case 2:
                        await down(botPressTime)
                    case 3:
                        await left(botPressTime)
                    case 4:
                        await right(botPressTime)
                    case 5:
                        await wander(4, botHoldTime)

        # tell obs idle bot is inactive
        else:
            if chatPlays.idleBotStatus:
                chatPlays.idleBotStatus = False
                await chatPlays.updateSnatus()
            await asyncio.sleep(5)

# makes inputs every so often
async def inputBot():

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
                    dice = random.randint(1, 17)
                    match dice:
                        case 1:
                            await up(botPressTime)
                        case 2:
                            await down(botPressTime)
                        case 3:
                            await left(botPressTime)
                        case 4:
                            await right(botPressTime)
                        case 5:
                            await holdUp(botHoldTime)
                        case 6:
                            await holdDown(botHoldTime)
                        case 7:
                            await holdLeft(botHoldTime)
                        case 8:
                            await holdDown(botHoldTime)
                        case 9:
                            await a(botPressTime)
                        case 10:
                            await holdA(botHoldTime)
                        case 11:
                            await b(botPressTime)
                        case 12:
                            await holdB()
                        case 15:
                            await select(botPressTime)
                        case 16:
                            await start(botPressTime)
                        case 17:
                            await wander(2, botHoldTime)

            # chris snack controls
            elif chatPlays.currentSnack == "chris":

                # time between inputs
                await asyncio.sleep(random.randint(10, 120))

                # 33% chance of no action
                dice = random.randint(1, 3)
                if dice != 1:
                    dice = random.randint(1, 17)
                    match dice:
                        case 1:
                            await up(botPressTime)
                        case 2:
                            await down(botPressTime)
                        case 3:
                            await left(botPressTime)
                        case 4:
                            await right(botPressTime)
                        case 5:
                            await holdUp(botHoldTime)
                        case 6:
                            await holdDown(botHoldTime)
                        case 7:
                            await holdLeft(botHoldTime)
                        case 8:
                            await holdDown(botHoldTime)
                        case 9:
                            await a(botPressTime)
                        case 10:
                            await holdA(botHoldTime)
                        case 11:
                            await b(botPressTime)
                        case 12:
                            await holdB()
                        case 15:
                            await select(botPressTime)
                        case 16:
                            await start(botPressTime)
                        case 17:
                            await wander(2, botHoldTime)

            # burst snack controls
            elif chatPlays.currentSnack == "burst":

                # time between inputs
                await asyncio.sleep(random.randint(300, 900))

                # 10% chance of no action
                dice = random.randint(1, 10)
                if dice != 1:
                    for i in range(5):
                        dice = random.randint(1, 17)
                        match dice:
                            case 1:
                                await up(botPressTime)
                            case 2:
                                await down(botPressTime)
                            case 3:
                                await left(botPressTime)
                            case 4:
                                await right(botPressTime)
                            case 5:
                                await holdUp(botHoldTime)
                            case 6:
                                await holdDown(botHoldTime)
                            case 7:
                                await holdLeft(botHoldTime)
                            case 8:
                                await holdDown(botHoldTime)
                            case 9:
                                await a(botPressTime)
                            case 10:
                                await holdA(botHoldTime)
                            case 11:
                                await b(botPressTime)
                            case 12:
                                await holdB()
                            case 15:
                                await select(botPressTime)
                            case 16:
                                await start(botPressTime)
                            case 17:
                                await wander(2, botHoldTime)

            # silly snack controls
            elif chatPlays.currentSnack == "silly":

                # time between inputs
                await asyncio.sleep(random.randint(10, 80))

                # 33% chance of no action
                dice = random.randint(1, 3)
                if dice != 1:
                    dice = random.randint(1, 9)
                    match dice:
                        case 1:
                            await up(botPressTime)
                        case 2:
                            await down(botPressTime)
                        case 3:
                            await left(botPressTime)
                        case 4:
                            await right(botPressTime)
                        case 5:
                            await holdUp(botHoldTime)
                        case 6:
                            await holdDown(botHoldTime)
                        case 7:
                            await holdLeft(botHoldTime)
                        case 8:
                            await holdDown(botHoldTime)
                        case 9:
                            await wander(2, botHoldTime)

            # cautious snack controls
            elif chatPlays.currentSnack == "cautious":

                # time between inputs
                await asyncio.sleep(random.randint(10, 120))

                # 20% chance of no action
                dice = random.randint(1, 5)
                if dice != 1:
                    dice = random.randint(1, 6)
                    match dice:
                        case 1:
                            await slightUp(lightPressTime)
                        case 2:
                            await slightDown(lightPressTime)
                        case 3:
                            await slightRight(lightPressTime)
                        case 4:
                            await slightLeft(lightPressTime)
                        case 5:
                            await b(botPressTime)
                        case 6:
                            await mashB(botPressTime)

            # sonic snack controls
            elif chatPlays.currentSnack == "sonic":

                # time between inputs
                await asyncio.sleep(random.randint(20, 60))

                # 10% chance of no action
                dice = random.randint(1, 10)
                if dice != 1:
                    dice = random.randint(1, 11)
                    match dice:
                        case 1:
                            await slightUp(lightPressTime)
                        case 2:
                            await slightDown(lightPressTime)
                        case 3:
                            await slightLeft(lightPressTime)
                        case 4:
                            await slightRight(lightPressTime)
                        case 5:
                            await mashA(botPressTime)
                        case 6:
                            await mashB(botPressTime)
                        case 7:
                            await wander(4, botHoldTime)
                        case 8:
                            await upWander(botHoldTime)
                        case 9:
                            await downWander(botHoldTime)
                        case 10:
                            await leftWander(botHoldTime)
                        case 11:
                            await rightWander(botHoldTime)
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

# define controls down here
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