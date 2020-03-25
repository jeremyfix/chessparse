# coding: utf-8

import sys
import logging
import numpy as np
import skimage
from skimage.transform import hough_line, hough_line_peaks

if len(sys.argv) != 2:
    logging.error("Usage : {} imagefile", sys.argv[0])
    sys.exit(-1)


imagefilepath = sys.argv[0]
image = skimage.io.imread(imagefilepath)

# Look for vertical and horizontal lines
tested_angles = [0.0, np.pi/2.0]
h, theta, d = hough_line(image, theta=tested_angles)
