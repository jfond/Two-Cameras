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
	def __init__(self, Camera = None, fileTargetLocationRoot = 'C:\\Users\\Camera\\Desktop\\Two Camera Imaging\\Data\Trial', PS3_Savename = "PS3_Vid" ):
		pass
		self.camera = Camera
		self.fileTargetLocationRoot = fileTargetLocationRoot
		self.PS3_Savename = PS3_Savename
		
	def maskedPlotRMS(self):
	#Private Constants
		yesList = ['y', 'Y', 'yes', 'YES', 'Yes']
		noList = ['n', 'N', 'No', 'NO', 'no']
		allList = ['a', 'A', 'All', 'all', 'ALL']
		allVideos = False
	
		while True:
			input = raw_input("Analyze Trial Number:")
			input = input.rstrip()
			input = int(input)
			if (type(input) == int and os.path.isdir(self.fileTargetLocation,'Trial%i'%self.trialNum)):
				self.trialNum = input
				break
			else:
				print "Please enter a valid number"

		print " "
		print "Which video number would you like to image?"
		print "If you would like to image them all, enter 'a'"
		
		while True:
			input = extras.getUserInput("Input:")
			input = input.rstrip()
			input = int(input)
			if (type(input) == int and os.path.isfile(os.path.join(self.fileTargetLocation,'\Trial%i'%self.trialNum,self.PS3_Savename+'%i'%input))):
				self.videoNum = input
				break
			elif input in allList:
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
			np.save(os.path.join(self.fileTargetLocation,'Analysis_mask_'+self.mask_name[m]), np.atleast_1d([self.masks]))
			
			while True:
				input = extras.getUserInput("Enter Another Mask? (Y/N):")
				if input in yesList:
					break
				elif input in noList:
					Continue = False
					break
				else:
					print "Please enter a valid response."
	
			
	
	
	
	
	
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