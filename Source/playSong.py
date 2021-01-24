# to build, use "cd (playsong directory)"
# pyinstaller --onefile playSong.py

import keyboard
import pythoncom
import threading

global isPlaying
global infoTuple

isPlaying = False
storedIndex = -1
conversionCases = {'!': '1', '@': '2', '£': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0'}

def onDelPress(event):
	global isPlaying
	isPlaying = not isPlaying

	if isPlaying:
		playNextNote()

	return True

def isShifted(charIn):
	asciiValue = ord(charIn)
	if(asciiValue >= 65 and asciiValue <= 90):
		return True
	if(charIn in "!@#$%^&*()_+{}|:\"<>?"):
		return True
	return False

def pressLetter(strLetter, t):
	if isShifted(strLetter):
		# we have to convert all symbols to numbers
		if strLetter in conversionCases:
			strLetter = conversionCases[strLetter]
		keyboard.press('left shift')
		keyboard.press(strLetter.lower())
		keyboard.release('left shift')
		keyboard.call_later(keyboard.release, args=(strLetter), delay=t)
	else:
		keyboard.press(strLetter)
		keyboard.call_later(keyboard.release, args=(strLetter), delay=t)

	return
		
def processFile():
	with open("song.txt","r") as macro_file:
		lines = macro_file.read().split("\n")
		tOffsetSet = False
		tOffset = 0
		tempo = 60/float(lines[0].split(" ")[1])
		
		processedNotes = []
		
		for l in lines[1:]:
			l = l.split(" ")
			if(len(l) < 2):
				# print("INVALID LINE")
				continue
			
			waitToPress = float(l[0])
			notes = l[1]
			processedNotes.append([waitToPress,notes])
			if(not tOffsetSet):
				tOffset = waitToPress
				print("Starting macro with offset t=",tOffset)
				tOffsetSet = True

	return [tempo,tOffset,processedNotes]

def floorToZero(i):
	if(i > 0):
		return i
	else:
		return 0

# for this method, we instead use delays as l[0] and work using indexes with delays instead of time
# we'll use recursion and threading to press keys
def parseInfo():
	tempo = infoTuple[0]
	notes = infoTuple[2]
	
	# parse time between each note
	for i in range(0, len(notes)):
		if not i == len(notes)-1:
			note = notes[i]
			nextNote = notes[i+1]
			note[0] = (nextNote[0] - note[0]) * tempo

	# let's just hold the last note for 1 second because we have no data on it
	notes[len(notes)-1][0] = 1.00

	return notes

def playNextNote():
	global isPlaying
	global storedIndex

	notes = infoTuple[2]
	if isPlaying and storedIndex < len(infoTuple[2])-1:
		storedIndex += 1
		noteInfo = notes[storedIndex]
		delay = floorToZero(noteInfo[0])

		for n in noteInfo[1]:
			pressLetter(n, delay)

		print("%10.2f %15s" % (delay,noteInfo[1]))
		threading.Timer(delay, playNextNote).start()
	elif storedIndex >= len(infoTuple[2])-1:
		isPlaying = False
		storedIndex = -1

def rewind(KeyboardEvent):
	global storedIndex
	if storedIndex - 10 < 0:
		storedIndex = 0
	else:
		storedIndex -= 10

def skip(KeyboardEvent):
	global storedIndex
	if storedIndex + 10 > len(infoTuple[2]):
		isPlaying = False
		storedIndex = 0
	else:
		storedIndex += 10

infoTuple = processFile()
infoTuple[2] = parseInfo()
keyboard.on_press_key("delete", onDelPress)
keyboard.on_press_key("home", rewind)
keyboard.on_press_key("end", skip)
pythoncom.PumpMessages()
