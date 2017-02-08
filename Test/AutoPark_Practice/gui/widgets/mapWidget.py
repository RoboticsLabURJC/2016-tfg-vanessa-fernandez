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
#       Irene Lope Rodríguez<irene.lope236@gmail.com>
#       Vanessa Fernández Matínez<vanessa_1895@msn.com>


#import resources_rc
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtCore import QPoint, QPointF, pyqtSignal, Qt
import numpy as np
import math

class MapWidget(QWidget):

    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(MapWidget, self).__init__()
        self.winParent=winParent
        self.initUI()
        self.scale = 15.0
        self.laser1 = []
        self.laser2 = []
        self.laser3 = []
        
    def initUI(self):
        layout=QGridLayout() 
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.resize(300,300)
        self.setMinimumSize(500,300)
        
    def paintEvent(self, e):
        _width = self.width()
        _height = self.height()
    
        painter=QPainter(self)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
    
        #Widget center
        painter.translate(QPoint(_width/2, _height/2))

        # Draw laser
        colorLaser1 = Qt.blue
        colorLaser2 = Qt.green
        colorLaser3 = Qt.red
        self.drawLaser(1, painter, colorLaser1, self.laser1)
        self.drawLaser(2, painter, colorLaser2, self.laser2)
        self.drawLaser(3, painter, colorLaser3,  self.laser3)

        # Draw car
        self.drawCar(painter)

        # Draw axis
        pi = math.pi
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        RT1 = np.matrix([[0],[0],[0],[1]])
        RT2 = np.matrix([[200],[0],[0],[1]])
        RT3 = np.matrix([[0],[200],[0],[1]])
        
        RT4 = RTx  * RTz * RT1
        RT5 = RTx  * RTz * RT2
        RT6 = RTx  * RTz * RT3
        
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(RT4.flat[0],RT4.flat[1]),QPointF(RT5.flat[0],RT5.flat[1]))
        pen = QPen(Qt.green, 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(RT4.flat[0],RT4.flat[1]),QPointF(RT6.flat[0],RT6.flat[1]))

    def drawCar(self, painter):
        carsize = 50

        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        # Chassis
        painter.fillRect(-carsize/2, -carsize,carsize,2*carsize,Qt.yellow)

        # Tires
        painter.fillRect(-carsize/2,-carsize,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,-carsize,-carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(-carsize/2,carsize-2*carsize/5,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,carsize-2*carsize/5,-carsize/5,2*carsize/5,Qt.black)
              
    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT   

    def RTLaser(self, num):
        pi = math.pi
        if num == 1:
            #Rotación en Z / Traslación en X
            RT = self.RTz(0, 2.79, 0, 0)
        elif num == 2:
            #Rotación en Z / Traslación en X
            RT = self.RTz(pi, -2.79, 0, 0)
        else:
            #Rotación en Z / Traslación en Y
            RT = self.RTz(pi/2, 0, 1.5, 0)
        return RT    
    
    def coordLaser(self, dist, angle):
        coord = [0,0] 
        coord[0] = dist * math.cos(angle)
        coord[1] = dist * math.sin(angle)
        return coord     

    def drawLaser(self, num, painter, color, laser):
        pi = math.pi
        pen = QPen(color, 2)
        painter.setPen(pen)
        RT = self.RTLaser(num)
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        RTOrigLaser = np.matrix([[0],[0],[0],[1]]) * self.scale
        RTFinalLaser1 = RT * RTOrigLaser
        RTFinalLaser = RTx * RTz * RTFinalLaser1
        for d in laser:
            dist = d[0]
            angle = d[1]
            coord = self.coordLaser(dist,angle)
            orig_poses = np.matrix([[coord[0]], [coord[1]], [1], [1]]) * self.scale
            final_poses1 = RT * orig_poses
            final_poses = RTx * RTz * final_poses1
            painter.drawLine(QPointF(RTFinalLaser.flat[0],RTFinalLaser.flat[1]),QPointF(final_poses.flat[0], final_poses.flat[1]))

    def setLaserValues(self, num, laser):
        # Init laser array
        if num == 1:
            laserX = self.laser1
        elif num == 2:
            laserX = self.laser2
        else:
            laserX = self.laser3
                
        if len(laserX) == 0:
            for i in range(laser.numLaser):
                laserX.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = -math.pi/2 + math.radians(i)
            laserX[i] = (dist, angle)
            
            
class MapWidget1(QWidget):

    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(MapWidget1, self).__init__()
        self.winParent=winParent
        self.initUI()
        self.scale = 19.0
        self.laser1 = []
        self.laser2 = []
        self.laser3 = []
        
    def initUI(self):
        layout=QGridLayout() 
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.resize(300,300)
        self.setMinimumSize(500,300)
        
    def paintEvent(self, e):
        _width = self.width()
        _height = self.height()
    
        painter=QPainter(self)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
    
        #Widget center
        painter.translate(QPoint(_width/2, _height/2))

        # Draw laser
        colorLaser1 = Qt.blue
        colorLaser2 = Qt.green
        colorLaser3 = Qt.red
        self.drawLaser(1, painter, colorLaser1, self.laser1)
        self.drawLaser(2, painter, colorLaser2, self.laser2)
        self.drawLaser(3, painter, colorLaser3,  self.laser3)

        # Draw car
        self.drawCar(painter)

        # Draw axis
        pi = math.pi
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        RT1 = np.matrix([[0],[0],[0],[1]])
        RT2 = np.matrix([[200],[0],[0],[1]])
        RT3 = np.matrix([[0],[200],[0],[1]])
        
        RT4 = RTx  * RTz * RT1
        RT5 = RTx  * RTz * RT2
        RT6 = RTx  * RTz * RT3
        
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(RT4.flat[0],RT4.flat[1]),QPointF(RT5.flat[0],RT5.flat[1]))
        pen = QPen(Qt.green, 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(RT4.flat[0],RT4.flat[1]),QPointF(RT6.flat[0],RT6.flat[1]))

    def drawCar(self, painter):
        carsize = 50

        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        # Chassis
        painter.fillRect(-carsize/2, -carsize,carsize,2*carsize,Qt.yellow)

        # Tires
        painter.fillRect(-carsize/2,-carsize,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,-carsize,-carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(-carsize/2,carsize-2*carsize/5,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,carsize-2*carsize/5,-carsize/5,2*carsize/5,Qt.black)
              
    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT   

    def RTLaser(self, num):
        pi = math.pi
        if num == 1:
            #Rotación en Z / Traslación en X
            RT = self.RTz(0, 2.79, 0, 0)
        elif num == 2:
            #Rotación en Z / Traslación en X
            RT = self.RTz(pi, -2.79, 0, 0)
        else:
            #Rotación en Z / Traslación en Y
            RT = self.RTz(pi/2, 0, 1.5, 0)
        return RT    
    
    def coordLaser(self, dist, angle):
        coord = [0,0] 
        coord[0] = dist * math.cos(angle)
        coord[1] = dist * math.sin(angle)
        return coord     

    def drawLaser(self, num, painter, color, laser):
        pi = math.pi
        pen = QPen(color, 2)
        painter.setPen(pen)
        RT = self.RTLaser(num)
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        RTOrigLaser = np.matrix([[0],[0],[0],[1]]) * self.scale
        RTFinalLaser1 = RT * RTOrigLaser
        RTFinalLaser = RTx * RTz * RTFinalLaser1
        for d in laser:
            dist = d[0]
            angle = d[1]
            coord = self.coordLaser(dist,angle)
            orig_poses = np.matrix([[coord[0]], [coord[1]], [1], [1]]) * self.scale
            final_poses1 = RT * orig_poses
            final_poses = RTx * RTz * final_poses1
            painter.drawLine(QPointF(RTFinalLaser.flat[0],RTFinalLaser.flat[1]),QPointF(final_poses.flat[0], final_poses.flat[1]))

    def setLaserValues(self, num, laser):
        # Init laser array
        if num == 1:
            laserX = self.laser1
        elif num == 2:
            laserX = self.laser2
        else:
            laserX = self.laser3
                
        if len(laserX) == 0:
            for i in range(laser.numLaser):
                laserX.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = -math.pi/2 + math.radians(i)
            laserX[i] = (dist, angle)
