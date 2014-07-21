import sys
import os
import extras
from core.cameras import CamSetup
from Organize import Organizer
from Recorder import Record
from core.cameras import CamSetup
from Analysis import analyze

def Menu_Loop(Imaging_Dict, File_Saving_Dict, Constants_Dict):
	#Acceptable entries for performing a certain command
	saveCommandList = ['s','S','Sort','sort']
	quitCommandList = ['q', 'Q', 'quit', 'Quit']
	runCommandList = ['run', 'go', 'record', 'g', 'G']
	viewCommandList = ['v', 'V', 'view', 'View']
	recordCommandList = ['r', 'R', 'record', 'Record', 'Record', 'autorecord']
	analyzeCommandList = ['a', 'A', 'analyze', 'Analyze', 'ANALYZE']
	syncCommandList = ['y', 'Y', 'sync', 'Sync', 'SYNC']
	changeCommandList = ['c', 'C', 'Change', 'change', 'CHANGE']

	Camera = CamSetup(Imaging_Dict)
	
	try:
		Camera.vc.read()
		Camera_Exists = True
	except:
		Camera_Exists = False
	
	while True:
		
	temp_ID = Imaging_Dict
	temp_FSD = File_Saving_Dict
	temp_CD = Constants_Dict
		
		while os.path.isdir(os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial%i"%File_Saving_Dict["Trial_Number"])):
			File_Saving_Dict["Trial_Number"] += 1
	
		print " "
		print "MENU: (Current Mouse: " + File_Saving_Dict["Mouse_Name"] +")"
		print "  Enter 'Quit' to Quit"
		if Camera_Exists:
			print "  Enter 'Go' to manually start recording one video (unstable)"
			print "  Enter 'Record' to have the software automatically record mouse movement"
		print "  Enter 'Change' to select a different mouse"
		print "  Enter 'Sort' to move and rename all Point Grey files to the Data folder"
		print "  Enter 'Analyze' to begin analyzing the data"
		print "  Enter 'Sync' to begin synchronizing the videos"
		print "  Enter 'View' to see from the Playstation 3 Camera without recording anything"
		
		input = extras.getUserInput("Input:")

		if (input in saveCommandList):
			savingProcess = Organizer(temp_FSD)
			if savingProcess.getInfo():
				if savingProcess.getSaveFrameCount():
					savingProcess.saveFiles()
			savingProcess = None
			
		elif (input in viewCommandList):
			extras.View(Camera,temp_FSD["File_Target_Location_Root"])
		
		elif (input in quitCommandList):
			break
		
		elif (input in runCommandList) and (Camera_Exists):
			if not Recording.currentlyRecording:
				Recording.run()
			else:
				print "->Camera is currently recording"
				print "  Please wait a moment to manually trigger it"
				
		elif (input in recordCommandList) and (Camera_Exists):
			Recording = Record(temp_ID, temp_FSD, temp_CD, Camera)
			Recording.autoRecord()
			Recording = None
			
		elif (input in analyzeCommandList):
			Analysis = analyze(temp_FSD)
			if Analysis.getInfo():
				Analysis.menu()
			pass
	  
		elif (input in syncCommandList):
			savingProcess = Organizer(temp_FSD)
			if savingProcess.getInfo():
				savingProcess.syncFiles()
			savingProcess = None
	  
		elif (input in changeCommandList):
			File_Saving_Dict["Mouse_Name"] = Mouse_Loop(File_Saving_Dict["File_Target_Location_Root"])
		
		else:
			print "->Did not recognize user input."
			print "  Please enter a valid command."

	
def Mouse_Loop(Directory):
	#Lists
	otherList = ['o', 'O', 'other', 'Other', 'OTHER']
	quitList = ['q', 'Q', 'quit', 'Quit', 'QUIT']
	yesList = ['y', 'Y', 'yes', 'YES', 'Yes']
	noList = ['n', 'N', 'No', 'nO', 'NO', 'no']
	
	text_file = open(Directory + '/Mice List.txt', "r")
	chosen_mouse = None
	miceDict = {}
	print "MOUSE MENU:"
	mouse = text_file.readline()
	mouse = mouse.rstrip()
	number = 1
	while not (mouse == ''):
		print "  Enter '%i' for mouse: "%number + mouse
		miceDict[number] = mouse
		mouse = text_file.readline()
		mouse = mouse.rstrip()
		number += 1
	text_file.close()
	print "  Enter 'Other' to enter a new mouse"
	print "  Enter 'Quit' to quit mouse selection"
	while True:
		input = extras.getUserInput("Input:")
		try:
			input = int(input)
		except:
			pass
		if type(input) == int and (input > 0) and (input < number):
			chosen_mouse = miceDict[input]	
			return chosen_mouse
		elif input in quitList:
			return None
		if input in otherList:
			while True:
				input = extras.getUserInput("Mouse Name: ")
				if input in noList:
					return None
				while True:
					print "You are about to add the mouse '"+input+"' to the list of mice"
					answer = extras.getUserInput("Is this correct? (Y/N):")
					if answer in yesList:
						text_file = open(Directory + '/Mice List.txt', "a")
						text_file.write('\n'+input)	
						chosen_mouse = input
						return chosen_mouse
					elif answer in noList:
						return None
					else:
						print "Please enter a valid response"
		else:
			print "Please enter a valid response"