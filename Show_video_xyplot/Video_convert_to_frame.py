import cv2
import os
import numpy as np
import os
import zhinst.utils
from itertools import chain
import matplotlib.pyplot as plt

def save_img(video_path):
    vc = cv2.VideoCapture(video_path)
    c = 0
    rval = vc.isOpened()

    while rval:
      c =c + 1
      rval, frame = vc.read()
      img = frame
      if rval:
        img_resize = cv2.resize(img, (1080, 607))
        imgGray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 0)
        imgCanny = cv2.Canny(img_resize, 0, 255)
        cv2.imwrite('C:/Users/panhuih/Videos/Demo_img/Demo_'+ str(c) + '.jpg', imgCanny)
      else:
        break
    vc.release()

save_img("C:/Users/panhuih/Videos/Videos_test/Demo.mp4")

