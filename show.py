import numpy as np
import os, glob
import cv2

file_list = glob.glob('./*.png')

file_number = len(file_list)
file_list.sort()

for i in range(file_number):

  img = cv2.imread(file_list[i], cv2.IMREAD_ANYDEPTH)
  print(img.max()-img.min())
  if img is None:
    continue
    
  img1 = cv2.normalize(img, img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
  cv2.imshow("depth_image", img1)
  k = cv2.waitKey()
  # esc quit
  if k==27:
     break
  # press a, next one
  elif k==ord('a'):
     continue
  else:
     print (k)
