import cv2
cv = cv2.cv
import time

class CamSetup(object):
	BW = 0
	COLOR = 1
	def __init__(self, Imaging_Dict):
		camera_index = 0
		try:
			self.vc = cv2.VideoCapture(camera_index) #If there is more than one camera plugged in, this may record from the wrong camera. Changing the index will change which camera is used (i.e. 0->1)
		except:
			raise Exception('Video capture from camera failed to initialize. Check Camera Index and make sure Camera is plugged in correctly.')
			sys.exit(1)

		self.vc.set(cv.CV_CAP_PROP_FPS, Imaging_Dict["FPS"])
		self.vc.set(cv.CV_CAP_PROP_FRAME_WIDTH, Imaging_Dict["PS3_Resolution"][0])
		self.vc.set(cv.CV_CAP_PROP_FRAME_HEIGHT, Imaging_Dict["PS3_Resolution"][1])



	def release(self):
		self.vc.release()	

