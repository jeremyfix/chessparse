# coding: utf-8

import sys
import logging
import numpy as np
import skimage
import skimage.io
import skimage.color
import skimage.feature
import cv2

if len(sys.argv) != 2:
    logging.error("Usage : {} imagefile".format(sys.argv[0]))
    sys.exit(-1)


# Load the image
imagefilepath = sys.argv[1]
logging.info("Opening ", imagefilepath)
rgb_image = skimage.io.imread(imagefilepath)

# Convert it to grayscale
rgb_image = cv2.imread(imagefilepath)
gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

# Extract the edges
edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
cv2.imwrite('edges-50-150.jpg', edges)

# From which we extract lines
minLineLength = 100
maxLineGap = 30
lines = cv2.HoughLinesP(edges, 0.1,
                        np.pi/2000,
                        30,
                        minLineLength,maxLineGap)
for l in lines:
    x1,y1,x2,y2 = l[0]
    cv2.line(rgb_image, (x1,y1),(x2,y2),(0,255,0),2)

cv2.imwrite('houghlines.jpg', rgb_image)
