# uses the tilitfy api to speak and display text in obs whenever someone donates

# imports
from obswebsocket import obsws
from obswebsocket import requests as obwsrequests
from libraries.autoStream import *
import os
import pyttsx3
import pyautogui
import configparser
import requests
import aiohttp
import aiofile

# reading config
config = configparser.ConfigParser()
config.read(os.path.abspath((os.path.join(directory, "config.ini"))))
ttsBodyDirectory = config.get("directories", "tts body")
ttsHeaderDirectory = config.get("directories", "tts header")
websocketPassword = config.get("obs", "websocket server password")
clientID = config.get("tiltify", "client id")
clientSecret = config.get("tiltify", "client secret")
code = config.get("tiltify", "code")
refreshToken = config.get("tiltify", "tiltify refresh token")

# setting up variables
ws = obsws("localhost", 4444, websocketPassword)
ttsOn = False
lastDonation = []
screenWidth, screenHeight = pyautogui.size()

# making token and writing to file if needed
if refreshToken == "":
    response = requests.post("https://v5api.tiltify.com/oauth/token", data = {"grant_type": "authorization_code", "client_id": clientID, "client_secret": clientSecret, "redirect_uri": "https://localhost/", "code": code})
    with open(os.path.abspath((os.path.join(directory, "config.ini"))), "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if line.startswith("tiltify refresh token ="):
            lines[i] = "tiltify refresh token = " + response.json().get("refresh_token") + "\n"
            break
    with open(os.path.abspath((os.path.join(directory, "config.ini"))), "w") as file:
        file.writelines(lines)

# finds the scene where the given source name is located
async def getScene(source):
    global ws

    # get scene names
    sceneData = ws.call(obwsrequests.GetSceneList())

    # loop through each scene
    for scene in sceneData.getScenes():
        name = scene.get("name")
        itemData = ws.call(obwsrequests.GetSceneItemList(sceneName = name))

        # loop through all scene items
        for item in itemData.getSceneItems():
            if item.get("sourceName") == source:

                # return the source whose name matches the given one
                return name

# takes donation info and tells obs to display it
async def donationAlert(name, amount, charity, message):

    # prepping engine
    engine = pyttsx3.init()
    rate = engine.getProperty("rate")
    engine.setProperty("rate", rate - 80)

    # format message into lines
    lineLength = len(name + " donated $" + amount + " to " + charity)
    words = message.split()
    text = []

    currentLine = ""
    for word in words:
        if len(currentLine) + len(word) < lineLength:
            if currentLine == "":
                currentLine += word
            else:
                currentLine += " " + word
        else:
            text += [currentLine + "\n"]
            currentLine = ""
    text += currentLine
    formatted_text = ''.join(text)

    # change donation text
    async with aiofile.async_open(os.path.abspath(ttsBodyDirectory), "w") as file:
        await file.write(formatted_text)
    async with aiofile.async_open(os.path.abspath(ttsHeaderDirectory), "w") as file:
        await file.write(name + " donated $" + amount + " to " + charity)

    # give obs time to update text
    await asyncio.sleep(2)

    # tell obs to show sources
    ws.call(obwsrequests.SetSceneItemProperties(sceneName = await getScene("tts body"), item = "tts body", visible = True))
    ws.call(obwsrequests.SetSceneItemProperties(sceneName = await getScene("tts header"), item = "tts header", visible = True))

    # speak message
    engine.say(message)
    engine.runAndWait()

    # tell obs to hide sources
    ws.call(obwsrequests.SetSceneItemProperties(sceneName = await getScene("tts body"), item = "tts body", visible = False))
    ws.call(obwsrequests.SetSceneItemProperties(sceneName = await getScene("tts header"), item ="tts header", visible = False))

# starts taking and displaying tts messages
async def startTTS():
    global ttsOn
    ttsOn = True
    asyncio.create_task(tts())

# stops taking and displaying tts messages
async def stopTTS():
    global ttsOn
    ttsOn = False

# infinite loop that looks for new donations if tts is on
async def tts():
    global ttsOn
    global ws
    global lastDonation
    while ttsOn:
        async with aiohttp.ClientSession() as session:

            # getting user info
            campaign_response = await session.get("https://v5api.tiltify.com/api/public/users/" + (requests.get("https://v5api.tiltify.com/api/public/current-user", headers = {"Authorization": "Bearer " + (requests.post("https://v5api.tiltify.com/oauth/token",data={"client_id": clientID, "client_secret": clientSecret, "grant_type": "refresh_token", "refresh_token": refreshToken}).json().get("access_token"))}).json().get("data").get("id")) + "/campaigns", headers = {"Authorization": "Bearer " + requests.post("https://v5api.tiltify.com/oauth/token",data={"client_id": clientID, "client_secret": clientSecret, "grant_type": "refresh_token", "refresh_token": refreshToken}).json().get("access_token")})
            campaignData = await campaign_response.json()

            # extracting campaigns
            ids = []
            for x in campaignData.get("data"):
                ids.append([x.get("id"), x.get("name")])

            # getting donation from data from each id
            for id in ids:
                connected = False
                while not connected:
                    try:
                        donationResponse = await session.get("https://v5api.tiltify.com/api/public/campaigns/" + str(id[0]) + "/donations", headers = {"Authorization": "Bearer " + requests.post("https://v5api.tiltify.com/oauth/token", data={"client_id": clientID, "client_secret": clientSecret, "grant_type": "refresh_token", "refresh_token": refreshToken}).json().get("access_token")})
                        donationData = await donationResponse.json()
                        donationData = donationData.get("data")
                        connected = True
                    except:
                        print("\033[91mTILTIFY FUCKED UP\033[0m")
                        await asyncio.sleep(5)

                # giving tts data to obs
                if donationData != [] and donationData not in lastDonation:
                    lastDonation += [donationData]
                    await donationAlert(donationData[0].get("donor_name"), donationData[0].get("amount").get("value"), id[1], donationData[0].get("donor_comment"))
        await asyncio.sleep(5)