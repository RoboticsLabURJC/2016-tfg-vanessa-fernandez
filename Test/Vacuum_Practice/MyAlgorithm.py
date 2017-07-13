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
        time.sleep(1)
        

    def execute(self):

        print ('Execute')
        # TODO
        
        # Check crash
        crash = self.checkCrash()

        if crash == 1:
            self.numCrash = 1

        print(crash)
        self.yaw = self.pose3d.getYaw()
        
        if self.numCrash == 0:
            # If self.numCrash equals 0, then we make the spiral
            self.motors.sendW(0.5)
            self.motors.sendV(self.radiusInitial*self.constant)
            self.constant += 0.012
        else:
            if crash == 1:
                # Stop
                self.stopVacuum()
                # Go backwards
                self.motors.sendV(-0.2)
                time.sleep(1)
                
                # Random angle and sign
                numAngle = random.uniform(pi/3, pi)
                signo = random.randint(0, 1)
                
                while self.turn == False:
                    yawNow = self.pose3d.getYaw()
                                            
                    if self.yaw == 2*pi:
                        self.yaw = 0
                    if yawNow == 2*pi:
                        yawNow = 0
                    
                    if (-pi < self.yaw < -pi/2) or (-pi < yawNow < -pi/2):
                        if (-pi < self.yaw < -pi/2) and ((pi/2 <= yawNow <= pi) or (0 <= yawNow <= pi/2)) :
                            self.yaw = self.yaw + 2*pi
                        elif (-pi < yawNow < -pi/2) and ((pi/2 <= self.yaw <= pi) or (0 <= self.yaw <= pi/2)):
                            yawNow = yawNow + 2*pi
                            
                    angle = abs(self.yaw - yawNow)
                    if angle <= (numAngle-self.MARGIN) or angle >= (numAngle+self.MARGIN):
                        self.motors.sendV(0)
                        if signo == 1:
                            self.motors.sendW(0.2)
                        else:
                            self.motors.sendW(-0.2)
                    else:
                        self.turn = True
                        
            # Go forward
            self.motors.sendW(0)
            time.sleep(1)
            self.turn = False
            self.motors.sendV(0.5)

