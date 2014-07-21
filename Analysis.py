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
		self.syncedList = ['s', 'S', 'sync', 'Sync', 'SYNC', 'synced', 'Synced', 'SYNCED']

		self.File_Saving_Dict = File_Saving_Dict
		self.VideoNum = 1

		#RMS Display Parameters
		self.color_names = ['-b', '-g', '-r', '-c', '-m', '-y', '-k', '-w']
		self.params = {}

		#Declare Necessary Variables
		self.masks = {}
		self.mask_idx = {}
		self.mask_pts = {}
		self.monitor_vals_display = 100
		self.mask_names = []
	
	def getInfo(self):
		
		date,trialNum =  extras.updateInfo(self.File_Saving_Dict)
		if (date is None) and (trialNum is None):
			return False
		else:
			self.File_Saving_Dict["Date"] = date
			self.File_Saving_Dict["Trial_Number"] = trialNum
			self.File_Saving_Dict["File_Complete_Target_Location"] = os.path.join(self.File_Saving_Dict["File_Target_Location_Root"],self.File_Saving_Dict["Mouse_Name"],self.File_Saving_Dict["Date"], "Trial%i"%self.File_Saving_Dict["Trial_Number"])
			return True
	
	def maskedPlotRMS(self):
	#Private Constants

		allVideos = False

		print "Would you like to analyze PS3, PG, or the Synchronized Videos?"
		print "Enter either 'PS3', 'PG', or 'Synced'"

		while True:
			input = extras.getUserInput("Type of Video:")
			if input in self.quitList:
				return None				
			if (input in self.ps3List):
				self.savename = self.File_Saving_Dict["PS3_Target_SaveName"]
				print 'Analyzing playstation videos...'
				break
			elif (input in self.pgList):
				self.savename = self.File_Saving_Dict["PG_Target_SaveName"]
				print 'Analyzing point grey videos...'
				break
			elif (input in self.syncedList):
				self.savename = self.File_Saving_Dict["Synced_Target_SaveName"]
				print 'analyzing the synchronized videos...'
				break
			else:
				print "Please enter a valid response"

		print " "
		print "Which video number would you like to image?"
		print "If you would like to image them all, enter 'a'"

		while True:
			input = extras.getUserInput("Input:")
			try:
				input = int(input)
			except:
				pass			
			if input in self.quitList:
				return None
			if (type(input) == int and os.path.isfile(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.savename+'%i.avi'%input))):
				self.videoNum = input
				break
			elif input in self.allList:
				allVideos = True
				break
			else:
				print "Please enter a valid number"	


		Continue = True
		m = 0
		while Continue:
			Video = cv2.VideoCapture(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.savename+'%i.avi'%input))
			success, frame = Video.read()
			#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			#frame = frame.astype(np.uint8)
			#frame, timestamp = self.camera.read()
			pl.figure()
			pl.title("Select mask number: %s."%str(m+1))
			pl.imshow(frame, cmap=mpl_cm.Greys_r)
			Video.release()
			pts = []
			while not len(pts):
				pts = pl.ginput(0)
			pl.close()
			path = mpl_path.Path(pts)
			pts = np.array(pts, dtype=np.int32)
			pts_x = pts[:,0]
			pts_y = pts[:,1]
			x_bound = (np.min(pts_x),np.max(pts_x))
			y_bound = (np.min(pts_y),np.max(pts_y))
			mask = np.ones(((y_bound[1] - y_bound[0] + 1),(x_bound[1] - x_bound[0] + 1)), dtype=bool)
			for ridx,row in enumerate(mask):
				for cidx,pt in enumerate(row):
					if path.contains_point([cidx, ridx]):
						mask[ridx+y_bound(0)-1,cidx+x_bound-1] = False

			self.mask_pts[m] = pts
			self.masks[m] = mask
			self.mask_idx[m] = np.where(mask==False)
			
			while True:
				input = extras.getUserInput("Mask Name:")
				if type(input) == str:
					self.mask_names.append(input)
					break
				else:
					print "Please enter a valid name"
			if not os.path.isdir(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],'Analysis')):
				os.mkdir(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],'Analysis'))
			np.save(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],'Analysis','Analysis_mask_'+self.mask_names[m]), np.atleast_1d([self.masks]))
			if m <= 6:
				while True:
					input = extras.getUserInput("Enter Another Mask? (Y/N):")
					if input in self.yesList:
						break
					elif input in self.noList:
						Continue = False
						m += 1
						break
					elif input in self.quitList:
						return None
					else:
						print "Please enter a valid response."


		pl.ion()
		self.fig = pl.figure()
		self.ax = self.fig.add_subplot(111)
		self.ax.set_ylim([-1, 255])
		print len(self.mask_names)
		print self.mask_names[0]
		self.plotdata = {m:self.ax.plot(np.arange(self.monitor_vals_display),np.zeros(self.monitor_vals_display), c)[0] for m,c in zip(self.mask_names[:len(self.mask_names)],self.color_names[:len(self.mask_names)])} 
		
		if allVideos:	
			dir = os.listdir(self.File_Saving_Dict["File_Complete_Target_Location"])
			if not len(dir) == 0:
				n = 1
				while os.path.isfile(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.savename+'%i.avi'%n)):
					n += 1

				for self.VideoNum in range(n):
					self.std_dev_plot()
		else:
			self.std_dev_plot()

				# cap = cv2.VideoCapture(os.path.join(self.fileTargetLocationRoot+str(self.trialNum), self.savename+str(self.videoNum)+'.avi'))
				# fourcc = cv2.cv.CV_FOURCC(*'XVID')

				# width = int(cap.get(3))
				# height = int(cap.get(4))
				# numFramesInMovie = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
				# fps = int(cap.get(cv.CV_CAP_PROP_FPS))


		# out = cv2.VideoWriter(os.path.join(self.fileTargetLocationRoot+'%i'%self.sortNum,self.pgFileName+vidNumStr+'.avi'),fourcc, fps, (width,height))
		# f, img = cap.read()
		# frameCounter = 1



		# frames = self.camera.get(vc.VC_CAP_PROP_FRAME_COUNT)

		# for counter in range(frames):
			# pass


			
	def menu(self):
		print "Analysis Options:"
		print "1:  Masked RMS Difference Plot"
		print "2:  Quit"
		while True:
			input = extras.getUserInput("Your Input:")
			try:
				input = int(input)
			except:
				print "Please enter a number"		
			if input == 1:
				self.maskedPlotRMS()
			elif input == 2:
				break
			else:
				print "Please enter in a valid number"


	def std_dev_plot(self):
		Video = cv2.VideoCapture(os.path.join(self.File_Saving_Dict["File_Complete_Target_Location"],self.savename+'%i.avi'%self.videoNum))
		success, frame = Video.read()

		numFrames = int(Video.get(cv.CV_CAP_PROP_FRAME_COUNT))
		Pts = {}
		for m in range(len(self.mask_idx)):
			Pts[m] = np.empty((len(self.mask_idx[m][0]),10))
			Pts[m][:,:] = None #Where [m] is the mask index, and [a,b] are the points analyzed, and the number of frames back ,respectively.
		width = int(Video.get(3))
		height = int(Video.get(4))
			
		self.monitor_vals = np.empty(numFrames)
		self.monitor_vals[:] = None
				
		for n in range(numFrames):
			s, image = Video.read()
			image.astype(int)
			for m in range(0,len(self.mask_idx)):
				Pts[m][:, 0] = image[self.mask_idx[0], self.mask_idx[1]]
				std_pts = np.std(Pts[m][:,:], axis = 1)
				wval = np.mean(std_pts)
				self.monitor_vals[m] = wval

		for m in enumerate(self.mask_idx):
			toShow = np.array(self.monitor_vals)
			if len(toShow) != self.monitor_vals:
				toShow = np.append(toShow, np.repeat(None, self.monitor_vals-len(toShow)))
			self.plotdata.set_ydata(toShow)
			self.fig.canvas.draw()
			time.sleep(2)
		