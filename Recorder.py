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
cv = cv2.cv
import extras
import winsound
import time as pytime
import pylab as pl
import numpy as np
import matplotlib.cm as mpl_cm
from matplotlib import path as mpl_path


from core.cameras import CamSetup

class record(object):
	def __init__(self, Camera = None, trialNum = None, videoNum = None, PS3_SaveName = 'PS3_Vid', Freq = 80, beepDur = 25, totalFrames = 100, movement_std_threshold = 75, mask_name = 'WHEEL', resample = 1, movement_query_frames = 10, monitor_vals_display = 100, fileTargetLocation = 'C:\\Users\\Camera\\Desktop\\Two Camera Imaging\\Data\Trial1', sortingProcess = None):
	
		if type(Camera) == CamSetup:
			self.camera = Camera
		else:
			self.CameraReady = False
			print('No valid camera supplied.')
		
		#Check to make sure there are no problems with the camera
		self.fig = None
		#Initialize Variables
		self.trialNum = trialNum
		self.videoNum = videoNum
		self.PS3_SaveName = PS3_SaveName
		self.fourcc = cv2.cv.CV_FOURCC(*'XVID')
		self.totalFrames = totalFrames
		self.currentlyRecording = False
		self.cameraReady = True
		self.fileTargetLocation = fileTargetLocation
		self.isPaused = False
		self.movement_std_threshold = movement_std_threshold
		self.sortingProcess = sortingProcess
		
		#Constants
		self.Freq = Freq
		self.beepDur = beepDur
		self.mask_name = mask_name
		self.resample = resample
		self.movement_query_frames = movement_query_frames
		self.monitor_img_set = np.empty((self.camera.resolution[1],self.camera.resolution[0],self.movement_query_frames))
		self.monitor_img_set[:] = None
		self.monitor_vals_display = monitor_vals_display



		#autoRecord Parameters
		self.param_names = ['movement_std_threshold', 'wheel_translation','wheel_stretch']
		self.params = {}
		self.params['movement_std_threshold'] = movement_std_threshold
		self.params['wheel_translation'] = 50
		self.params['wheel_stretch'] = 200
			
		if not os.path.isdir(os.path.join('Data','Trial%i'%self.trialNum)):
			os.mkdir(os.path.join('Data','Trial%s'%self.trialNum))
		
	def run(self):
		if (self.cameraReady == True and self.currentlyRecording == False):
			self.currentlyRecoring = True
			#There is about a 10 ms delay between the calling the Recorder.run() function and the cameras' beginning to record video - measured with pytime.time()
			#Initialize Playstation camera and PG camera before starting recording to minimize difference between their start times
			Output = cv2.VideoWriter(os.path.join('Data','Trial%i'%self.trialNum,self.PS3_SaveName+'%i'%self.videoNum)+'.avi',self.fourcc, self.camera.frame_rate, self.camera.resolution, self.camera.color_mode)
			counter = 1
			text_file = open(os.path.join('Data','Trial%i'%self.trialNum,'Timestamps_'+self.PS3_SaveName+'%i.txt'%self.videoNum), "w")
			print ("Recording...")
			self.videoNum+=1
			#point Grey Camera - Triggered by audio commend, mostly done through hardware
			winsound.Beep(self.Freq,self.beepDur)
			
			#PS3 Camera - Done through software
			#Initialize Camera object
			while (self.camera.vc.isOpened() == True): 
				if counter < self.totalFrames:
						currentTime = pytime.time()
						text_file.write(str(currentTime)+'\n')
						counter += 1
						valid, frame = self.camera.vc.read()
						if valid==True:
							#print str(np.shape(frame))
							Output.write(frame)
							self.updatePS3Viewer(frame)	
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
	
		#Private Constants		
		yesList = ['y', 'Y', 'yes', 'YES', 'Yes']
		noList = ['n', 'N', 'No', 'NO', 'no']
	
		# Setup interface
		dir = os.listdir('C:/tmp')
		if not len(dir) == 0:
			n = 1
			while os.path.exists('C:/Data/'+str(n)):
				n += 1
			os.mkdir('C:/Data/'+str(n))
			for file in dir:
				os.rename('C:/tmp/'+file, 'C:/Data/'+str(n)+'/'+file)
				text_file = open('C:/Data/'+str(n)+'/NOTES', "w")
				text_file.write(str(pytime.localtime()))
		
		print "You may press start recording on the Point Grey Camera Now"
		time.sleep(7.5)
		
		pl.ion()
		self.fig = pl.figure()
		self.ax = self.fig.add_subplot(111)
		self.ax.set_ylim([-1, 255])
		self.plotdata = {m:self.ax.plot(np.arange(self.monitor_vals_display),np.zeros(self.monitor_vals_display), c)[0] for m,c in zip(self.mask_name,['r-'])} 
		self.plotline, = self.ax.plot(np.arange(self.monitor_vals_display), np.repeat(self.params['movement_std_threshold'], self.monitor_vals_display), 'r--')
		self.window = 'Camera'
		self.control = 'Status'
		cv2.namedWindow(self.window, cv.CV_WINDOW_NORMAL)
		cv2.namedWindow(self.control, cv.CV_WINDOW_AUTOSIZE)
		cv2.moveWindow(self.window, 0, 0)
		cv2.moveWindow(self.control, 600, 0)
		self.controls = {'Pause':'p', 'Go':'g', 'Redo':'r', 'Quit':'q', 'Manual Trigger':'t'}
		for pn in self.param_names:
			cv2.createTrackbar(pn,self.control,int(self.params[pn]), 200, self.update_trackbar_params)
		self.update_trackbar_params(self)	
		
		
		#autoRecord waits for the mouse to begin moving, and then calls the run function to begin recording
		if self.cameraReady:
			print "Auto Recording..."
			self.set_masks()
			while self.cameraReady:
				if not self.currentlyRecording:
					input = extras.getStreamingUserInput() #Allows user to pause, unpause, quit, or manually trigger a run
					self.cameraReady = self.handleUserInput(input)					
					thisFrame = self.grabFrame()
					if self.mouseMovement(thisFrame) > self.movement_std_threshold:
						self.run()
						self.monitor_img_set = np.empty((self.camera.resolution[1],self.camera.resolution[0],self.movement_query_frames))
						self.monitor_img_set[:] = None
					else:
						self.updatePS3Viewer(thisFrame)
			while True:
				input = extras.getUserInput("Would you like to save these videos? (Y/N):")
				if input in yesList:
					print "Please stop recording with the Point Grey Camera"
					time.sleep(15)
					print "Saving Videos..."
					print "Please do not destroy the process or turn off the machine."
					self.sortingProcess.saveFiles()
					print "Saving Complete"
					break
				elif input in noList:
					break
				else:
					print "Please enter a valid response."

		else:
			print "Error in Auto Recording."
			return None

	def update_trackbar_params(self, _):
		for param in self.param_names:
			self.params[param] = cv2.getTrackbarPos(param,self.control)
		self.params['wheel_translation'] -= 50
		self.params['wheel_stretch'] /= 25.
		self.plotline.set_ydata(np.repeat(self.params['movement_std_threshold'], self.monitor_vals_display))
		
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
		np.save(os.path.join(self.fileTargetLocation,self.PS3_SaveName+'_mask'), np.atleast_1d([self.masks]))

	def handleUserInput(self, input):         
            if input == ord('p'):
                self.isPaused = True
                self.update_status()
                
            if input == ord('g'):
                self.isPaused = False

            if input == ord('q'):
                return False
            
            if not self.isPaused:
                if input==ord('t'):
                    self.run()
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
		return wval
		#self.monitor_vals['WHEEL'] = np.roll(self.monitor_vals['WHEEL'], -1)
		#self.monitor_vals['WHEEL'][-1] = wval

	def updatePS3Viewer(self, thisFrame):
		cv2.polylines(thisFrame, [self.mask_pts], 1, (255,255,255), thickness=1)
		cv2.imshow(self.window, thisFrame)
