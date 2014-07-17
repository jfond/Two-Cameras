import sys
import cv2
import cv2.cv as cv
import time as pytime
import numpy as np
import os

def getUserInput(display = ""):
	input = raw_input(display)
	input = input.rstrip()
	return input
	
def getStreamingUserInput():
	input = cv2.waitKey(1)
	return input
	
def sleep(duration = 1):
	current_time = pytime.time()
	while pytime.time() - current_time < duration:
		pass
	return True
	
def View(Camera,location):
	Overlay_Index = QUIT_OVERLAY(location)
	window = 'Live_Camera'	
	while True:
		input = getStreamingUserInput()
		if input == ord('q'):
			break
		f, image = Camera.vc.read()
		image[Overlay_Index[0], Overlay_Index[1],:] = (36,28,237)
		cv2.imshow(window, image)
	cv2.destroyWindow(window)
	
def QUIT_OVERLAY(location):
	image = cv2.imread(os.path.join(location,'Quit_Icon.png'))
	mask = np.ones((np.shape(image)[0], np.shape(image)[1],1), dtype=bool)
	for y,row in enumerate(image):
		for x,unused_point in enumerate(row):
			if (image[y,x,:] == (36,28,237)).all():
				mask[y,x] = False
	Overlay_Index = np.where(mask==False)
	return Overlay_Index
	
def updateInfo(File_Saving_Dict):
	
	quitList = ['n','N', 'No', 'NO', 'no']
	
	
	while True:
		input = getUserInput("Date (DDMMYYYY):")
		input = int(input)
		if input in quitList:
			return False			
		if type(input) == int:
			date = str(input)
			checkLocation = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"])
			if (os.path.isdir(checkLocation) == False):
				print "Error: Could not find Trial folder for sorting"
			else:
				break
		else:
			print "Please enter a valid numerical date in the form 'DDMMYYYY'"
	
	while True:
		input = extras.getUserInput("Trial Number:")
		input = int(input)
		if input in quitList:
			return False				
		if type(input) == int:
			trialNum = input
			checkLocation = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial%i"%File_Saving_Dict["Trial_Number"])
			if (os.path.isdir(checkLocation) == False):
				print "Error: Could not find Trial folder for sorting"
			else:
				File_Saving_Dict["File_Complete_Target_Location"] = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial%i"%File_Saving_Dict["Trial_Number"])
				break
		else:
			print "Please enter a valid number"

		return date,trialNum

