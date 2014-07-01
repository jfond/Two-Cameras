import sys
import cv2

def getUserInput(display = ""):
	input = raw_input(display)
	input = input.rstrip()
	return input
	
def getStreamingUserInput():
	input = cv2.waitKey(1)
	return input