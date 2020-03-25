# coding: utf-8

import sys
import logging
import numpy as np
import skimage
import skimage.io
import skimage.color
import skimage.feature
import cv2


logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 2:
    logging.error("Usage : {} imagefile".format(sys.argv[0]))
    sys.exit(-1)


# Load the image
imagefilepath = sys.argv[1]
logging.info("Opening {}".format(imagefilepath))

# Convert it to grayscale
rgb_image = cv2.imread(imagefilepath)
gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

# Binarize the image to find the grid 
ngray = cv2.bitwise_not(gray_image)
# threshold the image, setting all foreground pixels to
# 255 and all background pixels to 0
thresh = cv2.threshold(gray_image, 0, 255,
                        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
cv2.imwrite('thres.jpg', thresh)

# lines = cv2.HoughLines(thresh,1,np.pi/180,850)
# logging.info("{} lines detected".format(lines.shape[0]))
# for rho,theta in lines.squeeze():
# 	a = np.cos(theta)
# 	b = np.sin(theta)
# 	x0 = a*rho
# 	y0 = b*rho
# 	x1 = int(x0 + 1000*(-b))
# 	y1 = int(y0 + 1000*(a))
# 	x2 = int(x0 - 1000*(-b))
# 	y2 = int(y0 - 1000*(a))

# 	cv2.line(rgb_image,(x1,y1),(x2,y2),(0,0,255),2)

# From which we extract lines
minLineLength = 30
maxLineGap = 10
lines = cv2.HoughLinesP(thresh, 1,
                        np.pi/180,
                        80,
                        minLineLength=minLineLength,
						maxLineGap=maxLineGap)
logging.info("Got {} lines".format(len(lines)))
for x1,y1,x2,y2 in lines.squeeze():
	# print(np.sqrt((x2-x1)**2 + (y2-y1)**2))
	cv2.line(rgb_image, (x1,y1),(x2,y2),(0,255,0),2)

cv2.imwrite('houghlines.jpg', rgb_image)
