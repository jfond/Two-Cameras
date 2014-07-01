import os
import sys
import extras
import cv2
import cv2.cv as cv
import numpy as np

class sortProcess(object):
	def __init__(self, fileStartLocation = None, fileTargetLocationRoot = None, trialNum=1, pgFilename='PG_Vid', ps3Filename = 'PS3_Vid',framePerVid = 765):
		#Initialize variables
		self.fileStartLocation = fileStartLocation
		self.fileTargetLocationRoot = fileTargetLocationRoot
		self.pgFilename = pgFilename #
		self.ps3Filename = ps3Filename #Name of PS3 Videos 
		self.pgSaveName = 'fc2_save' #Name of raw saved Point Grey Videos
		self.sortingProcessPossible = True
		self.framePerVid = framePerVid
		self.trialNum = trialNum	 #This one should be static
		self.sortNum = self.trialNum #This one can vary
		print str(self.trialNum)
		
		print " " #Makes things look nicer
		
		#Verify that the directories given exist
		if not os.path.isdir(self.fileStartLocation):
			print ('->The File Start Location Supplied does not exist')
			print ('  Please choose a valid File Start Location')
			self.sortingProcessPossible = False
		if not os.path.isdir(self.fileTargetLocationRoot+'%i'%self.trialNum):
			self.trialNum -= 1
			if not os.path.isdir(self.fileTargetLocationRoot+'%i'%self.trialNum):
				print "->Could not find appropriate Trial folder to place sorted videos"
				print "  Please choose a valid File Target Location"
				self.sotringProcessPossible = False

		#Scan Point Grey folder for Point Grey video files
		# thereAreNotPgVideos = True 
		# dir = os.listdir(self.fileStartLocation)
		# for file in dir:
			# if file[:8] == "fc2_save":
				# thereAreNotPgVideos = False
				# break	
		# if thereAreNotPgVideos:
			# print ("->There are no Point Grey videos under the name '"+ self.pgSaveName+"'")
			# self.sortingProcessPossible = False
		# #Check PS3 folder for ps3 files
		# if not os.path.isfile(os.path.join(self.fileTargetLocation,ps3Filename+"1.avi")):
			# dirs = os.listdir(self.fileTargetLocation)
			# #print(dirs[1])
			# print('->There are no PS3 videos under the name '+ps3Filename)
			# self.sortingProcessPossible = False
					
		print " " #Makes things look nicer
		
	def isPossible(self):
		return self.sortingProcessPossible
		
	def sort(self, trialNum):
		while True:
			input = raw_input("Trial Number:")
			input = input.rstrip()
			input = int(input)
			print str(input)
			if type(input) == int:
				self.sortNum = input
				print str(input)
				break
			else:
				print "Please enter a valid number"
			if (os.path.isdir(self.fileTargetLocation) == False):
				print "Error: Could not find Trial folder for sorting"
				return None		
		
		#Eventually check frames in the videos vs number of PS3 videos and compare
		
		# #Count the number of unpaired PS3 Videos
		# dir = os.listdir(self.fileTargetLocation)
		# file = None
		numberofPS3Videos = 0
		# for file in dir:
			# if file[:7] == self.ps3Filename:
				# numberofPS3Videos +=1
		
		
		# #Count the number of raw Point Grey Videos
		# dir = os.listdir(self.fileStartLocation)
		numberofPGVideos = 0
		# for file in dir:
			# if file[:8] == "fc2_save":
				# numberofPGVideos +=1
			# else:
				# dir.remove(file)	
		
		if (numberofPGVideos == numberofPS3Videos): #A weak check to try to ensure that we are pairing videos correctly
			self.saveFiles()
		else: 
			print "->Number of Point Grey videos did not match number of PS3 Videos."
			print "  Please remove unwanted videos and try again"
				
	def saveFiles(self):
		dir = os.listdir(self.fileStartLocation)
		for file in dir:
			if not file[:8] == "fc2_save":
				dir.remove(file)
		numMoviesTotal = len(dir) - 1
		movieCounter = 0
		file = dir[movieCounter]
		
		cap = cv2.VideoCapture(os.path.join(self.fileStartLocation,file))
		fourcc = cv2.cv.CV_FOURCC(*'XVID')
		
		width = int(cap.get(3))
		height = int(cap.get(4))
		numFramesInMovie = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
		fps = int(cap.get(cv.CV_CAP_PROP_FPS))
		
		vidNum = 1
		vidNumStr = "%04d" % vidNum
		
		out = cv2.VideoWriter(os.path.join(self.fileTargetLocationRoot+'%i'%self.sortNum,self.pgFilename+vidNumStr+'.avi'),fourcc, fps, (width,height))
		f, img = cap.read()
		frameCounter = 1
		
		while (True):
			cv2.waitKey(1)
			f, img = cap.read()
			out.write(img)
			
			if (frameCounter  == numFramesInMovie):
				cap.release()
				if not (movieCounter==numMoviesTotal):
					movieCounter += 1
					file = dir[movieCounter]
					cap = cv2.VideoCapture(os.path.join(self.fileStartLocation,file))
					numFramesInMovie += int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
				else:
					break
			if (frameCounter % self.framePerVid == 0):
				out.release()
				vidNum +=1
				vidNumStr = "%04d" % vidNum
				out = cv2.VideoWriter(os.path.join(self.fileTargetLocationRoot+'%i'%self.sortNum,self.pgFilename+vidNumStr+'.avi'),fourcc, 120, (width,height))
						
			frameCounter += 1

	
	