# coding: utf-8

import os
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
parser.add_argument('imagefile', nargs=1,
                    help='The image file to process')
parser.add_argument('--delta_theta',
                    default=0.01,
                    help="The tolerance on the orientation of horizontal lines")
parser.add_argument('--output_dir', default='.',
                    help="The directory where to save the images")
args = parser.parse_args()

delta_theta = float(args.delta_theta)

# Load the image
imagefilepath = args.imagefile[0]
logging.info("Opening {}".format(imagefilepath))

# Convert it to grayscale
rgb_image = cv2.imread(imagefilepath)
result_image = rgb_image.copy()
gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

# Little blur
blur_image = cv2.GaussianBlur(gray_image,(7, 7),0)
cv2.imwrite(os.path.join(args.output_dir, '0-blur.jpg'), blur_image)
# thres_image = cv2.threshold(blur_image, 0, 255,
# cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
thres_image = cv2.adaptiveThreshold(blur_image, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 7, 5)

cv2.imwrite(os.path.join(args.output_dir, '1-threshold.jpg'), thres_image)
# Binarize the image to find the grid 
ngray = cv2.bitwise_not(thres_image)
cv2.imwrite(os.path.join(args.output_dir, '2-not.jpg'), ngray)

# Dilation to fill in some gaps
kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
dilation = cv2.dilate(ngray, kernel, iterations=1)
cv2.imwrite(os.path.join(args.output_dir, '3-dilation.jpg'), dilation)

# Detect the connected components
retval, labels, stats, centroids = cv2.connectedComponentsWithStats(dilation, connectivity=4)

# It seems the index 0 is the whole image
largest_cc_idx=np.argmax(stats[1:, cv2.CC_STAT_AREA])+1
logging.info("The largest component I found is idx {} with area {}".format(largest_cc_idx, stats[largest_cc_idx, cv2.CC_STAT_AREA]))

# Filter the lines of the grid
grid_mask = labels == largest_cc_idx
nogrid_mask = np.logical_not(grid_mask)

dilation[grid_mask] = 255
dilation[nogrid_mask] = 0

# cv2.erode(dilation, np.ones((10,10),np.uint8), iterations=3)


# Store the top left pixel and with , height of the grid
coordinates_grid = {"left": stats[largest_cc_idx, cv2.CC_STAT_LEFT],
                    "top": stats[largest_cc_idx, cv2.CC_STAT_TOP],
                    "width": stats[largest_cc_idx, cv2.CC_STAT_WIDTH],
                    "height": stats[largest_cc_idx, cv2.CC_STAT_HEIGHT]
                   }
coordinates_grid["right"] = coordinates_grid["left"] + coordinates_grid["width"]
coordinates_grid["bottom"] = coordinates_grid["top"] + coordinates_grid["height"]
logging.info("BBox of the largest object {}".format(coordinates_grid))

cv2.rectangle(result_image,
              (coordinates_grid["left"], coordinates_grid["top"]),
              (coordinates_grid["right"], coordinates_grid["bottom"]),
              color=(255, 0, 0), thickness=2)
cv2.imwrite(os.path.join(args.output_dir, "4-grid.jpg"), result_image)

# We can now crop the image around the grid
# The cropped RGB image
rgb_grid = rgb_image[coordinates_grid["top"]:coordinates_grid["bottom"],
                     coordinates_grid["left"]:coordinates_grid["right"]]
result_grid = rgb_grid.copy()
dilation_grid = dilation[coordinates_grid["top"]:coordinates_grid["bottom"],
                         coordinates_grid["left"]:coordinates_grid["right"]]

cv2.imwrite(os.path.join(args.output_dir, "5-rgb_grid.jpg"), rgb_grid)
cv2.imwrite(os.path.join(args.output_dir, "5-dilation_grid.jpg"), dilation_grid)

# Detecting the vertical and horizontal lines

lines = cv2.HoughLines(dilation_grid, rho=1, theta=np.pi/180.0, threshold=300).squeeze()
# The lines are represented by (rho, theta)
# rho is the distance from the origin (0, 0) top left corner
# theta is the orientation with 0 for vertical line and pi/2 for horizontal lines
vertical_lines = []
horizontal_lines = []
logging.info("Filtering the vertical and horizontal lines with tolerance {}".format(delta_theta))
for rho, theta in lines:
    if theta == 0:
        pt1 = (rho, 0)
        pt2 = (rho, coordinates_grid["height"])
        vertical_lines.append(rho)
        cv2.line(result_grid, pt1, pt2, color=(0, 0, 255), thickness=1)
    if np.pi/2.0 - delta_theta <= theta <= np.pi/2.0 + delta_theta:
        m = -1./np.tan(theta)
        c = rho/np.sin(theta)
        horizontal_lines.append(c)
        pt1 = (0, c)
        pt2 = (coordinates_grid["width"], int(m*coordinates_grid["width"] + c))
        cv2.line(result_grid, pt1, pt2, color=(0, 0, 255), thickness=1)
cv2.imwrite(os.path.join(args.output_dir, '6-lines.jpg'), result_grid)
 
