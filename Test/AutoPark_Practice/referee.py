import sys, math
from math import pi as pi
import numpy as np
import cv2
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt5.QtGui import (QBrush, QConicalGradient, QLinearGradient, QPainter, QPainterPath, QPalette, QPen, QPixmap, QPolygon, QRadialGradient, QColor, QTransform, QPolygonF, QKeySequence, QIcon)
from PyQt5.QtWidgets import (QApplication, QProgressBar, QCheckBox, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSpinBox, QWidget, QPushButton, QSpacerItem, QSizePolicy, QLCDNumber )
from PyQt5 import QtGui, QtCore
from parallelIce.pose3dClient import Pose3DClient
import easyiceconfig as EasyIce
from gui.threadGUI import ThreadGUI

class MainWindow(QWidget):

    updGUI=pyqtSignal()
    def __init__(self, pose3d, parent=None):
        super(MainWindow, self).__init__(parent)
        
        layout = QGridLayout()
        self.quesito = quesoWidget(self, pose3d)
        self.tiempo = tiempoWidget(self)
        self.calidad = calidadWidget(self)
        self.distancia = distanciaWidget(self, pose3d)
        self.nota = notaWidget(self,pose3d)
        self.logo = logoWidget(self)
        layout.addWidget(self.quesito,1,0)
        layout.addWidget(self.tiempo,0,0)
        layout.addWidget(self.distancia,0,2)
        layout.addWidget(self.calidad,1,2)
        layout.addWidget(self.nota,0,1)
        layout.addWidget(self.logo,2,2)
    
        vSpacer = QSpacerItem(30, 50, QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout.addItem(vSpacer,1,0)
        
        self.setFixedSize(740,640);

        self.setLayout(layout)
        self.updGUI.connect(self.update)

    def update(self):
        self.quesito.updateG()
        self.distancia.updateG()
        self.nota.updateG()

class logoWidget(QWidget):
    def __init__(self, winParent):
        super(logoWidget, self).__init__()
        self.winParent=winParent
        self.logo = cv2.imread("resources/logo_jderobot1.png",cv2.IMREAD_UNCHANGED)
        self.logo = cv2.resize(self.logo, (100, 100))
        image = QtGui.QImage(self.logo.data, self.logo.shape[1], self.logo.shape[0],  QtGui.QImage.Format_ARGB32);
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.height = self.pixmap.height()
        self.width = self.pixmap.width()
        self.mapWidget = QLabel(self)
        self.mapWidget.setPixmap(self.pixmap)
        self.mapWidget.resize(self.width, self.height)
        self.setMinimumSize(100,100)
        
class calidadWidget(QWidget):
    def __init__(self,winParent):    
        super(calidadWidget, self).__init__()
        self.winParent=winParent

        vLayout = QVBoxLayout()
        choquesLabel = QLabel("Choques:")
        bar = QProgressBar()
        bar.setValue(50)
        st = "QProgressBar::chunk {background-color: #ff0000;}\n QProgressBar {border: 1px solid grey;border-radius: 2px;text-align: center;background: #eeeeee;}"
        bar.setStyleSheet(st)
        bar.setTextVisible(False)
        vLayout.addWidget(choquesLabel, 0)
        vLayout.addWidget(bar, 0)

        vSpacer = QSpacerItem(30, 80, QSizePolicy.Ignored, QSizePolicy.Ignored)
        vLayout.addItem(vSpacer)

        self.setLayout(vLayout)



class distanciaWidget(QWidget):
    def __init__(self,winParent, pose3d):    
        super(distanciaWidget, self).__init__()
        self.winParent=winParent
        self.pose3d = pose3d
        self.distFrontFinal = 0
        self.distRearFinal = 0
        self.distanceSidewalk = 0

        vLayout = QVBoxLayout()

        self.distances()

        distancesLabel = QLabel("Distancias:")
        self.distanceFrontalLabel = QLabel("Distancia frontal: " + str(round(self.distFrontFinal, 3)) + ' m')
        self.distanceRearLabel = QLabel("Distancia trasera: " + str(round(self.distRearFinal, 3)) + ' m')
        self.distanceSidewalkLabel = QLabel("Distancia a la acera: " + str(round(self.distanceSidewalk, 3)) + ' m')
        vLayout.addWidget(distancesLabel, 0)
        vLayout.addWidget(self.distanceFrontalLabel, 0)
        vLayout.addWidget(self.distanceRearLabel, 0)
        vLayout.addWidget(self.distanceSidewalkLabel, 0)

        self.setLayout(vLayout)

    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT

    def RTCar(self):
        yaw = self.pose3d.getYaw()
        RTz = self.RTz(yaw, 0, 0, 0)
        return RTz


    def distancePoint2Rect(self, ax, ay, bx, by, cx, cy):
        distance = abs((bx - ax)*(cy - ay) - (by - ay)*(cx - ax)) / (math.sqrt(pow((bx-ax),2) + pow((by-ay),2)))
        return distance

    def parameterU(self, ax, ay, bx, by, cx, cy):
        # parameter U of equations: Px = ax + u*(bx-ax); and Py = ay + u*(by-ay)
        u = ((cx - ax)*(bx - ax) + (cy - ay)*(by - ay)) / (pow((bx - ax),2) + pow((by - ay),2))
        return u

    def distancePoint2Point(self, x1, y1, x2, y2):
        return math.sqrt(pow((x2-x1),2) + pow((y2-y1),2))

    def distancePoint2Segment(self, ax, ay, bx, by, cx, cy):
        # Calculate U parameter
        u = self.parameterU(ax, ay, bx, by, cx, cy)
        if u < 0:
            distance = self.distancePoint2Point(ax, ay, cx, cy)
        elif u > 1:
            distance = self.distancePoint2Point(bx, by, cx, cy)
        else:
            distance = self.distancePoint2Rect(ax, ay, bx, by, cx, cy)
        return distance


    def distanceCar2Car(self, pointCarLeft, pointCarRight, pointFrontLeft, pointFrontRight, pointRearLeft, pointRearRight):
        distance = self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointFrontLeft.flat[0], pointFrontLeft.flat[1])

        if (self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointFrontRight.flat[0], pointFrontRight.flat[1]) < distance):
            distance = self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointFrontRight.flat[0], pointFrontRight.flat[1])
        if (self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointRearLeft.flat[0], pointRearLeft.flat[1]) < distance):
            distance = self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointRearLeft.flat[0], pointRearLeft.flat[1])
        if (self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointRearRight.flat[0], pointRearRight.flat[1]) < distance):
            distance = self.distancePoint2Segment(pointCarLeft[0], pointCarLeft[1], pointCarRight[0], pointCarRight[1], pointRearRight.flat[0], pointRearRight.flat[1])

        return distance


    def distances(self):
        carSize = [5.75, 2.5]
        pointCarFrontal_left = [14 - carSize[0]/2, 3+carSize[1]/2]
        pointCarFrontal_right = [14 - carSize[0]/2, 3-carSize[1]/2]
        pointCarRear_left = [0.5 + carSize[0]/2, 3+carSize[1]/2]
        pointCarRear_right = [0.5 + carSize[0]/2, 3-carSize[1]/2]
        positionSideWalk_start = [-25, 3.25]
        positionSideWalk_final = [35, 3.25]

        xFront = self.pose3d.getX() + carSize[0]/2
        xRear = self.pose3d.getX() - carSize[0]/2
        yLeft = self.pose3d.getY() + carSize[1]/2
        yRight = self.pose3d.getY() - carSize[1]/2

        # Car's rotation
        pointFrontLeft = self.RTCar() * np.matrix([[xFront], [yLeft], [1], [1]])
        pointFrontRight = self.RTCar() * np.matrix([[xFront], [yRight], [1], [1]])
        pointRearLeft = self.RTCar() * np.matrix([[xRear], [yLeft], [1], [1]])
        pointRearRight = self.RTCar() * np.matrix([[xRear], [yRight], [1], [1]])
        
        self.distFrontFinal = self.distanceCar2Car(pointCarFrontal_left, pointCarFrontal_right, pointFrontLeft, pointFrontRight, pointRearLeft, pointRearRight)
        self.distRearFinal = self.distanceCar2Car(pointCarRear_left, pointCarRear_right, pointFrontLeft, pointFrontRight, pointRearLeft, pointRearRight)
        self.distanceSidewalk = self.distanceCar2Car(positionSideWalk_start, positionSideWalk_final, pointFrontLeft, pointFrontRight, pointRearLeft, pointRearRight)


    def updateG(self):
        self.distances()
        self.distanceFrontalLabel.setText("Distancia frontal: " + str(round(self.distFrontFinal, 3)) + ' m')
        self.distanceRearLabel.setText("Distancia trasera: " + str(round(self.distRearFinal, 3)) + ' m')
        self.distanceSidewalkLabel.setText("Distancia a la acera: " + str(round(self.distanceSidewalk, 3)) + ' m')
        self.update()      
   
   
        
