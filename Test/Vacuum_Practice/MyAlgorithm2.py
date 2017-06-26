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
        

class MyAlgorithm2(threading.Thread):

    def __init__(self, pose3d, motors, laser, bumper):
        self.pose3d = pose3d
        self.motors = motors
        self.laser = laser
        self.bumper = bumper
        
        self.map = cv2.imread("resources/images/mapgrannyannie.png", cv2.IMREAD_GRAYSCALE)
        self.map = cv2.resize(self.map, (500, 500))
        
        self.numCrash = 0

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

    def execute(self):

        print ('Execute')
        # TODO
        # Map is self.map
        #cv2.imshow('map',self.map)
        
        # Pose's vacuum
        x = self.pose3d.getX()
        y = self.pose3d.getY()
        yaw = self.pose3d.getYaw()
        
        for i in range(0, 350):
            # Devuelve 1 si choca y 0 si no choca
            crash = self.bumper.getBumperData().state
            if crash == 1:
                self.motors.sendW(0)
                self.motors.sendV(0)
                break
                
        print(crash)
        
        turn = False
        
        if crash == 1:
            self.numCrash = self.numCrash + 1
            
            self.motors.sendW(0)
            self.motors.sendV(0)
            time.sleep(1)
            self.motors.sendV(-0.1)
            time.sleep(1)
            
            while turn == False:
                yawNow = self.pose3d.getYaw()

                if self.numCrash % 2 != 0 and (yawNow <= (pi/2-0.115) or yawNow >= (pi/2+0.115)):
                    self.motors.sendV(0)
                    self.motors.sendW(0.2)
                elif self.numCrash % 2 == 0 and (yawNow <= (pi/2-0.115) or yawNow >= (pi/2+0.115)):
                    self.motors.sendV(0)
                    self.motors.sendW(-0.2)
                    
                else:
                    self.motors.sendW(0)
                    time.sleep(2)
                    self.motors.sendV(0.38)
                    time.sleep(1)
                    yaw = self.pose3d.getYaw()
                    while turn == False:
                        yawNow = self.pose3d.getYaw()
                        
                        if self.numCrash % 2 != 0 and (yawNow <= (pi-0.115) or yawNow >= (pi+0.115)):
                            self.motors.sendV(0)
                            self.motors.sendW(0.2)
                        elif self.numCrash % 2 == 0 and (yawNow <= (-0.115) or yawNow >= (+0.115)):
                            self.motors.sendV(0)
                            self.motors.sendW(-0.2)
                        else:
                            turn = True
        else:
            self.motors.sendW(0.0)
            time.sleep(1)
            self.motors.sendV(0.5)
        
        
