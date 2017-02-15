#!/usr/bin/python3
#
#  Copyright (C) 1997-2016 JDE Developers Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#  Authors :
#       Eduardo Perdices <eperdices@gsyc.es>
#       Aitor Martinez Fernandez <aitor.martinez.fernandez@gmail.com>
#

import sys
#from PyQt5.QtWidgets import QApplication
#from gui.GUI import MainWindow
#from gui.threadGUI import ThreadGUI
from parallelIce.pose3dClient import Pose3DClient
import easyiceconfig as EasyIce
import math
from math import pi as pi



if __name__ == "__main__":
    ic = EasyIce.initialize(sys.argv)
    pose3d = Pose3DClient(ic, "Autopark.Pose3D", True)

    #app = QApplication(sys.argv)
    #myGUI = MainWindow()
    #myGUI.setMotors(motors)
    #myGUI.setPose3D(pose3d)
    #myGUI.setLaser1(laser1)
    #myGUI.setLaser2(laser2)
    #myGUI.setLaser3(laser3)
    #myGUI.setAlgorithm(algorithm)
    #myGUI.show()

    idealAngle = 0

    while True:
        pose = pose3d.getPose3D()
        x = pose3d.getX()
        y = pose3d.getY()
        yaw = pose3d.getYaw()

        print('Pose 3D (Referee): x: ', x, ' y: ', y, ' yaw: ', yaw)

        if yaw <= 20*pi/180 and yaw >= -20*pi/180:
            print("verde")
        elif yaw > 20*pi/180 and yaw <= 40*pi/180 or yaw < -20*pi/180 and yaw >= -40*pi/180:
            print("amarillo")
        elif yaw > 40*pi/180 and yaw <= 60*pi/180 or yaw < -40*pi/180 and yaw >= -60*pi/180:
            print("naranja")
        else:
            print("rojo")

    #t2 = ThreadGUI(myGUI)
    #t2.daemon=True
    #t2.start()


    #sys.exit(app.exec_())
