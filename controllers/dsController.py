# imports
import random
import time
import asyncio
from controllers import gbaController
from libraries import chatPlays
timeSinceLastMessage = time.time()

# makes inputs when no one has typed in chat for a while
async def idleBot():
    
    # checks if idle bot is supposed to be on and if no one has chatted
    while chatPlays.idleBotPlaying:
        global timeSinceLastMessage
        timeSinceLastMessage = time.time()
        
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
                if dice == 1:
                    dice = random.randint(1, 6)
                    match dice:
                        case 1:
                            await gbaController.a(botPressTime)
                        case 2:
                            await gbaController.b(botPressTime)
                        case 3:
                            await x(botPressTime)
                        case 4:
                            await y(botPressTime)
                        case 5:
                            await l(botPressTime)
                        case 6:
                            await r(botPressTime)

            # 75% chance of directionals
            else:
                dice = random.randint(1, 5)
                match dice:
                    case 1:
                        await gbaController.up(botPressTime)
                    case 2:
                        await gbaController.down(botPressTime)
                    case 3:
                        await gbaController.left(botPressTime)
                    case 4:
                        await gbaController.right(botPressTime)
                    case 5:
                        await gbaController.wander(4, botHoldTime)
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
                            await gbaController.up(botPressTime)
                        case 2:
                            await gbaController.down(botPressTime)
                        case 3:
                            await gbaController.left(botPressTime)
                        case 4:
                            await gbaController.right(botPressTime)
                        case 5:
                            await gbaController.holdUp(botHoldTime)
                        case 6:
                            await gbaController.holdDown(botHoldTime)
                        case 7:
                            await gbaController.holdLeft(botHoldTime)
                        case 8:
                            await gbaController.holdDown(botHoldTime)
                        case 9:
                            await gbaController.a(botPressTime)
                        case 10:
                            await gbaController.holdA(botHoldTime)
                        case 11:
                            await gbaController.b(botPressTime)
                        case 12:
                            await gbaController.holdB()
                        case 13:
                            await x(botPressTime)
                        case 14:
                            await y(botPressTime)
                        case 15:
                            await l(botPressTime)
                        case 16:
                            await r(botPressTime)
                        case 17:
                            await gbaController.wander(2, botHoldTime)

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
                            await gbaController.up(botPressTime)
                        case 2:
                            await gbaController.down(botPressTime)
                        case 3:
                            await gbaController.left(botPressTime)
                        case 4:
                            await gbaController.right(botPressTime)
                        case 5:
                            await gbaController.holdUp(botHoldTime)
                        case 6:
                            await gbaController.holdDown(botHoldTime)
                        case 7:
                            await gbaController.holdLeft(botHoldTime)
                        case 8:
                            await gbaController.holdDown(botHoldTime)
                        case 9:
                            await gbaController.a(botPressTime)
                        case 10:
                            await gbaController.holdA(botHoldTime)
                        case 11:
                            await gbaController.b(botPressTime)
                        case 12:
                            await gbaController.holdB()
                        case 13:
                            await x(botPressTime)
                        case 14:
                            await y(botPressTime)
                        case 15:
                            await l(botPressTime)
                        case 16:
                            await r(botPressTime)
                        case 17:
                            await gbaController.wander(2, botHoldTime)
                        
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
                                await gbaController.up(botPressTime)
                            case 2:
                                await gbaController.down(botPressTime)
                            case 3:
                                await gbaController.left(botPressTime)
                            case 4:
                                await gbaController.right(botPressTime)
                            case 5:
                                await gbaController.holdUp(botHoldTime)
                            case 6:
                                await gbaController.holdDown(botHoldTime)
                            case 7:
                                await gbaController.holdLeft(botHoldTime)
                            case 8:
                                await gbaController.holdDown(botHoldTime)
                            case 9:
                                await gbaController.a(botPressTime)
                            case 10:
                                await gbaController.holdA(botHoldTime)
                            case 11:
                                await gbaController.b(botPressTime)
                            case 12:
                                await gbaController.holdB()
                            case 13:
                                await x(botPressTime)
                            case 14:
                                await y(botPressTime)
                            case 15:
                                await l(botPressTime)
                            case 16:
                                await r(botPressTime)
                            case 17:
                                await gbaController.wander(2, botHoldTime)

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
                            await gbaController.up(botPressTime)
                        case 2:
                            await gbaController.down(botPressTime)
                        case 3:
                            await gbaController.left(botPressTime)
                        case 4:
                            await gbaController.right(botPressTime)
                        case 5:
                            await gbaController.holdUp(botHoldTime)
                        case 6:
                            await gbaController.holdDown(botHoldTime)
                        case 7:
                            await gbaController.holdLeft(botHoldTime)
                        case 8:
                            await gbaController.holdDown(botHoldTime)
                        case 9:
                            await gbaController.wander(2, botHoldTime)
            
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
                            await gbaController.slightUp(lightPressTime)
                        case 2:
                            await gbaController.slightDown(lightPressTime)
                        case 3:
                            await gbaController.slightRight(lightPressTime)
                        case 4:
                            await gbaController.slightLeft(lightPressTime)
                        case 5:
                            await gbaController.b(botPressTime)
                        case 6:
                            await gbaController.mashB(botPressTime)

            # sonic snack controls
            elif chatPlays.currentSnack == "sonic":

                # time between inputs
                await asyncio.sleep(random.randint(20, 60))

                # 10% chance of no action
                dice = random.randint(1, 10)
                if dice != 1:
                    dice = random.randint(1, 6)
                    match dice:
                        case 1:
                            await gbaController.slightRight(lightPressTime)
                        case 2:
                            await gbaController.slightLeft(lightPressTime)
                        case 3:
                            await gbaController.slightUp(lightPressTime)
                        case 4:
                            await gbaController.slightDown(lightPressTime)
                        case 5:
                            await gbaController.mashA(botPressTime)
                        case 6:
                            await gbaController.mashB(botPressTime)
                        case 7:
                            await gbaController.wander(4, botHoldTime)
                        case 8:
                            await gbaController.upWander(botHoldTime)
                        case 9:
                            await gbaController.downWander(botHoldTime)
                        case 10:
                            await gbaController.leftWander(botHoldTime)
                        case 11:
                            await gbaController.rightWander(botHoldTime)
        else:
            await asyncio.sleep(5)

