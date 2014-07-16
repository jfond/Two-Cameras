import sys
import cv2
import time as pytime

def getUserInput(display = ""):
	input = raw_input(display)
	input = input.rstrip()
	return input
	
def getStreamingUserInput():
	input = cv2.waitKey(1)
	return input
	
def sleep(duration = 1):
	current_time = pytime.time()
	while pytime.time() - current_time < duration:
		pass
	return True