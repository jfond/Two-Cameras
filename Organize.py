import os
import sys
import extras
import cv2
import cv2.cv as cv
import numpy as np

class Organizer(object):
	FOURCC = cv2.cv.CV_FOURCC(*'XVID')
	quitList = ['q', 'Q', 'quit', 'Quit']
	
	def __init__(self, File_Saving_Dict):
		#Initialize Dictionary
		self.File_Saving_Dict = File_Saving_Dict


		print " " #Makes things look nicer
			
	def getLocation(self):
		
		while True:
			input = extras.getUserInput("Date (DDMMYYYY):")
			input = int(input)
			if input in self.quitList:
				return None			
			if type(input) == int:
				File_Saving_Dict["Date"] = input
				checkLocation = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"])
				if (os.path.isdir(checkLocation) == False):
					print "Error: Could not find Trial folder for sorting"
					return None
				else:
					break
			else:
				print "Please enter a valid numerical date in the form 'DDMMYYYY'"
		
		while True:
			input = extras.getUserInput("Trial Number:")
			input = int(input)
			if input in self.quitList:
				return None				
			if type(input) == int:
				File_Saving_Dict["Trial_Number"] = input
				checkLocation = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial" + str(File_Saving_Dict["Trial_Number"]))
				if (os.path.isdir(File_Saving_Dict["File_Complete_Target_Location"]) == False):
					print "Error: Could not find Trial folder for sorting"
					return None
				else:
					File_Saving_Dict["File_Complete_Target_Location"] = os.path.join(File_Saving_Dict["File_Target_Location_Root"],File_Saving_Dict["Mouse_Name"],File_Saving_Dict["Date"], "Trial%i"%File_Saving_Dict["Trial_Number"])
					break
			else:
				print "Please enter a valid number"

	def getFrameCount(self):
		
		while True:
			input = extras.getUserInput("Frames per Video:")
			if input in self.quitList:
				return None				
			try:
				File_Saving_Dict["Frames_In_Saved_Video"] = int(input)
				break
			except:
				print "Please enter a valid number"
				
	def saveFiles(self):
		#Find all desired PG videos
		dir = os.listdir(self.File_Saving_Dict["File_PG_Initial_Save_Location"])
		length = len(self.File_Saving_Dict["PG_Initial_SaveName"])
		for file in dir:
			if not (file[:length] == self.File_Saving_Dict["PG_Initial_SaveName"]):
				dir.remove(file)
		
		numMoviesTotal = len(dir)
		movieCounter = 0
		file = dir[movieCounter]
		
		cap = cv2.VideoCapture(os.path.join(File_Saving_Dict["File_PG_Initial_Save_Location"],file))
		
		width = int(cap.get(3))
		height = int(cap.get(4))
		numFramesInMovie = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
		fps = int(cap.get(cv.CV_CAP_PROP_FPS))
		
		frameCounter = 1
		vidNum = 1
		
		out = cv2.VideoWriter(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.File_Saving_Dict["PG_Target_SaveName"]+'%i.avi'%vidNum),FOURCC, fps, (width,height))
		f, img = cap.read()

		while (True):
			cv2.waitKey(1)
			f, img = cap.read()
			out.write(img)
			
			if (frameCounter  == numFramesInMovie):
				cap.release()
				if not (movieCounter==numMoviesTotal):
					movieCounter += 1
					file = dir[movieCounter]
					cap = cv2.VideoCapture(os.path.join(File_Saving_Dict["File_PG_Initial_Save_Location"],file))
					numFramesInMovie += int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
				else:
					break
			if (frameCounter % self.File_Saving_Dict["Frames_In_Saved_Video"] == 0):
				out.release()
				vidNum +=1
				out = cv2.VideoWriter(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.File_Saving_Dict["PG_Target_SaveName"]+'%i.avi'%vidNum),FOURCC, fps, (width,height))
						
			frameCounter += 1
			
	def syncFiles(self):	
			
		dir = os.listdir(self.File_Saving_Dict["File_Complete_Target_Location"])
		length = len(self.File_Saving_Dict["PS3_Target_SaveName"])
		for file in dir:
			if not (file[:length] == self.File_Saving_Dict["PS3_Target_SaveName"]):
				dir.remove(file)		
				
		
		for videoNum in enumerate(dir):
			vidNum = videoNum[0] + 1
			cap1 = cv2.VideoCapture(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.File_Saving_Dict["PS3_Target_SaveName"]+'%i.avi'%vidNum))
			cap2 = cv2.VideoCapture(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.File_Saving_Dict["PG_Target_SaveName"]+'%i.avi'%vidNum))
			width1 = int(cap1.get(3))
			width2 = int(cap2.get(3))
			height1 = int(cap1.get(4))
			height2 = int(cap2.get(4))
			frames_in_video1 = int(cap1.get(cv.CV_CAP_PROP_FRAME_COUNT))
			frames_in_video2 = int(cap2.get(cv.CV_CAP_PROP_FRAME_COUNT))	
			fps1 = int(cap1.get(cv.CV_CAP_PROP_FPS))
			fps2 = int(cap2.get(cv.CV_CAP_PROP_FPS))
			timeTotal = min(((frames_in_video1/fps1),(frames_in_video2/fps2)))				
			fps = np.max((fps1,fps2))
			framesTotal = timeTotal*fps
			fps_ratio = (fps1/fps2)
			slower_camera_index = 1 #Camera index is 0 or 1 where 0 is cap1 and 1 is cap2
			if fps_ratio < 1:
				fps_ratio = 1/fps_ratio
				slower_camera_index = 0
				faster_camera_index = 1
			smaller_resolution_index = 0
			if (width2*height2 < width1*height1):
				smaller_resolution_index = 1
			Height = max(height1,height2)
			Width = (width1 + width2)	

			camera1 = {"cap":cap1,"width":width1,"height":height1,"frames":frames_in_video1,"fps":fps1}
			camera2 = {"cap":cap2,"width":width2,"height":height2,"frames":frames_in_video2,"fps":fps2}
			camera_list = (camera1,camera2)
               
			out = cv2.VideoWriter(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],'Synchronized_Vid%i'%vidNum+'.avi'),FOURCC, fps, (Width,Height),0)			
			image = np.ones((Height,Width))
			
			for n in range(framesTotal-2):
				cv2.waitKey(1)
							
				if n%fps_ratio < 1:
					if (slower_camera_index == smaller_resolution_index):
						f1, img_small = camera_list[slower_camera_index]["cap"].read()
						img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)	
					else: 
						f1, img_large = camera_list[slower_camera_index]["cap"].read()
						img_large = cv2.cvtColor(img_large, cv2.COLOR_BGR2GRAY)
					
				if (slower_camera_index == smaller_resolution_index):
					f1, img_large = camera_list[(slower_camera_index+1)%2]["cap"].read()
					img_large = cv2.cvtColor(img_large, cv2.COLOR_BGR2GRAY)
				else: 
					f1, img_small = camera_list[(slower_camera_index+1)%2]["cap"].read() 
					img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)	
					
				image[:camera_list[(smaller_resolution_index+1)%2]["height"], :camera_list[(smaller_resolution_index+1)%2]["width"]] = img_large
				image[:camera_list[smaller_resolution_index]["height"], camera_list[(smaller_resolution_index+1)%2]["width"]:Width] = img_small
				image = image.astype(np.uint8)
				
				out.write(image)
			
			cap1.release()
			cap2.release()
			out.release()
			#cv2.destroyAllWindows()