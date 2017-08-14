import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
import cv2
from math import pi as pi

time_cycle = 80


class MyAlgorithm(threading.Thread):

    def __init__(self, pose3d, laser1, laser2, laser3, motors):
        self.pose3d = pose3d
        self.laser1 = laser1
        self.laser2 = laser2
        self.laser3 = laser3
        self.motors = motors
        
        self.StopTaxi = False
        self.goForward = False
        self.turn1 = False
        
        self.startTime = 0
        self.startTimePark = 2
        
        self.DIST_REAR_SPOT = 6.3
        self.DIST_REAR_CARY = 4.2
        self.DIST_REAR_CARX = 2.2
        self.DIST_RIGHT = 3.5
        self.MARGIN1 = 0.2
        self.MARGIN2 = 0.15
        self.YAW_MAX = 1.05
        self.YAW_MARGIN = 0.02
        self.DIST_MAX = 20

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


    def get_laser_vector(self,laser_array):
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

    def absolutas2relativas(self, x, y, rx, ry, rt):
        # Convert to relatives
        dx = x - rx
        dy = y - ry

        # Rotate with current angle
        x = dx*math.cos(-rt) - dy*math.sin(-rt)
        y = dx*math.sin(-rt) + dy*math.cos(-rt)

        return x,y
        
        
    def driveArc(self, speed, angleTurn):
        self.motors.sendV(speed)
        self.motors.sendW(angleTurn)
            
         
    def execute(self):

        # TODO

        # Get the position of the robot
        xCar = self.pose3d.getX()
        yCar = self.pose3d.getY()
        
        # We get the orientation of the robot with respect to the map
        yawCar = self.pose3d.getYaw()

        # Get the data of the laser sensor, which consists of 180 pairs of values
        laser_data_Front = self.laser1.getLaserData()
        laserFront = self.parse_laser_data(laser_data_Front)
        
        laser_data_Rear = self.laser2.getLaserData()
        laserRear = self.parse_laser_data(laser_data_Rear)
        
        laser_data_Right = self.laser3.getLaserData()
        laserRight = self.parse_laser_data(laser_data_Right)
              
        laserFront_vectorized = self.get_laser_vector(laserFront)
        laserRear_vectorized = self.get_laser_vector(laserRear)
        laserRight_vectorized = self.get_laser_vector(laserRight)
        
        # Average of the 180 values of the laser
        laserFront_mean = np.mean(laserFront_vectorized, axis=0)
        laserRear_mean = np.mean(laserRear_vectorized, axis=0)
        laserRight_mean = np.mean(laserRight_vectorized, axis=0)
        
        if self.StopTaxi == False:
            if(self.DIST_RIGHT-self.MARGIN1)<=abs(laserRight_mean[1])<=(self.DIST_RIGHT+self.MARGIN1) and (self.DIST_REAR_SPOT-self.MARGIN1)<=abs(laserRear_mean[1])<=(self.DIST_REAR_SPOT+self.MARGIN1):
                # If the taxi is alligned with the car in front of the parking spot the taxi stops
                self.motors.sendV(0)
                self.StopTaxi = True
                if self.startTime == 0:
                    self.startTime = time.time()
            else:
                # If the taxi did not get to the car ahead, the taxi drives forward
                self.motors.sendV(20)
        else:
            if (time.time() - self.startTime) <= self.startTimePark:
                # The taxi stopped for a while
                self.motors.sendV(0)
            else:
                if self.goForward == False:
                    # The taxi goes backward
                    if yawCar <= self.YAW_MAX and self.turn1 == False:
                        # The car is getting into the parking space
                        self.driveArc(-3, pi/4)
                    else:
                        # The taxi straightens
                        self.turn1 = True
                        self.driveArc(-3, -pi/7)
                    
                    if (self.DIST_REAR_CARY-self.MARGIN2) <= abs(laserRear_mean[1]) <= (self.DIST_REAR_CARY+self.MARGIN2):
                        # If the taxi is very close to the car from behind, it stop
                        self.goForward = True
                        self.motors.sendV(0)
                        self.motors.sendW(0)
                else:
                    if yawCar <= -self.YAW_MARGIN or yawCar >= self.YAW_MARGIN:
                        # The taxi rectifies
                        self.driveArc(1, -pi/2)
                    else:
                        # When the car is straight, it stops and rectifies until it is centered in the parking spot
                        self.motors.sendW(0)
                        if (laser_data_Front.distanceData[90]/10 - laser_data_Rear.distanceData[90]/10) > self.DIST_MAX:
                            self.motors.sendV(2)
                        elif (laser_data_Rear.distanceData[90]/10 - laser_data_Front.distanceData[90]/10) > self.DIST_MAX:
                            self.motors.sendV(-2)
                        else:
                            # The taxi is parked
                            print('CAR PARKED')
                            self.motors.sendV(0)

