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

    def __init__(self, pose3d, cameraL, cameraR, cameraC, motors):
        self.cameraL = cameraL
        self.cameraR = cameraR
        self.cameraC = cameraC
        self.pose3d = pose3d
        self.motors = motors

        self.imageC = None
        self.imageL = None
        self.imageR = None
        
        self.detection = False
        self.stop = False
        
        # 0 to grayscale
        self.template = cv2.imread('resources/template.png',0)

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
        input_image = self.cameraC.getImage()

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.motors.setV(10)
        #self.motors.setW(5)

        # RGB model change to HSV
        hsv_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2HSV)

        # Values of red
        value_min_HSV = np.array([131, 71, 0])
        value_max_HSV = np.array([179, 232, 63])

        # Segmentation
        image_filtered = cv2.inRange(hsv_image, value_min_HSV, value_max_HSV)
        #cv2.imshow("filtered", image_filtered)

        # Close, morphology element
        kernel = np.ones((11,11), np.uint8)
        image_filtered = cv2.morphologyEx(image_filtered, cv2.MORPH_CLOSE, kernel)
        #cv2.imshow('cierre', image_filtered)

        # Template's size
        h, w = self.template.shape

        #detection = False
            
        # Detection of object contour
        img2, contours, hierarchy = cv2.findContours(image_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if (len(contours) != 0):
            # Approximates a polygonal curve(s) with the specified precision.
            cnt = cv2.approxPolyDP(contours[0], 3, True)
            
            # It's a straight rectangle, it doesn't consider the rotation of the object. So area of the bounding rectangle won't be minimum.
            # Let (x,y) be the top-left coordinate of the rectangle and (w,h) be its width and height. 
            x, y, bw, bh = cv2.boundingRect(cnt)
            
            # Draw the box
            img_rect = cv2.rectangle(image_filtered, (x, y), (x+bw,y+bh), (0,0,0) ,0)
            # Cut an image (the signal)
            img_bounding = img_rect[(y-4):(y+bh+4), (x-4):(x+bw+4)]
            
            if img_bounding != []:
                # Resize an image
                img_res = cv2.resize(img_bounding, (w, h), interpolation=cv2.INTER_CUBIC)
                            
                # Matching with template image
                # match: grayscale image, where each pixel denotes how much does the neighbourhood of that pixel math with template
                match = cv2.matchTemplate(img_res,self.template,cv2.TM_CCOEFF_NORMED)
                #cv2.imshow("matching", match)
                threshold = 0.3
                loc = np.where(match >= threshold)
                # zip: This function returns a list of tuples, where the i-th tuple contains the i-th element from each of the argument sequences or iterables.
                for pt in zip(*loc[::-1]):
                    cv2.rectangle(input_image, (pt[0]+x,pt[1]+y), (pt[0] + bw+x, pt[1] + bh+y), (0,0,255), 2)
                    self.detection = True
                    print("Found signal")
                    
                if self.detection == True:
                    print('bw:       ', bw)
                    print('bh:       ', bh)  
                    
                    if self.stop == False:
                        if bw >= 10 and bw < 30:
                            self.motors.sendV(50)
                            print('VELOCIDAD:     50')
                        elif bw >= 30 and bw < 45:
                            self.motors.sendV(30)
                            print('VELOCIDAD:     30')
                        elif bw >= 45 and bw < 65:
                            self.motors.sendV(15)
                            print('VELOCIDAD:     15')
                        elif bw >= 65:
                            self.stop = True
                            self.motors.sendV(0)
                            print('VELOCIDAD:     0')
                        else:
                            self.motors.sendV(70)
                            print('VELOCIDAD:     70')
                    else:       
                        self.motors.sendV(0)
                        print('VELOCIDAD:     0')                        
                    
                else:
                    self.motors.sendV(70)
                    print('VELOCIDAD:     70')
          
        print('DETECTION:            ', self.detection)
        print('STOP:            ', self.stop)
        
        
        if self.detection == True and self.stop == True:
            # Center image
            img_detection = self.cameraC.getImage()
            # RGB model change to GRAY
            img_gray = cv2.cvtColor(img_detection, cv2.COLOR_RGB2GRAY)
            # Segmentation
            img_filtered = cv2.inRange(img_gray, 166, 167)
            cv2.imshow('img', img_filtered)
            
            # Colums and rows
            # Shape gives us the number of rows and columns of an image
            rows = img_gray.shape[0]
            columns = img_gray.shape[1]
            print columns, rows
            
            
            # RGB model change to HSV
            hsv_image = cv2.cvtColor(img_detection, cv2.COLOR_RGB2HSV)

            # Values
            value_min_HSV = np.array([0, 0, 165])
            value_max_HSV = np.array([2, 2, 168])

            # Segmentation
            image_filtered = cv2.inRange(hsv_image, value_min_HSV, value_max_HSV)
            cv2.imshow("filtered", image_filtered)
