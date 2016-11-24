import threading
import time
from datetime import datetime
import cv2
import numpy as np

from sensors.cameraFilter import CameraFilter
from parallelIce.navDataClient import NavDataClient
from parallelIce.cmdvel import CMDVel
from parallelIce.extra import Extra
from parallelIce.pose3dClient import Pose3DClient


time_cycle = 80

class MyAlgorithm(threading.Thread):

    def __init__(self, camera, navdata, pose, cmdvel, extra):
        self.camera = camera
        self.navdata = navdata
        self.pose = pose
        self.cmdvel = cmdvel
        self.extra = extra

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


    def run (self):

        self.stop_event.clear()

        while (not self.kill_event.is_set()):
           
            start_time = datetime.now()

            if not self.stop_event.is_set():
                self.execute()

            finish_Time = datetime.now()

            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop (self):
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()

    def bounding(self, contours, colors, input_image_Copy):
        area = 0
        if (len(contours) != 0):
            cnt = cv2.approxPolyDP(contours[0], 3, True)
            rectX, rectY, rectW, rectH = cv2.boundingRect(cnt)

        for cnt in contours:
            # Approximates a polygonal curve(s) with the specified precision.
            cnt = cv2.approxPolyDP(cnt, 3, True);
            # It is a straight rectangle, it doesn't consider the rotation of the object. So area of the bounding rectangle won't be minimum.
            # Let (x,y) be the top-left coordinate of the rectangle and (w,h) be its width and height. 
            x, y, w, h= cv2.boundingRect(cnt)
            if((x - w) * (y -h) > area):
                rectX = x
                rectY = y
                rectH = h
                rectW = w
            if (len(contours) != 0):
                cv2.rectangle(input_image_Copy, (rectX, rectY), (rectX+rectW,rectY+rectH), (colors[0],colors[1], colors[2]) ,2)

    def execute(self):
       # Add your code here

        # Input image
        input_image = self.camera.getImage()
        if input_image is not None:
            self.camera.setColorImage(input_image)
            '''
            If you want show a thresold image (black and white image)
            self.camera.setThresoldImage(bk_image)
            '''
            # Gaussian filter (Soften the image)
            gaussian_image = cv2.GaussianBlur(input_image, (5,5), 0.2)
            cv2.imshow("gaussian", gaussian_image)

            # RGB model change to HSV
            hsv_image = cv2.cvtColor(gaussian_image, cv2.COLOR_RGB2HSV)
            cv2.imshow("HSV", hsv_image)

            # Minimum and maximum values ​​of the red
            value_min_HSV = np.array([110, 175, 140])
            value_max_HSV = np.array([180, 255, 255])
            value_min_HSV_blue = np.array([72, 58, 34])
            value_max_HSV_blue = np.array([150, 255, 255])



            # Filtering image
            image_HSV_filtered = cv2.inRange(hsv_image, value_min_HSV, value_max_HSV)
            image_HSV_filtered_blue = cv2.inRange(hsv_image, value_min_HSV_blue, value_max_HSV_blue)
            cv2.imshow("HSV filter", image_HSV_filtered)
            cv2.imshow("HSV filter blue", image_HSV_filtered_blue)

            # Close, morphology element
            kernel = np.ones((19,19), np.uint8)
            image_HSV_filt_close = cv2.morphologyEx(image_HSV_filtered, cv2.MORPH_CLOSE, kernel)
            image_HSV_filt_close_blue = cv2.morphologyEx(image_HSV_filtered_blue, cv2.MORPH_CLOSE, kernel)
            

            # Output image
            self.camera.setThresoldImage(image_HSV_filt_close+image_HSV_filt_close_blue)


            # Copying image
            image_HSV_filtered_Copy = np.copy(image_HSV_filt_close)
            image_HSV_filtered_Copy_blue = np.copy(image_HSV_filt_close_blue)
            input_image_Copy = np.copy(input_image)


            # Detection of object contour
            _, contours, hierarchy = cv2.findContours(image_HSV_filtered_Copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            _, contours_blue, hierarchy_blue = cv2.findContours(image_HSV_filtered_Copy_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Size of image
            size = input_image.shape
            height = size[0]
            width = size[1]

            # Bounding box
            colors = [0, 255, 0]
            self.bounding(contours, colors, input_image_Copy)
            colors_blue = [255, 0, 0]
            self.bounding(contours_blue, colors_blue, input_image_Copy)

            # Output image
            self.camera.setColorImage(input_image_Copy)

