import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
import cv2

time_cycle = 80


class MyAlgorithm(threading.Thread):

    #def __init__(self, cameraL, cameraR, pose3d, laser, motors):
    def __init__(self, pose3d, laser1, laser2, laser3, motors):
        #self.cameraL = cameraL
        #self.cameraR = cameraR
        self.pose3d = pose3d
        self.laser1 = laser1
        self.laser2 = laser2
        self.laser3 = laser3
        self.motors = motors
        #self.grid = np.empty([300, 300], float)

        #self.imageRight=None
        #self.imageLeft=None

        # Car direction
        self.carx = 0.0
        self.cary = 0.0

        # Obstacles direction
      #  self.obsx = 0.0
      #  self.obsy = 0.0

        # Average direction
      #  self.avgx = 0.0
      #  self.avgy = 0.0

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


    def getCarDirection(self):
        return (self.carx, self.cary)

    #def getObstaclesDirection(self):
    #    return (self.obsx, self.obsy)

    #def getAverageDirection(self):
    #    return (self.avgx, self.avgy)


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
            # (4.2.1) laser into GUI reference system
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1
            v = (x,y)
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
        laser_data1 = self.laser1.getLaserData()
        laser1_array = self.parse_laser_data(laser_data1)
        laser1_vect = self.laser_vector(laser1_array)

        #for x,y in laser1_vect:
        #    for i in range(0, 300):
        #        for j in range(0, 300):
        #           self.grid[int(x[0])][int(x[1])] = 255

        #for x in range(self.grid):
        #    for y in range(self.grid):
        #        self.grid[x][y] = 255
       # cv2.imshow("grid", self.grid)        
