import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
from math import pi as pi
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
        
        self.framePrev = None
        
        self.sleep = False
        
        self.detection = False
        self.stop = False
        self.detectionCar = True
        self.turn = False
        
        self.yaw = 0
        self.numFrames = 0
        self.time = 0
        
        self.FRAMES = 10
        
        # 0 to grayscale
        self.template = cv2.imread('resources/template.png',0)

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


    def setImageFiltered(self, image):
        self.lock.acquire()
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
        
        
    def brake (self, bw):
        if self.detection == True:
            if self.stop == False:
                if bw >= 10 and bw < 30:
                    v = 50
                elif bw >= 30 and bw < 45:
                    v = 30
                elif bw >= 45 and bw < 65:
                    v = 15
                elif bw >= 65:
                    self.stop = True
                    v = 0
                else:
                    v = 60
            else:       
                v = 0        
        else:
            v = 60
        print('VELOCIDAD: ', v)
        return v

    
    def saveFrame(self, image):
        self.numFrames += 1
        if self.numFrames == self.FRAMES:
            self.framePrev = image
            self.numFrames = 0
    
    
    def findCar(self, cont, image):
        if len(cont) != 0:
            # We traverse all contours
            for c in cont:
                # We obtain the bounds of the contour, the larger rectangle that encloses the contour
                (x, y, w, h) = cv2.boundingRect(c)
                 # We draw the rectangle of bounds
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.detectionCar = True
                

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
                  
                  
                # STOPPING
                
                v = self.brake(bw)
                self.motors.sendV(v)
                
                
                '''  
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
                    print('VELOCIDAD:     70')'''
          
        print('DETECTION:            ', self.detection)
        print('STOP:            ', self.stop)
        
        
        
        # CAR DETECTION
        
        if self.stop == True and self.turn == False:
            
            # Stop for a while before seeing if cars come
            if self.sleep == False:
                self.sleep = True
                time.sleep(2)
  
            
            # Getting the images
            imageL = self.cameraL.getImage()
            imageR = self.cameraR.getImage()
            
            # Converting to grayscale
            imageL_gray = cv2.cvtColor(imageL, cv2.COLOR_BGR2GRAY)
            
            # We apply smoothing to eliminate noise
            imageL_gray = cv2.GaussianBlur(imageL_gray, (21, 21), 0)
            
            # If we have not yet obtained the background, we obtain it
            # It will be the first frame we get
            if self.framePrev is None:
                self.framePrev = imageL_gray 
                
            # Calculating the difference between the background and the current frame
            image_diff = cv2.absdiff(self.framePrev, imageL_gray)
            #cv2.imshow("image_diff", image_diff)
            
            # I save the image every 5 frames
            self.saveFrame(imageL_gray)
            '''
            self.numFrames += 1
            if self.numFrames == self.FRAMES:
                self.framePrev = imageL_gray
                self.numFrames = 0
            '''
            
            
            # We apply a threshold
            image_seg = cv2.threshold(image_diff, 25, 255, cv2.THRESH_BINARY)[1]
            #cv2.imshow("image_seg", image_seg)
            
            # Dilatamos the image to cover holes
            image_dil = cv2.dilate(image_seg, None, iterations=2)
            #cv2.imshow("image_dil", image_dil)
            
            # Copy the image to detect the contours
            contornosimg = image_dil.copy()
            
            # We look for contours in the image
            im, cont, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            
            self.findCar(cont, imageL)
            '''
            if len(cont) != 0:
                # We traverse all contours
                for c in cont:
                    # We obtain the bounds of the contour, the larger rectangle that encloses the contour
                    (x, y, w, h) = cv2.boundingRect(c)
                    # We draw the rectangle of bounds
                    cv2.rectangle(imageL, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    self.detectionCar = True'''
       
        
        
        
        if self.detectionCar == False:
            self.turn = True
            
            yaw = self.pose3d.getYaw() * 180/pi
            # Turn 45 degrees
            while yaw < -145:
                self.motors.sendV(10)
                self.motors.sendW(3.5)
                yaw = self.pose3d.getYaw() * 180/pi
            
                    
            # Center image
            img_detection = self.cameraC.getImage()
            
            # RGB model change to HSV
            hsv_image = cv2.cvtColor(img_detection, cv2.COLOR_RGB2HSV)
            
            # Values
            value_min_HSV = np.array([0, 5, 0])
            value_max_HSV = np.array([10, 20, 60])

            # Segmentation
            image_filtered = cv2.inRange(hsv_image, value_min_HSV, value_max_HSV)
            cv2.imshow("filtered no kernel", image_filtered)
            # Close, morphology element
            kernel = np.ones((18,18), np.uint8)
            image_filtered = cv2.morphologyEx(image_filtered, cv2.MORPH_CLOSE, kernel)
            
            cv2.imshow("filtered", image_filtered)
            
            # Colums and rows
            # Shape gives us the number of rows and columns of an image
            rows = img_detection.shape[0]
            columns = img_detection.shape[1]
            print columns, rows
            
            # Initialize variables
            position_pixel_left = 0
            position_pixel_right = 0
            
            # We look for the pixels in white
            for i in range(0, columns-1):
                if i == 0:
                    value = image_filtered[300, i+1] - image_filtered[300, i]
                else:
                    value = image_filtered[300, i] - image_filtered[300, i-1]
                if(value != 0):
                    if (value == 255):
                        position_pixel_left = i
                    else:
                        position_pixel_right = i - 1
                        
            if position_pixel_left != 0 or position_pixel_right != 0:    
                # Calculating the intermediate position of the road
                position_middle_road = (position_pixel_left + position_pixel_right) / 2
                # Calculating the intermediate position of the lane
                position_middle_lane = (position_middle_road + position_pixel_right) / 2
                
                cv2.rectangle(input_image, (300,position_middle_lane), (300 + 1, position_middle_lane + 1), (0,255,0), 2)
                
                
                # Calculating the desviation
                desviation = position_middle_lane - (columns/2)
                print (" desviation    ", desviation)
            
                # Speed
                if abs(desviation) < 35:
                    # Go straight
                    self.motors.sendV(50)
                    self.motors.sendW(0)
                elif abs(desviation) >= 35:
                    self.motors.sendW(-desviation*0.05)
                    self.motors.sendV(15)
                    
                    
        if self.stop == True:
            timeNow = time.time()
            if self.time == 0:
                self.time = time.time()
                
            if timeNow - self.time >= 5:
                self.time = 0
                self.detectionCar = False
