import threading
import time
from datetime import datetime

import math
import jderobot
from Beacon import Beacon

from parallelIce.cameraClient import CameraClient
from parallelIce.navDataClient import NavDataClient
from parallelIce.cmdvel import CMDVel
from parallelIce.extra import Extra
from parallelIce.pose3dClient import Pose3DClient

time_cycle = 80

class MyAlgorithm(threading.Thread):

    class pid(object):
        def __init__(self, kp, kd, ki):
            # Constant of PID control
            self.kp = kp
            self.kd = kd
            self.ki = ki
            self.error = 0
            self.acumulate_error = 0

        def calculateU(self, e):
            proportional = self.kp * e
            derivate = self.kd * (e - self.error)
            self.acumulate_error = self.acumulate_error + e
            integral = self.ki*(self.acumulate_error)
            u =  -(proportional) -(derivate) -(integral)
            self.error = e
            return u
            

    def __init__(self, camera, navdata, pose, cmdvel, extra):
        self.camera = camera
        self.navdata = navdata
        self.pose = pose
        self.cmdvel = cmdvel
        self.extra = extra

        self.beacons=[]
        self.initBeacons()
        self.minError=0.01

        # Constructor PID
        self.pidX = self.pid(0.655,0.000112,0.00029)
        self.pidY = self.pid(0.655,0.000112,0.00029)

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

    def initBeacons(self):
        self.beacons.append(Beacon('baliza1',jderobot.Pose3DData(0,5,0,0,0,0,0,0),False,False))
        self.beacons.append(Beacon('baliza2',jderobot.Pose3DData(5,0,0,0,0,0,0,0),False,False))
        self.beacons.append(Beacon('baliza3',jderobot.Pose3DData(0,-5,0,0,0,0,0,0),False,False))
        self.beacons.append(Beacon('baliza4',jderobot.Pose3DData(-5,0,0,0,0,0,0,0),False,False))
        self.beacons.append(Beacon('baliza5',jderobot.Pose3DData(10,0,0,0,0,0,0,0),False,False))
        self.beacons.append(Beacon('inicio',jderobot.Pose3DData(0,0,0,0,0,0,0,0),False,False))

    def getNextBeacon(self):
        for beacon in self.beacons:
            if beacon.isReached() == False:
                return beacon

        return None

    def run (self):

        self.stop_event.clear()

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
        # Add your code here

        # Opcional despegar el drone hasta ver una baliza e ir hasta la baliza mas proxima
        # hacer control pid de x e y

        # Getting actual beacon
        actualBeacon = self.getNextBeacon()

        if actualBeacon != None:

            # Coordinates of target
            posX_target = actualBeacon.getPose().x
            posY_target = actualBeacon.getPose().y

            # Calculating the error (position of target minus position of drone)
            errorx = posX_target - self.pose.getPose3D().x
            errory = posY_target - self.pose.getPose3D().y

            # Controlador PID
            controladorX = self.pidX.calculateU(errorx)
            controladorY = self.pidY.calculateU(errory)

            print("error", errorx, errory)
            print(controladorX, controladorY)

            # Correct position
            if abs(controladorX) > self.minError:
                self.cmdvel.setVX(-controladorX)

            if abs(controladorY) > self.minError:
                self.cmdvel.setVY(-controladorY)

            # If the margin is minimum, then we have got the target
            if (abs(controladorX) <= self.minError) and (abs(controladorY) <= self.minError):
                # We have got the target.
                actualBeacon.setReached(True)
                # The acumulate error is zero
                self.pidX.acumulate_error = 0
                self.pidY.acumulate_error = 0
            else:
                # Send speed 
                self.cmdvel.sendVelocities()

        else:
            # If the drone has visited all targets, then the drone stop
            self.cmdvel.sendCMDVel(0,0,0,0,0,0)
        pass