class notaWidget(QWidget):
    def __init__(self,winParent,pose3d):    
        super(notaWidget, self).__init__()
        self.winParent=winParent
        self.pose3d = pose3d

        hLayout = QHBoxLayout()
        
        notaAngle = self.testAngle() * 0.025
        notaTime = self.testTime() * 0.025
        notaDist = self.testDistance() * 0.025
        notaCol = self.testCollision() * 0.025
        nota = notaAngle + notaTime + notaDist + notaCol
        
        notaLabel = QLabel('Nota final: ' + str(nota))
        hLayout.addWidget(notaLabel, 0) 
        self.setLayout(hLayout) 
        
    def testAngle(self):
        yawRad = self.pose3d.getYaw()
        angle = math.degrees(yawRad) + 90
        if (angle >= 85 and angle <= 105):
            notaAngle = 100
        elif (angle < 85 and angle >= 70 or angle > 105 and angle <= 120):
            notaAngle = 80
        elif (angle < 70 and angle >= 60 or angle > 120 and angle <= 130):
            notaAngle = 50
        else: 
            notaAngle = 0
        return notaAngle
    
    def testTime(self):
        time = tiempoWidget(self)
        myTime = time.seconds
        if myTime <= 30:
            notaTime = 100
        elif myTime > 30 and myTime <= 60:
            notaTime = 80
        elif myTime > 60 and myTime <= 120:
            notaTime = 50
        else:
            notaTime = 0    
        return notaTime
    
    def testDistance(self):
        notaDist = 0
        return notaDist
    
    def testCollision(self):
        notaCol = 0
        return notaCol

    def updateG(self):
        self.update() 
        
             

