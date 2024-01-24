"""
This tool is to convert the picture to XY arrays.
"""
import cv2 as cv
import numpy as np
import os
import zhinst.utils
from itertools import chain
import matplotlib.pyplot as plt




def fig_xy_convert(path):

        #path = "C:/Users/panhuih/Pictures/Fu.png"
        img = cv.imread(path)
        imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        imgBlur = cv.GaussianBlur(imgGray, (3, 3), 0)
        imgCanny = cv.Canny(img, 128, 255 )
        default_height = len(imgCanny[0])

        #cv.imshow("Gray Image", imgGray)
        #cv.imshow("Blur Image", imgBlur)
        cv.imshow("Canny Image", imgCanny)
        cv.waitKey()
        # Get the contour of the image
        contour_tuple = cv.findContours(imgCanny, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_NONE)
        contours = contour_tuple[0]
        rings = [np.array(c).reshape([-1, 2]) for c in contours]

        # Get ratio of between the width and the height of the image
        true_ratio = 1

        # adjust coordinate system to the image coordinate system
        max_x, max_y, min_x, min_y = 0, 0, 0, 0
        for ring in rings:
            max_x = max(max_x, ring.max(axis=0)[0])
            max_y = max(max_y, ring.max(axis=0)[1])
            min_x = max(min_x, ring.min(axis=0)[0])
            min_y = max(min_y, ring.min(axis=0)[1])

        # adjust ratio
        plt.figure(figsize=[default_height * true_ratio, default_height])

        # plot to the matplotlib
        wave_x = []
        wave_y = []
        for _, ring in enumerate(rings):
            close_ring = np.vstack((ring, ring[0]))
            xx = close_ring[..., 0]
            time = np.arange(0, len(xx))
            yy = max_y - close_ring[..., 1]
            wave_x.append(xx)
            wave_y.append(yy)
        wave_x = list(chain.from_iterable(wave_x))
        wave_y = list(chain.from_iterable(wave_y))
        wave_x = wave_x/max(wave_x)-0.5
        wave_y = wave_y/max(wave_y)-0.5
        #print(wave_x)
        print(len(wave_x))
        #plt.scatter(wave_x, wave_y, s =1, c= 'r' )
        #plt.show()


        # Save the data of XY to two csv files and to the waves folder under HDAWG
        data_dir = "C:/Users/panhuih/OneDrive - Zurich Instruments AG/Documents/Zurich Instruments/LabOne/WebServer"
        wave_dir = os.path.join(data_dir, "awg", "waves")
        csv_file_x = os.path.join(wave_dir, "wave_x.csv")
        csv_file_y = os.path.join(wave_dir, "wave_y.csv")
        np.savetxt(csv_file_x, wave_x)
        np.savetxt(csv_file_y, wave_y)



        return (wave_x, wave_y)

fig_xy_convert("C:/Users/panhuih/Pictures/ZI.png")
