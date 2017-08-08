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
        self.framePrevL = None
        self.framePrevR = None
        
        self.sleep = False
        self.detection = False
        self.stop = False
        self.turn = False
        self.turn45 = False
        
        self.yaw = 0
        self.numFramesL = 0
        self.numFramesR = 0
        self.time = 0
        
        self.detectionCar = 100 
        self.FRAMES = 10
        self.MAX_DESV = 15
        self.MAX_DETECTION = 100
        self.THRESHOLD_DET = 70
        self.MIN_DET = 2
        self.ADD_DET = 20
        self.ROW = 300
        
        self.turnTo = ''
        
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

    def stopAlgorithm (self):
        self.motors.sendV(0)
        self.motors.sendW(0)
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()
        
        
    def filterHSV(self, input_image, Hmin, Hmax, Smin, Smax, Vmin, Vmax, size_Kernel):
        # RGB model change to HSV
        hsv_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2HSV)

        # Values of red
        value_min_HSV = np.array([Hmin, Smin, Vmin])
        value_max_HSV = np.array([Hmax, Smax, Vmax])

        # Segmentation
        image_filtered = cv2.inRange(hsv_image, value_min_HSV, value_max_HSV)

        # Close, morphology element
        kernel = np.ones((size_Kernel,size_Kernel), np.uint8)
        image_filtered = cv2.morphologyEx(image_filtered, cv2.MORPH_CLOSE, kernel)
        
        return image_filtered
        
        
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
            print('Going foward..')
        print('VELOCIDAD: ', v)
        return v

    
    def saveFrame(self, image, frame, numFrames):
        numFrames += 1
        if numFrames == self.FRAMES:
            frame = image
            numFrames = 0
        return frame, numFrames
    
    
    def findCar(self, cont, image):
        if len(cont) != 0:
            # We traverse all contours
            for c in cont:
                # We obtain the bounds of the contour, the larger rectangle that encloses the contour
                (x, y, w, h) = cv2.boundingRect(c)
                 # We draw the rectangle of bounds
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if self.detectionCar < self.MAX_DETECTION:
                    self.detectionCar += self.ADD_DET
                    
                    
    def subImages(self, image, framePrev, numFrames):
        # Converting to grayscale
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # We apply smoothing to eliminate noise
        image_gray = cv2.GaussianBlur(image_gray, (21, 21), 0)
        
        # If we have not yet obtained the background, we obtain it
        # It will be the first frame we get
        if framePrev is None:
            framePrev = image_gray 
            
        # Calculating the difference between the background and the current frame
        image_diff = cv2.absdiff(framePrev, image_gray)
        
        # I save the image every 5 frames
        framePrev, numFrames = self.saveFrame(image_gray, framePrev, numFrames)
                
        # We apply a threshold
        image_seg = cv2.threshold(image_diff, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilatamos the image to cover holes
        image_dil = cv2.dilate(image_seg, None, iterations=2)
        
        # Copy the image to detect the contours
        contornosimg = image_dil.copy()
        
        # We look for contours in the image
        im, cont, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        self.findCar(cont, image)
        
        return framePrev, numFrames
        
    
    def checkDetectionCar(self):
        if self.detectionCar >= self.MIN_DET:
            self.detectionCar -= self.MIN_DET
            

    def findRoad(self, image):

        # Shape gives us the number of rows and columns of an image
        columns = image.shape[1]
        
        # Initialize variables
        border_left = 0
        border_right = 0
        
        # Recorre las columnas de la imagen y la fila 300
        for i in range(0, columns-1):   
            # We look for the pixels in white                
            if i == 0:
                # If the pixel is the first
                value = image[300, i+1] - image[300, i] 
            else:
                value = image[300, i] - image[300, i-1]
                
            if(value != 0):
                # If there are changes of color
                if (value == 255):
                    # Left border (change to black)
                    border_left = i
                else:
                    # Right border (change to white)
                    border_right = i - 1
                    
        return border_left, border_right  
        
        
    def controlDesviation(self, desv, direction):
        if abs(desv) < self.MAX_DESV:
            # Go straight
            self.motors.sendV(50)
            self.motors.sendW(0)
        else:
            # Turn
            if direction == 'left':
                if desv < 0:
                    self.motors.sendW(3.5)
                else:
                    self.motors.sendW(-3.5)
            else:
                if desv < 0:
                    self.motors.sendW(4)
                else:
                    self.motors.sendW(-4)
            self.motors.sendV(30)
         
            
    def mean(self, a, b):
        m = (a + b)/2
        return m
        
        
    def findMidLane(self, border_left, border_right, columns):
        middle_lane = 0
        if border_left != 0 or border_right != 0:    
            # Calculating the intermediate position of the road
            middle_road = self.mean(border_left, border_right)
            # Calculating the intermediate position of the lane
            middle_lane = self.mean(middle_road, border_right)
            
        return middle_lane
                    
    
    def turn45degrees(self, yaw, direction):
        if self.turn45 == False:
            if yaw < 180 and yaw > 100:
                if direction == 'left':
                    print('Girando 45...')
                    self.motors.sendV(30)
                    self.motors.sendW(3.5)
                else:
                    print('Girando -45...')
                    self.motors.sendV(30)
                    self.motors.sendW(-5.6)
                    print('yaw: ', yaw)
            else:
                self.turn45 = True
                
 
    def chooseDirection(self):
        # Random int number between [0,2) --> 0 o 1
        randm = np.random.randint(2)
        if randm == 1:
            return 'left'
        else:
            return 'right'
                

    def execute(self):
        
        # TODO
        print ('execute')
       
        # GETTING THE IMAGES
        input_image = self.cameraC.getImage()

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.motors.setV(10)
        #self.motors.setW(5)
        
        # RGB model change to HSV
        image_filtered = self.filterHSV(input_image, 131, 179, 71, 232, 0, 63, 11)

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

          
        print('DETECTION:            ', self.detection)
        print('STOP:            ', self.stop)
        
        
        
        # CAR DETECTION
        
        if self.stop == True and self.turn == False:
            
            # Getting the images
            imageL = self.cameraL.getImage()
            imageR = self.cameraR.getImage()
            
            # Substraction of images
            self.framePrevL, self.numFramesL = self.subImages(imageL, self.framePrevL, self.numFramesL)
            self.framePrevR, self.numFramesR = self.subImages(imageR, self.framePrevR, self.numFramesR)
            
            # Check detection
            self.checkDetectionCar()
            print('DETECTION CAR: ', self.detectionCar)
        
        
        
        if self.detectionCar <= self.THRESHOLD_DET:
            # GO
        
            self.turn = True
            
            # Choose the direction of the rotation
            if self.turnTo == '':
                self.turnTo = self.chooseDirection()
            self.turnTo = 'right'
            print ('Turn to: ', self.turnTo)    
            
            # Turn 45 degrees
            yaw = abs(self.pose3d.getYaw() * 180/pi)
            self.turn45degrees(yaw, self.turnTo)
            
            
            if self.turn45:
                # ROAD DETECTION
                 
                # Center image
                imageC = self.cameraC.getImage()
                
                # RGB model change to HSV
                image_filtered = self.filterHSV(imageC, 0, 10, 5, 20, 0, 60, 18)
                #cv2.imshow("filtered", image_filtered)
                
                # Find the position of the road
                border_left, border_right = self.findRoad(image_filtered)
                
                # Shape gives the size of image
                columns = imageC.shape[1]
                
                # TURN LEFT
                middle_lane = self.findMidLane(border_left, border_right, columns)
                if middle_lane != 0:
                    #cv2.rectangle(imageC, (self.ROW, middle_lane), (self.ROW + 1, middle_lane + 1), (0,255,0), 2)
                    cv2.rectangle(imageC, (middle_lane, self.ROW), ( middle_lane + 1,self.ROW + 1), (0,255,0), 2)
                    # Calculating the desviation
                    desviation = middle_lane - (columns/2)
                    print('desv', desviation)
                    # Speed
                    self.controlDesviation(desviation, self.turnTo)