class tiempoWidget(QWidget):

    time = pyqtSignal()
    def __init__(self,winParent):    
        super(tiempoWidget, self).__init__()
        self.winParent=winParent
        self.seconds = 0
        
        hLayout = QHBoxLayout()
        
        tiempoLabel = QLabel("Tiempo")
        self.lcd = QLCDNumber(self)
        self.lcd.setMaximumSize(100,50)
        hLayout.addWidget(tiempoLabel,0)
        hLayout.addWidget(self.lcd, 1)

        hSpacer = QSpacerItem(300, 30, QSizePolicy.Ignored, QSizePolicy.Ignored)
        hLayout.addItem(hSpacer)

        self.setLayout(hLayout)

        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.printTime)


        # get the palette
        palette = self.lcd.palette()

        # foreground color
        palette.setColor(palette.WindowText, QColor(85, 85, 255))
        # background color
        palette.setColor(palette.Background, QColor(0, 170, 255))
        # "light" border
        palette.setColor(palette.Light, QColor(255, 0, 0))
        # "dark" border
        palette.setColor(palette.Dark, QColor(0, 255, 0))

        # set the palette
        self.lcd.setPalette(palette)

    def printTime(self):
        self.seconds += 1
        self.lcd.display(self.seconds)



class quesoWidget(QWidget):
    
    def __init__(self,winParent, pose3d):    
        super(quesoWidget, self).__init__()
        self.winParent=winParent
        self.rectangle = QRectF(0.0, 0.0, 300.0, 300.0)
        self.pose3d = pose3d       

    def drawRedZones(self, painter):
        self.setStyle(painter, QColor(255,70,70),QColor(255,70,70),1)
        startAngle = 0 * 16
        spanAngle = 45 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)
        startAngle = 135 * 16
        spanAngle = 45 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)
        startAngle = 180 * 16
        spanAngle = 180 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)
        
    def drawOrangeZones(self, painter):
        self.setStyle(painter, QColor(255,220,23),QColor(255,220,23),1)
        startAngle = 45 * 16
        spanAngle = 30 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)
        startAngle = 105 * 16
        spanAngle = 30 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)

    def drawGreenZones(self, painter):
        self.setStyle(painter, QColor(117,240,154),QColor(117,240,154),1)
        startAngle = 75 * 16
        spanAngle = 15 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)
        startAngle = 90 * 16
        spanAngle = 15 * 16
        painter.drawPie(self.rectangle, startAngle, spanAngle)

    def drawArrow(self, painter, angle=90):
        radius = 130
        yawRad = self.pose3d.getYaw()
        angle = -(yawRad + pi/2) # PI/2 para centrar la aguja
        origx = self.rectangle.width() / 2
        origy = self.rectangle.height() / 2
        finx = radius * math.cos(angle) + origx
        finy = radius * math.sin(angle) + origy   
        self.setStyle(painter, Qt.black,Qt.black,3)
        painter.drawLine(QPoint(origx,origy), QPoint(finx,finy))
        painter.drawEllipse(145,145, 10, 10)

    def resetPen(self, painter):
        pen = QPen(Qt.black, 1)
        brush = QBrush()
        painter.setPen(pen)
        painter.setBrush(brush)

    def setStyle(self, painter, fillColor, penColor, stroke):
        brush = QBrush()
        pen = QPen(penColor, stroke)
        brush.setColor(fillColor)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
      
    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawRedZones(painter)
        self.drawOrangeZones(painter)
        self.drawGreenZones(painter)
        self.drawArrow(painter,120)

    def updateG(self):
        self.update()



if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    ic = EasyIce.initialize(sys.argv)
    pose3d = Pose3DClient(ic, "Autopark.Pose3D", True)

    myGUI = MainWindow(pose3d)
    myGUI.show()
    t2 = ThreadGUI(myGUI)
    t2.daemon=True
    t2.start()
    sys.exit(app.exec_())
