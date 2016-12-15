import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
from Target import Target
from Parser import Parser

time_cycle = 80


def absolutas2relativas(x, y, rx, ry, rt):
    # Convert to relatives
    dx = x - rx
    dy = y - ry

    # Rotate with current angle
    x = dx*math.cos(-rt) - dy*math.sin(-rt)
    y = dx*math.sin(-rt) + dy*math.cos(-rt)

    return x,y


def parse_laser_data(laser_data):
    laser = []
    for i in range(laser_data.numLaser):
        dist = laser_data.distanceData[i]/1000.0
        angle = math.radians(i)
        laser += [(dist, angle)]
    return laser



class MyAlgorithm(threading.Thread):

    def __init__(self, cameraL, cameraR, pose3d, laser, motors):
        self.cameraL = cameraL
        self.cameraR = cameraR
        self.pose3d = pose3d
        self.laser = laser
        self.motors = motors

        self.imageRight=None
        self.imageLeft=None

        # Car direction
        self.carx = 0.0
        self.cary = 0.0

        # Obstacles direction
        self.obsx = 0.0
        self.obsy = 0.0

        # Average direction
        self.avgx = 0.0
        self.avgy = 0.0

        # Current target
        self.targetx = 0.0
        self.targety = 0.0

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

        # Init targets
        parser = Parser('targets.json')
        self.targets = parser.getTargets()

    def getNextTarget(self):
        for target in self.targets:
            if target.isReached() == False:
                return target

        return None

    def setRightImageFiltered(self, image):
        self.lock.acquire()
        self.imageRight=image
        self.lock.release()


    def setLeftImageFiltered(self, image):
        self.lock.acquire()
        self.imageLeft=image
        self.lock.release()

    def getRightImageFiltered(self):
        self.lock.acquire()
        tempImage=self.imageRight
        self.lock.release()
        return tempImage

    def getLeftImageFiltered(self):
        self.lock.acquire()
        tempImage=self.imageLeft
        self.lock.release()
        return tempImage

    def getCarDirection(self):
        return (self.carx, self.cary)

    def getObstaclesDirection(self):
        return (self.obsx, self.obsy)

    def getAverageDirection(self):
        return (self.avgx, self.avgy)

    def getCurrentTarget(self):
        return (self.targetx, self.targety)

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
        self.currentTarget=self.getNextTarget()
        self.targetx = self.currentTarget.getPose().x
        self.targety = self.currentTarget.getPose().y

        # TODO
        # Get the position of the robot
        rx = self.pose3d.getX()
        ry = self.pose3d.getY()


        # We marked the subgoals as we go through
        if(abs(ry)<(abs(self.targety)+1) and abs(ry)>(abs(self.targety)-1)):
            self.currentTarget.setReached(True)

        # We get the orientation of the robot with respect to the map
        rt = self.pose3d.getYaw()


        # Get the data of the laser sensor, which consists of 180 pairs of values
        laser_data = self.laser.getLaserData()
        laser = parse_laser_data(laser_data)
        # Convert self.targetx y self.targety to relative coordinates
        self.carx,self.cary=absolutas2relativas(self.targetx,self.targety,rx,ry,rt)

        # Laser       
        laser_vectorized = []
        for d,a in laser:
            # (4.2.1) laser into GUI reference system
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1
            v = (x,y)
            laser_vectorized += [v]

        # Average of the 180 values of the laser
        laser_mean = np.mean(laser_vectorized, axis=0)


        # Repulsor vector
        dist_threshold = 6
        vff_repulsor_list = []
        for d,a in laser:
            # (4.2.1) laser into GUI reference system
            if(d < dist_threshold):
                x = (d - dist_threshold) * math.cos(a) * -1
                y = (d - dist_threshold) * math.sin(a) * -1
                v = (x,y)
                vff_repulsor_list += [v]

        vff_repulsor = np.mean(vff_repulsor_list, axis=0)


        self.obsx,self.obsy = vff_repulsor

        # Calculating repulsor vector module
        mod_repulsor = pow(pow(self.obsx,2) + pow(self.obsy,2),0.5)
        if (mod_repulsor > 1.55):
            self.obsx,self.obsy = vff_repulsor * 4.5


        # Calculating the coordinates of the resultant vector
        self.avgx = self.carx + self.obsx
        self.avgy = self.cary + self.obsy


        # Calculating the module of the speed
        speed = pow(pow(self.avgx,2) + pow(self.avgy,2),0.5)

        # Correction
        if (abs(self.obsx) > 2):
            if (abs(self.obsx) < abs(self.carx)):
                if (self.obsx >= 0):
                    self.avgx = abs(self.avgx)
                else:
                    self.avgx = -abs(self.avgx)


        if ((self.obsx == (-self.carx)) and (self.obsy == (-self.cary))):
            self.avgx = self.obsx
            self.avgy = self.cary


        # Calculating angle
        if (speed < 1):
            # Use the tangent to avoid indeterminacy
            angle = math.atan(abs(self.avgx/self.avgy))
        else:
            angle = math.asin(abs(self.avgx/speed))
        if(self.avgy > 0):
            angle = math.pi - angle


        # Linear speed
        if ((speed < 1) or (speed > 3)):
            self.motors.sendV(3)
        else:
            self.motors.sendV(speed)

        # Angular speed
        if(self.avgx < 0):
            self.motors.sendW(-angle * 0.75)
        else:
            self.motors.sendW(angle * 0.75)

