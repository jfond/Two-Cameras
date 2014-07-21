import cv2
import os
import extras
import time
import sys
from core.cameras import CamSetup
from Main_Loops import Menu_Loop
from Main_Loops import Mouse_Loop

#######################
# THINGS TO DO:
#1. Proper naming of the timestamp files: don't overlap with ps3 videos		- done																				- DONE
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

#Constants
Constants_Dict = {}
Constants_Dict["Frequency"] = 80     
Constants_Dict["Beep_Duration"] = 25 #Milliseconds

#Imaging Parameters
Imaging_Dict = {}
Imaging_Dict["FPS"] = 120
Imaging_Dict["PS3_Resolution"] = (320,240)
Imaging_Dict["Video_Duration"] = 4.0 #seconds
Imaging_Dict["Total_Frames"] = int(Imaging_Dict["FPS"] * Imaging_Dict["Video_Duration"])
Imaging_Dict["Color_Mode"] = CamSetup.COLOR
Imaging_Dict["Query_Frames"] = 10
Imaging_Dict["Number_STD_Points_Displayed"] = 100
Imaging_Dict["STD_Translation"] = 50
Imaging_Dict["STD_Scale_Factor"] = 100
Imaging_Dict["Movement_STD_Threshold"] = 110

#File Saving Parameters
File_Saving_Dict = {}
File_Saving_Dict["Date"] =  time.strftime("%d%m%Y")
File_Saving_Dict["PS3_Target_SaveName"] = 'PS3_Vid'
File_Saving_Dict["PG_Target_SaveName"] = 'PG_Vid'
File_Saving_Dict["Synced_Target_SaveName"] = 'Synchronized_Vid'
File_Saving_Dict["PG_Initial_SaveName"] = 'fc2_save'
File_Saving_Dict["File_Target_Location_Root"] = 'C:\Users\Camera\Desktop\GtHUb\Two-Cameras\Data' #Used when I need flexibility in manipulating directories
File_Saving_Dict["File_PG_Initial_Save_Location"] = "C:\\tmp"
File_Saving_Dict["Frames_In_Saved_Video"] = Imaging_Dict["Total_Frames"]

File_Saving_Dict["Mouse_Name"] = Mouse_Loop(File_Saving_Dict["File_Target_Location_Root"])
if File_Saving_Dict["Mouse_Name"] is None:
	sys.exit(0)

#Select first number available to name the video:
trialNum,videoNum = 1,1 #counter variables
while os.path.isdir(os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial%i"%trialNum)):
	trialNum += 1
#Prepare the system for recording...	

File_Saving_Dict["Trial_Number"] = trialNum
File_Saving_Dict["File_Complete_Target_Location"] = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial%i"%File_Saving_Dict["Trial_Number"]) #Used when I want to be compact

Menu_Loop(Imaging_Dict, File_Saving_Dict, Constants_Dict)
	
cv2.destroyAllWindows()						
			