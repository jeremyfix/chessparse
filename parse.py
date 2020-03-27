# coding: utf-8

import sys
import logging
import numpy as np
import skimage
import skimage.io
import skimage.color
import skimage.feature
import argparse
import cv2


logging.basicConfig(level=logging.DEBUG)

# The parser of input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=int,
                    choices=[1, 2],
                    help="Which type of grid are we processing?",
                    required=True)
parser.add_argument('imagefile', nargs=1,
                    help='The image file to process')
args = parser.parse_args()


# Load the image
imagefilepath = args.imagefile[0]
logging.info("Opening {}".format(imagefilepath))

# Convert it to grayscale
rgb_image = cv2.imread(imagefilepath)
result_image = rgb_image.copy()
gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

# Little blur
blur_image = cv2.GaussianBlur(gray_image,(7, 7),0)
cv2.imwrite('0-blur.jpg', blur_image)
# thres_image = cv2.threshold(blur_image, 0, 255,
# cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
thres_image = cv2.adaptiveThreshold(blur_image, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 7, 5)

cv2.imwrite('1-threshold.jpg', thres_image)
# Binarize the image to find the grid 
ngray = cv2.bitwise_not(thres_image)
cv2.imwrite('2-not.jpg', ngray)

# Dilation to fill in some gaps
kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
dilation = cv2.dilate(ngray, kernel, iterations=1)
cv2.imwrite('3-dilation.jpg', dilation)

# Detect the connected components
retval, labels, stats, centroids = cv2.connectedComponentsWithStats(dilation, connectivity=4)

# It seems the index 0 is the whole image
largest_cc_idx=np.argmax(stats[1:, cv2.CC_STAT_AREA])+1
logging.info("The largest component I found is idx {} with area {}".format(largest_cc_idx, stats[largest_cc_idx, cv2.CC_STAT_AREA]))

# Store the top left pixel and with , height of the grid
coordinates_grid = {"left": stats[largest_cc_idx, cv2.CC_STAT_LEFT],
                    "top": stats[largest_cc_idx, cv2.CC_STAT_TOP],
                    "width": stats[largest_cc_idx, cv2.CC_STAT_WIDTH],
                    "height": stats[largest_cc_idx, cv2.CC_STAT_HEIGHT]
                   }
logging.info("BBox of the largest object {}".format(coordinates_grid))

cv2.rectangle(result_image, (0, 0), (50, 50), color=(255, 0, 0), thickness=3)
cv2.rectangle(result_image,
              (coordinates_grid["left"], coordinates_grid["top"]),
              (coordinates_grid["left"] + coordinates_grid["width"],
               coordinates_grid["top"] + coordinates_grid["height"]),
              color=(255, 0, 0), thickness=2)
cv2.imwrite("4-grid.jpg", result_image)

