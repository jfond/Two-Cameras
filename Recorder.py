#########################################
#Some parts of this class are work of Ben Deverett.
#Parts have been transferred or adapted form his
#work in the experimental-interface master repository on github.
#Exp. Interface Master can be found at:
#https://github.com/bensondaled/exp_interface
#
#
#
#Author: Jacob Fondriest
##########################################

import time
import json
import os
import cv2
import cv2.cv as cv
import extras
import winsound
import time as pytime
import pylab as pl
import numpy as np
import matplotlib.cm as mpl_cm
from matplotlib import path as mpl_path

from Organize import Organizer
from core.cameras import CamSetup

class Record(object):
	FOURCC = cv.CV_FOURCC(*'XVID')
	quitList = ['q', 'Q', 'quit', 'Quit']		
	yesList = ['y', 'Y', 'yes', 'YES', 'Yes']
	noList = ['n', 'N', 'No', 'NO', 'no']
	doneList = ['d', 'D', 'Done', 'done', 'DONE']
	
	def __init__(self, Imaging_Dict, File_Saving_Dict, Constants_Dict, Camera = None):
	
		if type(Camera) == CamSetup:
			self.camera = Camera
			self.camera.vc.read()
		else:
			raise Exception('No valid camera supplied.')
	
		self.Imaging_Dict = Imaging_Dict
		self.File_Saving_Dict = File_Saving_Dict
		self.Constants_Dict = Constants_Dict
	
		self.videoNum = 1
		self.fig = None
		self.currentlyRecording = False
		self.cameraReady = True
		self.isPaused = False #Must be manually triggered. Can be resumed by the 'g' key
		self.isSuspended = False #Happens automatically due to user input sleep time. Can be overridden by the 'g' key, or by waiting for the prescribed time
		
		#Constants
		self.mask_name = 'WHEEL'
		self.resample = 1
		self.movement_query_frames = Imaging_Dict["Query_Frames"]
		self.monitor_img_set = np.empty((self.Imaging_Dict["PS3_Resolution"][1],self.Imaging_Dict["PS3_Resolution"][0],self.movement_query_frames))
		self.monitor_img_set[:] = None
		self.monitor_vals_display = Imaging_Dict["Number_STD_Points_Displayed"]
		self.monitor_vals = np.empty(self.monitor_vals_display)
		for m in self.monitor_vals:
			self.monitor_vals[:] = None
		
		#autoRecord Parameters
		self.param_names = ['movement_std_threshold', 'wheel_translation','wheel_stretch']
		self.params = {}
		self.params['movement_std_threshold'] = self.Imaging_Dict["Movement_STD_Threshold"]
		self.params['wheel_translation'] = Imaging_Dict["STD_Translation"]
		self.params['wheel_stretch'] = Imaging_Dict["STD_Scale_Factor"]
			
		if not os.path.isdir(self.File_Saving_Dict["File_Complete_Target_Location"]):
			if not os.path.isdir(os.path.join(self.File_Saving_Dict["File_Target_Location_Root"],self.File_Saving_Dict["Mouse_Name"])):	
				os.mkdir(os.path.join(self.File_Saving_Dict["File_Target_Location_Root"],self.File_Saving_Dict["Mouse_Name"]))
			if not os.path.isdir(os.path.join(self.File_Saving_Dict["File_Target_Location_Root"],self.File_Saving_Dict["Mouse_Name"],self.File_Saving_Dict["Date"])):	
				os.mkdir(os.path.join(self.File_Saving_Dict["File_Target_Location_Root"],self.File_Saving_Dict["Mouse_Name"],self.File_Saving_Dict["Date"]))
			os.mkdir(self.File_Saving_Dict["File_Complete_Target_Location"])
		
	def run(self):
		if (self.cameraReady == True and self.currentlyRecording == False):
			self.currentlyRecoring = True
	
			Output = cv2.VideoWriter(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.File_Saving_Dict["PS3_Target_SaveName"]+'%i.avi'%self.videoNum),self.FOURCC, self.Imaging_Dict["FPS"],  self.Imaging_Dict["PS3_Resolution"], self.Imaging_Dict["Color_Mode"])
			counter = 1
			text_file = open(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],'Timestamps_'+self.File_Saving_Dict["PS3_Target_SaveName"]+'%i.txt'%self.videoNum), "w")
			print ("Recording...")
			self.videoNum+=1
			#point Grey Camera - Triggered by audio commend, mostly done through hardware
			winsound.Beep(self.Constants_Dict["Frequency"],self.Constants_Dict["Beep_Duration"])
			extras.sleep(0.05) #Wait a moment for the LED to turn on all the way. The Point Grey Camera is also delayed for 50 ms.
			extras.sleep(0.191) #My best estimate to account for the time difference between activation of the PS3 and PG
			#PS3 Camera - Done through software
			#Initialize Camera object
			while (self.camera.vc.isOpened() == True): 
				if counter < self.Imaging_Dict["Total_Frames"]:
						currentTime = pytime.time()
						text_file.write(str(currentTime)+'\n')
						counter += 1
						valid, frame = self.camera.vc.read()
						if valid==True:
							Output.write(frame)
							self.updatePS3Viewer(frame)	#no idea why this dosen't work here...
						else:
							print "Unable to read from Playstation camera. Please make sure it is plugged in."
							break
				else:
					break
			print("Recording Complete")
			Output.release()
			text_file.close()	
			self.currentlyRecording = False
			
	def autoRecord(self):
	
		#Ask user for minimum time between trials
		sleep_time = None
		while sleep_time is None:
			input = extras.getUserInput("Seconds between trials:")
			if input in self.quitList:
				return None
			try:
				sleep_time = float(input)
			except:
				print "Please enter a valid number"

	
		# Setup interface
		dir = os.listdir(self.File_Saving_Dict["File_PG_Initial_Save_Location"])
		if not len(dir) == 0:
			n = 1
			while os.path.exists('C:/Data/%i'%n):
				n += 1
			os.mkdir('C:/Data/%i'%n)
			for file in dir:
				os.rename('C:/tmp/'+file, os.path.join('C:/Data/%i'%n,file))
			text_file = open('C:/Data/%i'%n+'/NOTES', "w")
			text_file.write(str(pytime.localtime()))
			text_file.close()
		 
		print "You may press start recording on the Point Grey Camera Now"
		print "Do not set the mask until the Point Grey Camera has begun recording"
		
		pl.ion()
		self.fig = pl.figure()
		self.ax = self.fig.add_subplot(111)
		self.ax.set_ylim([-1, 255])
		self.plotdata = self.ax.plot(np.arange(self.monitor_vals_display),np.zeros(self.monitor_vals_display), 'r-')[0]  
		self.plotline, = self.ax.plot(np.arange(self.monitor_vals_display), np.repeat(self.params['movement_std_threshold'], self.monitor_vals_display), 'r--')
		self.window = 'Camera'
		self.control = 'Status'
		cv2.namedWindow(self.window, cv.CV_WINDOW_NORMAL)
		cv2.namedWindow(self.control, cv.CV_WINDOW_AUTOSIZE)
		cv2.moveWindow(self.window, 0, 0)
		cv2.moveWindow(self.control, 600, 0)
		for pn in self.param_names:
			cv2.createTrackbar(pn,self.control,int(self.params[pn]), 200, self.update_windows)
		self.update_windows(self)	
		
		
		#autoRecord waits for the mouse to begin moving, and then calls the run function to begin recording
		if self.cameraReady:
			print "Auto Recording..."
			self.set_masks()
			text_file = open(self.File_Saving_Dict["File_Complete_Target_Location"]+"\Parameters.txt", "w")
			for parameter in self.Imaging_Dict:
				text_file.write(str(parameter) + ": " + str(self.Imaging_Dict[parameter]) +"\n")
			text_file.write("Suspend Time: %d"%sleep_time)
			text_file.close()
			while self.cameraReady:
				if not self.currentlyRecording:
					input = extras.getStreamingUserInput() #Allows user to pause, unpause, quit, or manually trigger a run
					self.cameraReady = self.handleUserInput(input)					
					if self.isSuspended and (pytime.time() - sleep_begin > sleep_time):
						if self.isPaused:
							print "Trial Paused, but no longer suspended. Press the 'g' key to resume"
						else:
							print "Trial Resumed"
						self.isSuspended = False
					if not self.isPaused and not self.isSuspended:
						thisFrame = self.grabFrame()
						if self.mouseMovement(thisFrame) > self.Imaging_Dict["Movement_STD_Threshold"]:
							self.run()
							self.monitor_img_set = np.empty((self.Imaging_Dict["PS3_Resolution"][1],self.Imaging_Dict["PS3_Resolution"][0],self.movement_query_frames))
							self.monitor_img_set[:] = None
							self.monitor_vals = np.empty(self.monitor_vals_display)
							for m in self.monitor_vals:
								self.monitor_vals[:] = None				
							if sleep_time >= 1:
								self.isSuspended = True
								sleep_begin = pytime.time()
								print "Trial temporarily suspended"
						else:
							self.updatePS3Viewer(thisFrame)
							self.update_windows(self)
			while True:
				input = extras.getUserInput("Would you like to save these videos now? (Y/N):")
				if input in self.yesList:
					while True:
						print "Type 'Done' when the Point Grey Camera recording has stopped and the buffer has cleared"
						input = extras.getUserInput("")
						if input in self.doneList:
							break
						else:
							print "Unrecognised Command"
					print "Saving Videos..."
					self.savingProcess = Organizer(self.File_Saving_Dict)
					print "Please do not destroy the process or turn off the machine."
					self.savingProcess.saveFiles()
					print "Saving Complete"
					while True:
						input = extras.getUserInput("Would you like to sync these videos now? (Y/N):")
						if input in self.yesList:
							print "Synchronizing Videos..."
							print "Please do not destroy the process or turn off the machine."
							self.savingProcess.syncFiles()
							print "Synchronization Complete"
						elif input in self.noList:
							break
						else:
							print "Please enter a valid response"
					break
				elif input in self.noList:
					break
				else:
					print "Please enter a valid response."

		else:
			print "Error in Auto Recording."
			return None

	def update_windows(self, _):
		for param in self.param_names:
			self.params[param] = cv2.getTrackbarPos(param,self.control)
		self.params['wheel_translation'] -= 50
		self.params['wheel_stretch'] /= 25.
		self.plotline.set_ydata(np.repeat(self.params['movement_std_threshold'], self.monitor_vals_display))
		toShow = np.array(self.monitor_vals)
		if len(toShow) != self.monitor_vals_display:
			toShow = np.append(toShow, np.repeat(None, self.monitor_vals_display-len(toShow)))
		self.plotdata.set_ydata(toShow)
		self.fig.canvas.draw()		
		
		
	def set_masks(self):
		m=self.mask_name
		success, frame = self.camera.vc.read()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = frame.astype(np.uint8)
		#frame, timestamp = self.camera.read()
		pl.figure()
		pl.title("Select mask: %s."%m)
		pl.imshow(frame, cmap=mpl_cm.Greys_r)
		pts = []
		while not len(pts):
			pts = pl.ginput(0)
		pl.close()
		path = mpl_path.Path(pts)
		mask = np.ones(np.shape(frame), dtype=bool)
		for ridx,row in enumerate(mask):
			for cidx,pt in enumerate(row):
				if path.contains_point([cidx, ridx]):
					mask[ridx,cidx] = False
		
		self.mask_pts = np.array(pts, dtype=np.int32)
		self.masks = mask
		self.mask_idx = np.where(mask==False)
		#np.save(os.path.join(self.fileTargetLocation,self.PS3_SaveName+'_mask'), np.atleast_1d([self.masks]))

	def handleUserInput(self, input):         
		if input == ord('p'):
			self.isPaused = True
			print "Trial Paused"

		if input == ord('g'):
			self.isPaused = False
			self.isSuspended = False
			print "Trial Resumed"

		if input == ord('q'):
			return False

		if input==ord('t'):
			print "Trial Resumed"
			self.isPaused = False
			self.isSuspended = False
			self.run()
			self.monitor_img_set = np.empty((self.Imaging_Dict["PS3_Resolution"][1],self.Imaging_Dict["PS3_Resolution"][0],self.movement_query_frames))
			self.monitor_img_set[:] = None
			self.monitor_vals = np.empty(self.monitor_vals_display)
			self.monitor_vals[:] = None
		return True
		
	def grabFrame(self):
		success, frame = self.camera.vc.read()
		return frame
		
	def mouseMovement(self, thisFrame):
		#if None in self.monitor_img_set:
		#	return 
		thisFrame = cv2.cvtColor(thisFrame, cv2.COLOR_BGR2GRAY)
		thisFrame = thisFrame.astype(np.uint8)
		
		self.monitor_img_set = np.roll(self.monitor_img_set, 1, axis=2)
		self.monitor_img_set[:,:,0] = thisFrame
		pts = self.monitor_img_set[self.mask_idx[0],self.mask_idx[1],:]
		std_pts = np.std(pts, axis=1)
		wval = np.mean(std_pts) * self.params['wheel_stretch'] + self.params['wheel_translation']
		#print "Wval: " + str(wval)
		self.monitor_vals = np.roll(self.monitor_vals, -1)
		self.monitor_vals[-1] = wval
		return wval

	def updatePS3Viewer(self, thisFrame):
		cv2.polylines(thisFrame, [self.mask_pts], 1, (255,255,255), thickness=1)
		cv2.imshow(self.window, thisFrame)
