import sys
import winsound
import numpy as np
import cv2
import os
import extras
from Organize import sortProcess
from Recorder import record
from core.cameras import CamSetup
import time
from Analysis import analyze

#######################
# THINGS TO DO:
#1. Proper naming of the timestamp files: don't overlap with ps3 videos																						- DONE
#2. Get the sorting process functional                                                                                                                      - DONE
#3. Implement Experimental Interface so that the video taking beings when the mouse begins to move
#4. Implement a viewing software that will merge the two videos together properly
#5. Do some kind of validation through software that confirms that the videos are true to the fps and resolution they specified
#6. GUI?
#7. One Timestamp.txt for every ps3 video																													- DONE
#8. Have sorting properly autosave files rather than rely on user to remember
#9. Give proper credit to Ben Deverett wherever applicable
#10. Close all windows after doing the autoTrigger
#######################



print ('Initializing...')
#Initialize Static Variables
Freq = 80
beepDur = 25 #Milliseconds
fps = 75
PS3_SaveName = 'PS3_Vid'
resolution = (640,480)
videoDur = 6.4 #seconds
totalFrames = int(fps * videoDur)
fourcc = cv2.cv.CV_FOURCC(*'XVID')
movement_std_threshold = 100
fileTargetLocationRoot = 'C:\\Users\\Camera\\Desktop\\Two Camera Imaging\\Data\Trial'

#Acceptable entries for performing a certain command
sortCommandList = ['s','S','Sort','sort']
quitCommandList = ['q', 'Q', 'quit', 'Quit']
runCommandList = ['run', 'go', 'record', 'g', 'G']
viewCommandList = ['v', 'V', 'view', 'View']
recordCommandList = ['r', 'R', 'record', 'Record', 'Record', 'autorecord']
analyzeCommandList = ['a', 'A', 'analyze', 'Analyze', 'ANALYZE']

#Select first number available to name the video:
trialNum,videoNum = 1,1 #counter variables
while os.path.isdir(os.path.join('Data','Trial%s'%trialNum)):
	trialNum += 1
fileTargetLocation = fileTargetLocationRoot+'%iWS'%trialNum
#Prepare the system for recording...	

Camera = CamSetup(idx=0,resolution=resolution,frame_rate=fps,color_mode=CamSetup.COLOR)
sortingProcess = sortProcess(fileStartLocation = 'C:\\tmp',fileTargetLocationRoot = fileTargetLocationRoot,  pgFilename='PG_Vid', ps3Filename = 'PS3_Vid')

while True:
	print "MENU:"
	print "  Enter 'quit' to Quit"
	print "  Enter 'go' to manually start recording one video (unstable)"
	print "  Enter 'view' to view saved videos"
	print "  Enter 'sort' to move and rename all Point Grey files to the Data folder"
	print "  Enter 'record' to have the software automatically record mouse movement"
	print "  Enter 'analyze' to begin analyzing the data"

	input = extras.getUserInput("Input:")

	if (input in sortCommandList):
		if sortingProcess.isPossible():
			sortingProcess.sort(trialNum)
		

	elif (input in viewCommandList):
		VideoSelect(name=savename)
	
	elif (input in quitCommandList):
		break
	
	elif (input in runCommandList):
		if not Recording.currentlyRecording:
			Recording.run()
		else:
			print "->Camera is currently recording"
			print "  Please wait a moment to manually trigger it"
			
	elif (input in recordCommandList):
		Recording = record(Camera = Camera, trialNum = trialNum, videoNum = videoNum, PS3_SaveName = PS3_SaveName, Freq = Freq, beepDur = beepDur, totalFrames = totalFrames, movement_std_threshold = movement_std_threshold, mask_name = 'WHEEL', resample = 1, movement_query_frames = 10, monitor_vals_display = 100, fileTargetLocation = 'C:\\Users\\Camera\\Desktop\\Two Camera Imaging\\Data\Trial1', sortingProcess = None)
		Recording.autoRecord()
		
	elif (input in analyzeCommandList):
		Analysis = analyze(Camera, fileTargetLocationRoot,PS3_SaveName )
		Analysis.menu()
  
	else:
		print "->Did not recognize user input."
		print "  Please enter a valid command."
		
		
Camera.release()
cv2.destroyAllWindows()	
	
	