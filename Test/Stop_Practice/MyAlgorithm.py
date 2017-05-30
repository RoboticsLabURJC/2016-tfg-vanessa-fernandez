import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
import cv2

from matplotlib import pyplot as plt
time_cycle = 80
        

class MyAlgorithm(threading.Thread):

    def __init__(self, pose3d, camera, motors):
        self.camera = camera
        self.pose3d = pose3d
        self.motors = motors

        #self.imageRight=None
        self.image=None
        # 0 to grayscale
        self.template = cv2.imread('resources/template.png',0)

        # Car direction
        self.carx = 0.0
        self.cary = 0.0

        # Obstacles direction
        self.obsx = 0.0
        self.obsy = 0.0


        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


    def setImageFiltered(self, image):
        self.lock.acquire()
        #self.imageRight=image
        self.lock.release()

    def getImageFiltered(self):
        self.lock.acquire()
        tempImage=self.image
        self.lock.release()
        return tempImage

    def parse_laser_data(self,laser_data):
        laser = []
        for i in range(laser_data.numLaser):
            dist = laser_data.distanceData[i]/1000.0
            angle = math.radians(i)
            laser += [(dist, angle)]
        return laser
    
    def laser_vector(self,laser_array):
        laser_vectorized = []
        for d,a in laser_array:
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1 
            v = (x, y)
            laser_vectorized += [v]
        return laser_vectorized

    def run (self):
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

    def execute(self):
        
        # TODO
        print ('execute')
       
        # GETTING THE IMAGES
        input_image = self.camera.getImage()

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.motors.setV(10)
        #self.motors.setW(5)

        # RGB model change to HSV
        hsv_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2HSV)

        # Values of red
        value_min_HSV = np.array([0, 71, 0])
        value_max_HSV = np.array([179, 232, 63])

        # Filtering image
        image_filtered = cv2.inRange(hsv_image, value_min_HSV, value_max_HSV)
        cv2.imshow("filtered", image_filtered)

        # Close, morphology element
        kernel = np.ones((11,11), np.uint8)
        image_filtered = cv2.morphologyEx(image_filtered, cv2.MORPH_CLOSE, kernel)

        detection = False

        # Template's size
        h, w = self.template.shape

        # Matching with template image
        # match: grayscale image, where each pixel denotes how much does the neighbourhood of that pixel math with template
        match = cv2.matchTemplate(image_filtered,self.template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(match >= threshold)
        # zip: This function returns a list of tuples, where the i-th tuple contains the i-th element from each of the argument sequences or iterables.
        for pt in zip(*loc[::-1]):
            cv2.rectangle(input_image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
            cv2.rectangle(image_filtered, pt, (pt[0] + w, pt[1] + h), (255,0,0), 2)
            detection = True
            print("Found signal")
            self.motors.sendV(0)


        if detection == False:
            self.motors.sendV(50)

        cv2.imshow('img', image_filtered)

