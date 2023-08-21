# functions for letting chat press keys based on their messages
# the arrow keys didn't seem to work on my pc so use LEFT, RIGHT, UP, and DOWN at your own risk ig

# imports
import ctypes
import pynput
import aiofile

# change controller here
from controllers.gbaController import *

# setting up variables
connection = None
chatPlaying = False
inputBotPlaying = False
idleBotPlaying = False
autoSaving = False
snackShot = False
snackHealed = False
idleBotStatus = False
timeSinceLastMessage = time.time()
snacks = ["sleepy", "chris", "burst", "silly", "cautious", "sonic"]
currentSnack = "chris"
sendInput = ctypes.windll.user32.SendInput
keyCodes = {"Q": 0x10, "W": 0x11, "E": 0x12, "R": 0x13, "T": 0x14, "Y": 0x15, "U": 0x16, "I": 0x17, "O": 0x18, "P": 0x19, "A": 0x1E, "S": 0x1F, "D": 0x20, "F": 0x21, "G": 0x22, "H": 0x23, "J": 0x24, "K": 0x25, "L": 0x26, "Z": 0x2C, "X": 0x2D, "C": 0x2E, "V": 0x2F, "B": 0x30, "N": 0x31, "M": 0x32, "LEFT": 0xCB, "RIGHT": 0xCD, "UP": 0xC8, "DOWN": 0xD0, "ESCAPE": 0x01, "ONE": 0x02, "TWO": 0x03, "THREE": 0x04, "FOUR": 0x05, "FIVE": 0x06, "SIX": 0x07, "SEVEN": 0x08, "EIGHT": 0x09, "NINE": 0x0A, "ZERO": 0x0B, "MINUS": 0x0C, "EQUALS": 0x0D, "BACKSPACE": 0x0E, "APOSTROPHE": 0x28, "SEMICOLON": 0x27, "TAB": 0x0F, "CAPSLOCK": 0x3A, "ENTER": 0x1C, "CONTROL": 0x1D, "ALT": 0x38, "SHIFT": 0x2A, "TILDE": 0x29, "PRINTSCREEN": 0x37, "NUMLOCK": 0x45, "SPACE": 0x39, "DELETE": 0x53, "COMMA": 0x33, "PERIOD": 0x34, "BACKSLASH": 0x35, "FORWARDSLASH": 0x2B, "OPENBRACKET": 0x1A, "CLOSEBRACKET": 0x1B, "F1": 0x3B, "F2": 0x3C, "F3": 0x3D, "F4": 0x3E, "F5": 0x3F, "F6": 0x40, "F7": 0x41, "F8": 0x42, "F9": 0x43, "F10": 0x44, "F11": 0x57, "F12": 0x58}

# reading config
config = configparser.ConfigParser()
config.read(os.path.abspath((os.path.join(directory, "config.ini"))))
snackDirectory = config.get("directories", "snack status")

# holds down the given key
async def holdKey(key):
	extra = ctypes.c_ulong(0)
	ii_ = pynput._util.win32.INPUT_union()
	ii_.ki = pynput._util.win32.KEYBDINPUT(0, key, 0x0008, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
	x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
	sendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# releases the given key
async def releaseKey(key):
	extra = ctypes.c_ulong(0)
	ii_ = pynput._util.win32.INPUT_union()
	ii_.ki = pynput._util.win32.KEYBDINPUT(0, key, 0x0008 | 0x0002, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
	x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
	sendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# holds down the given key for the given number of seconds
async def holdAndReleaseKey(key, delay):
	await holdKey(key)
	await asyncio.sleep(delay)
	await releaseKey(key)

# presses the autosave key every ten minutes
async def autoSave():
	while autoSaving:
		await holdKey(keyCodes.get("SHIFT"))
		await holdAndReleaseKey(keyCodes.get("F1"), 1)
		await releaseKey(keyCodes.get("SHIFT"))
		await asyncio.sleep(600)

# starts autosaving
async def startAutoSave():
	global autoSaving
	autoSaving = True
	asyncio.create_task(autoSave())

# stops autosaving
async def stopAutoSave():
	global autoSaving
	autoSaving = False

# starts the input bot
async def startInputBot():
	global inputBotPlaying
	inputBotPlaying = True
	asyncio.create_task(inputBot())

# stops the input bot
async def stopInputBot():
	global inputBotPlaying
	inputBotPlaying = False

# starts idle bot
async def startIdleBot():
	global idleBotPlaying
	idleBotPlaying = True
	asyncio.create_task(idleBot())

# stops the idle bot
async def stopIdleBot():
	global idleBotPlaying
	idleBotPlaying = False

# allows the program to start taking and executing commands from chat messages
async def startChatPlays():
	global chatPlaying
	chatPlaying = True

# stops the program from executing commands from chat
async def stopChatPlays():
	global chatPlaying
	chatPlaying = False

# updates snack status text in obs
async def updateSnatus():
	async with aiofile.async_open(os.path.abspath(snackDirectory), "w") as file:
		if idleBotStatus:
			await file.write("idle bot is active")
		elif snackShot and not snackHealed:
			await file.write(currentSnack + " snack is dead")
		else:
			await file.write(currentSnack + " snack is alive")