import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
import cv2
from math import pi as pi
import random

time_cycle = 80
        

class MyAlgorithm(threading.Thread):

    def __init__(self, pose3d, motors, laser, bumper):
        self.pose3d = pose3d
        self.motors = motors
        self.laser = laser
        self.bumper = bumper

        self.radiusInitial = 0.1
        self.constant = 0.01
        self.numCrash = 0
        self.turn = False
        self.yaw = 0
        self.crash = False
        self.numAngle = 0
        self.sign = 0
        
        self.MARGIN = 0.2

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

    
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
        
        
    
    def checkCrash(self):
        for i in range(0, 350):
            # Returns 1 if it collides, and 0 if it doesn't collide
            crash = self.bumper.getBumperData().state
            if crash == 1:
                self.motors.sendW(0)
                self.motors.sendV(0)
                break
        return crash
        
    def stopVacuum(self):
        self.motors.sendW(0)
        self.motors.sendV(0)
        
    def convert2PiTo0(self, angle):
        if angle == 2*pi:
            angle = 0
        return angle
        
    def turnAngle(self, angle):
        if angle <= (self.numAngle-self.MARGIN) or angle >= (self.numAngle+self.MARGIN):
            self.motors.sendV(0)
            if self.sign == 1:
                self.motors.sendW(0.2)
            else:
                self.motors.sendW(-0.2)
        else:
            self.turn = True
        

    def execute(self):

        print ('Execute')
        # TODO
        
        # Check crash
        crash = self.checkCrash()

        if crash == 1:
            # When there has already been a crash we change the value of self.numCrash to start doing the bump & go
            self.numCrash = 1

        print(crash)
        
        if self.numCrash == 0:
            # If self.numCrash equals 0, then we make the spiral
            self.motors.sendW(0.5)
            self.motors.sendV(self.radiusInitial*self.constant)
            self.constant += 0.012
        else:
            if crash == 1:
                # Stop
                self.stopVacuum()
                time.sleep(1)
                # Go backwards
                self.motors.sendV(-0.2)
                time.sleep(1)
                
                self.crash = True
                self.yaw = self.pose3d.getYaw()
                # Random angle and sign
                self.numAngle = random.uniform(pi/3, pi)
                self.sign = random.randint(0, 1)
                
            elif self.turn == False and self.crash == True:
                # Rotate the self.numAngle
                
                # yawNow is the orientation that I have at the moment
                yawNow = self.pose3d.getYaw()
                
                # Conversion of angles                
                self.yaw = self.convert2PiTo0(self.yaw)
                yawNow = self.convert2PiTo0(yawNow)
                
                if (-pi < self.yaw < -pi/2) or (-pi < yawNow < -pi/2):
                    if (-pi < self.yaw < -pi/2) and ((pi/2 <= yawNow <= pi) or (0 <= yawNow <= pi/2)) :
                        self.yaw = self.yaw + 2*pi
                    elif (-pi < yawNow < -pi/2) and ((pi/2 <= self.yaw <= pi) or (0 <= self.yaw <= pi/2)):
                        yawNow = yawNow + 2*pi
                        
                # Calculate the difference between angles and do the turn        
                angle = abs(self.yaw - yawNow)
                self.turnAngle(angle)
            
            else:            
                # Go forward
                self.motors.sendW(0)
                time.sleep(1)
                self.motors.sendV(0.5)
                
                # Restart global variables
                self.crash = False
                self.turn = False

