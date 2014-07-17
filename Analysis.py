import os
import sys
import extras
import cv2
import cv2.cv as cv
import numpy as np
import pylab as pl
import matplotlib.cm as mpl_cm
from matplotlib import path as mpl_path

class analyze(object):
	def __init__(self, File_Saving_Dict):
		pass

		self.quitList = ['q', 'Q', 'quit', 'Quit']	 
		self.yesList = ['y', 'Y', 'yes', 'YES', 'Yes']
		self.noList = ['n', 'N', 'No', 'NO', 'no']
		self.allList = ['a', 'A', 'All', 'all', 'ALL']
		self.ps3List = ['ps3', 'Ps3', 'PS3', 'pS3', 'ps', 'Ps', 'pS', 'PS']
		self.pgList = ['pg', 'Pg', 'pG', 'PG']		

		self.File_Saving_Dict = File_Saving_Dict
		self.VideoNum = 1

		#RMS Display Parameters
		self.param_names = ['movement_std_threshold', 'wheel_translation','wheel_stretch']
		self.params = {}
	
	def maskedPlotRMS(self):
	#Private Constants

		analyze_video_type = None
		video_type_dict = {1:self.File_Saving_Dict["PS3_Target_SaveName"], 2:self.File_Saving_Dict["PG_Target_SaveName"]}
		allVideos = False

		while True:
			input = extras.getUserInput("Analyze Trial Number:")
			try:
				input = int(input)
			except:
				pass
			if (type(input) == int and os.path.isdir(self.File_Saving_Dict["File_Complete_Target_Location"],'Trial%i'%self.trialNum)):
				self.trialNum = input
				break
			else:
				print "Please enter a valid number"


		print " "
		print "Would you like to analyze PS3 Videos or Point Grey Videos?"
		print "Enter either 'PS3' or 'PG'"

		while True:
			input = extras.getUserInput("Type of Video:")
			input = int(input)
			if input in self.quitList:
				return None				
			if (input in self.ps3List):
				self.savename = self.PS3_SaveName
				print 'Analyzing playstation videos...'
				break
			elif (input in self.pgList):
				self.savename = self.pgFileName
				print 'Analyzing point grey videos...'
				break
			else:
				print "Please enter a valid response"

		print " "
		print "Which video number would you like to image?"
		print "If you would like to image them all, enter 'a'"

		while True:
			input = extras.getUserInput("Input:")
			input = int(input)
			if input in self.quitList:
				return None
			if (type(input) == int and os.path.isfile(os.path.join(self.fileTargetLocation,'\Trial%i'%self.trialNum,video_type_dict[analyze_video_type]+'%i'%input))):
				self.videoNum = input
				break
			elif input in self.allList:
				allVideos = True
			else:
				print "Please enter a valid number"	


		Continue == True
		while Continue:
			m=0
			success, frame = self.camera.vc.read()
			#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			#frame = frame.astype(np.uint8)
			#frame, timestamp = self.camera.read()
			pl.figure()
			pl.title("Select mask number: %s."%str(m+1))
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

			self.mask_pts[m] = np.array(pts, dtype=np.int32)
			self.masks[m] = mask
			self.mask_idx[m] = np.where(mask==False)
			while True:
				input = extras.getUserInput("Mask Name:")
				if type(input) == str:
					self.mask_name[m] = input
					break
				else:
					print "Please enter a valid name"
			#np.save(os.path.join(self.fileTargetLocation,'Analysis_mask_'+self.mask_name[m]), np.atleast_1d([self.masks]))

			while True:
				input = extras.getUserInput("Enter Another Mask? (Y/N):")
				if input in self.yesList:
					break
				elif input in self.noList:
					Continue = False
					break
				elif input in self.quitList:
					return None
				else:
					print "Please enter a valid response."


		pl.ion()
		self.fig = pl.figure()
		self.ax = self.fig.add_subplot(111)
		self.ax.set_ylim([-1, 255])
		self.plotdata = {m:self.ax.plot(np.arange(self.monitor_vals_display),np.zeros(self.monitor_vals_display), c)[0] for m,c in zip(self.mask_name,['r-'])} 
		self.plotline, = self.ax.plot(np.arange(self.monitor_vals_display), np.repeat(self.params['movement_std_threshold'], self.monitor_vals_display), 'r--')

		if not allVideos:	
			dir = os.listdir(self.fileTargetLocationRoot+str(self.trialNum))
			if not len(dir) == 0:
				n = 1
				while os.path.isfile(os.path.join(self.fileTargetLocationRoot+str(self.trialNum),self.savename + str(self.videoNum)+'.avi')):
					n += 1

				for self.VideoNum in range(n):
					self.std_dev_plot(os.path.join(self.fileTargetLocationRoot+str(self.trialNum), self.savename+str(self.videoNum)+'.avi'))
		else:
			self.std_dev_plot(os.path.join(self.fileTargetLocationRoot+str(self.trialNum), self.savename+str(self.videoNum)+'.avi'))

				# cap = cv2.VideoCapture(os.path.join(self.fileTargetLocationRoot+str(self.trialNum), self.savename+str(self.videoNum)+'.avi'))
				# fourcc = cv2.cv.CV_FOURCC(*'XVID')

				# width = int(cap.get(3))
				# height = int(cap.get(4))
				# numFramesInMovie = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
				# fps = int(cap.get(cv.CV_CAP_PROP_FPS))


		out = cv2.VideoWriter(os.path.join(self.fileTargetLocationRoot+'%i'%self.sortNum,self.pgFileName+vidNumStr+'.avi'),fourcc, fps, (width,height))
		f, img = cap.read()
		frameCounter = 1



		frames = self.camera.get(vc.VC_CAP_PROP_FRAME_COUNT)

		for counter in range(frames):
			pass


	def menu(self):
		print "Analysis Options:"
		print "1:  Masked RMS Difference Plot"
		print "2:  Quit"
		while True:
			input = raw_input("Your Input:")
			input = input.rstrip()
			input = int(input)
			if type(input) == int:
				if input == 1:
					self.maskedPlotRMS()
				elif input == 2:
					break
			else:
				print "Please enter a valid number"

	def std_dev_plot(self, video_file):
		pass