# chat controls
async def controller(message):

    # makes sure chat is playing
    if chatPlays.chatPlaying is True:

        # setting up variables
        pressTime = (random.randint(1, 3) / 10)
        lightPressTime = (random.randint(1, 3) / 400)
        holdTime = random.randint(5, 10)
        slightlyDifferentHoldTimeForWhateverFuckingReason = (random.randint(9, 15) / 10)
        message = message.lower()
        dice = random.randint(1, 40)

        # 2.5% chance of random input
        if dice == 1 and (message == "a" or "shoot" in message or "left+" in message or "right+" in message or "down+" in message or "up+" in message or "hold a" in message or "mash a" in message or message == "b" or "hold b" in message or "mash b" in message or message == "x" or message == "y" or "select" in message or "start" in message or message == "l" or message == "r" or "up wander" in message or "down wander" in message or "left wander" in message or "right wander" in message or "wander" in message or "hold up" in message or "hold down" in message or "hold left" in message or "hold right" in message or "slup" in message or "slown" in message or "sleft" in message or "slight" in message or "up" in message or "down" in message or "left" in message or "right" in message or "stop" in message):
            dice = random.randint(1, 34)
            match dice:
                case 1:
                    await gbaController.up(pressTime)
                case 2:
                    await gbaController.down(pressTime)
                case 3:
                    await gbaController.left(pressTime)
                case 4:
                    await gbaController.right(pressTime)
                case 5:
                    await gbaController.holdUp(holdTime)
                case 6:
                    await gbaController.holdDown(holdTime)
                case 7:
                    await gbaController.holdLeft(holdTime)
                case 8:
                    await gbaController.holdRight(holdTime)
                case 9:
                    await gbaController.a(pressTime)
                case 10:
                    await gbaController.holdA(holdTime)
                case 11:
                    await gbaController.mashA(pressTime)
                case 12:
                    await gbaController.b(pressTime)
                case 13:
                    await gbaController.holdB()
                case 14:
                    await gbaController.mashB(pressTime)
                case 15:
                    await x(pressTime)
                case 16:
                    await y(pressTime)
                case 17:
                    await gbaController.select(pressTime)
                case 18:
                    await gbaController.start(pressTime)
                case 19:
                    await l(pressTime)
                case 20:
                    await r(pressTime)
                case 21:
                    await gbaController.stop()
                case 22:
                    await gbaController.wander(4, holdTime)
                case 23:
                    await gbaController.slightDown(lightPressTime)
                case 24:
                    await gbaController.slightUp(lightPressTime)
                case 25:
                    await gbaController.slightLeft(lightPressTime)
                case 26:
                    await gbaController.slightRight(lightPressTime)
                case 27:
                    await gbaController.upWander(holdTime)
                case 28:
                    await gbaController.downWander(holdTime)
                case 29:
                    await gbaController.leftWander(holdTime)
                case 30:
                    await gbaController.rightWander(holdTime)
                case 31:
                    await leftPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
                case 32:
                    await rightPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
                case 33:
                    await upPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
                case 34:
                    await downPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
        # 2.5% chance of opposite input
        elif dice == 2:
            if message == "a" or "shoot" in message:
                await gbaController.b(pressTime)
            elif "hold a" in message:
                await gbaController.holdB()
            elif "mash a" in message:
                await gbaController.mashB(pressTime)
            elif message == "b":
                await gbaController.a(pressTime)
            elif "hold b" in message:
                await gbaController.holdA(holdTime)
            elif "mash b" in message:
                await gbaController.mashA(pressTime)
            elif message == "x":
                await y(pressTime)
            elif message == "y":
                await x(pressTime)
            elif "select" in message:
                await gbaController.start(pressTime)
            elif "start" in message:
                await gbaController.select(pressTime)
            elif message == "l":
                await r(pressTime)
            elif message == "r":
                await l(pressTime)
            elif "up wander" in message:
                await gbaController.downWander(holdTime)
            elif "down wander" in message:
                await gbaController.upWander(holdTime)
            elif "left wander" in message:
                await gbaController.rightWander(holdTime)
            elif "right wander" in message:
                await gbaController.leftWander(holdTime)
            elif "wander" in message:
                await gbaController.stop()
            elif "hold up" in message:
                await gbaController.holdDown(holdTime)
            elif "hold down" in message:
                await gbaController.holdUp(holdTime)
            elif "hold left" in message:
                await gbaController.holdRight(holdTime)
            elif "hold right" in message:
                await gbaController.holdLeft(holdTime)
            elif "slup" in message:
                await gbaController.slightDown(lightPressTime)
            elif "slown" in message:
                await gbaController.slightUp(lightPressTime)
            elif "sleft" in message:
                await gbaController.slightRight(lightPressTime)
            elif "slight" in message:
                await gbaController.slightLeft(lightPressTime)
            elif "up+" in message:
                await downPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "down+" in message:
                await upPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "left+" in message:
                await rightPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "right+" in message:
                await leftPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "up" in message:
                await gbaController.down(pressTime)
            elif "down" in message:
                await gbaController.up(pressTime)
            elif "left" in message:
                await gbaController.right(pressTime)
            elif "right" in message:
                await gbaController.left(pressTime)
            elif "stop" in message:
                await gbaController.upWander(holdTime)
                await gbaController.downWander(holdTime)
                await gbaController.leftWander(holdTime)
                await gbaController.rightWander(holdTime)

        # 95% chance of correct inputs
        else:
            if message == "a" or "shoot" in message:
                await gbaController. a(pressTime)
            elif "hold a" in message:
                await gbaController.holdA(holdTime)
            elif "mash a" in message:
                await gbaController.mashA(pressTime)
            elif message == "b":
                await gbaController.b(pressTime)
            elif "hold b" in message:
                await gbaController.holdB()
            elif "mash b" in message:
                await gbaController.mashB(pressTime)
            elif message == "x":
                await x(pressTime)
            elif message == "y":
                await y(pressTime)
            elif "select" in message:
                await gbaController.select(pressTime)
            elif "start" in message:
                await gbaController.start(pressTime)
            elif message == "l":
                await l(pressTime)
            elif message == "r":
                await r(pressTime)
            elif "up wander" in message:
                await gbaController.upWander(holdTime)
            elif "down wander" in message:
                await gbaController.downWander(holdTime)
            elif "left wander" in message:
                await gbaController.leftWander(holdTime)
            elif "right wander" in message:
                await gbaController.rightWander(holdTime)
            elif "wander" in message:
                await gbaController.wander(4, holdTime)
            elif "hold up" in message:
                await gbaController.holdUp(holdTime)
            elif "hold down" in message:
                await gbaController.holdDown(holdTime)
            elif "hold left" in message:
                await gbaController.holdLeft(holdTime)
            elif "hold right" in message:
                await gbaController.holdRight(holdTime)
            elif "slup" in message:
                await gbaController.slightUp(lightPressTime)
            elif "slown" in message:
                await gbaController.slightDown(lightPressTime)
            elif "sleft" in message:
                await gbaController.slightLeft(lightPressTime)
            elif "slight" in message:
                await gbaController.slightRight(lightPressTime)
            elif "up+" in message:
                await upPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "down+" in message:
                await downPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "left+" in message:
                await leftPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "right+" in message:
                await rightPlus(slightlyDifferentHoldTimeForWhateverFuckingReason)
            elif "up" in message:
                await gbaController.up(pressTime)
            elif "down" in message:
                await gbaController.down(pressTime)
            elif "left" in message:
                await gbaController.left(pressTime)
            elif "right" in message:
                await gbaController.right(pressTime)
            elif "stop" in message:
                await gbaController.stop()

# define controls down here
async def x(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("O"), pressTime)

async def y(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("V"), pressTime)

async def l(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("Q"), pressTime)

async def r(pressTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("E"), pressTime)

async def leftPlus(holdTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("A"), holdTime)

async def rightPlus(holdTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("D"), holdTime)

async def upPlus(holdTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("W"), holdTime)

async def downPlus(holdTime):
    await chatPlays.holdAndReleaseKey(chatPlays.keyCodes.get("S"), holdTime)