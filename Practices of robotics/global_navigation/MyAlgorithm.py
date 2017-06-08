from sensors import sensor
import numpy as np
import cv2
import math
import threading
import time
from datetime import datetime
from matplotlib import pyplot as plt

time_cycle = 80

class MyAlgorithm(threading.Thread):

    def __init__(self, grid, sensor, vel):
        self.sensor = sensor
        self.grid = grid
        self.vel = vel
        self.posObstaclesBorder = []
        self.targets = []
        self.rejilla = np.zeros((400, 400),np.uint8)
        sensor.getPathSig.connect(self.generatePath)

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


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

    def findStopExpansion(self, dest, posRobot, margin, i, j, fin):
        # Cases of the margins
        if ((dest[0] <= posRobot[0]) and (dest[1] <= posRobot[1])):
            if((i > (posRobot[0] + margin)) and (j > (posRobot[1] + margin))):
                fin = "true"
        elif ((dest[0] >= posRobot[0]) and (dest[1] <= posRobot[1])):
            if((i < (posRobot[0] - margin)) and (j > (posRobot[1] + margin))):
                fin = "true"
        elif ((dest[0] >= posRobot[0]) and (dest[1] >= posRobot[1])):
            if((i < (posRobot[0] - margin)) and (j < (posRobot[1] - margin))):
                fin = "true"
        elif ((dest[0] <= posRobot[0]) and (dest[1] >= posRobot[1])):
            if((i > (posRobot[0] + margin)) and (j < (posRobot[1] - margin))):
                fin = "true"
        return fin


    def incorporateNode(self, pos0, pos1, nodos):
        found = False
        for i in range(0, len(nodos)):
            if self.grid.getVal(pos0, pos1) == self.grid.getVal(nodos[i][0][0], nodos[i][0][1]):
                nodos[i].append([pos0, pos1])
                found = True
        if found == False:
            nodos.append([[pos0, pos1]])
        return nodos


    def incorporatePosObstacle(self, pos0, pos1):
        found = False
        for i in range(0, len(self.posObstaclesBorder)):
            if (self.posObstaclesBorder[i][0] == pos0) and (self.posObstaclesBorder[i][1]) == pos1:
                found = True
        if (found == False):
            self.posObstaclesBorder.append([pos0, pos1])


    def penaltiesObstacles(self, i, j, dest0, dest1, destino):
        # Penaltie's Obstacles
        penaltie =  0
        penaltieMax = 130
        for c in range(1, 5):
            if ((((i == (dest0-c)) or (i == (dest0+c)) and (dest1-c <= j <= dest1+c)) or (((j == (dest1-c)) or (j == (dest1+c))) and (dest0-c-1 <= i <= dest0+c-1)))):
                penaltie = penaltieMax - c * 10
        if (penaltie > self.rejilla[j][i] and (i != destino[0] or j != destino[1])):
            self.rejilla[j][i] = penaltie


    def checkPositionPath(self, arrayPath, i, j):
        found = "false"
        for x in range(0, len(arrayPath)):
            if (arrayPath[x][0] == i) and (arrayPath[x][1] == j):
                found = "true"

        return found

    def getTargetWorld(self, posRobot):
        found = False
        mapIm = self.grid.getMap()
        valMin = 2000000000000
        for i in range(posRobot[0]-8, posRobot[0]+9):
            for j in range(posRobot[1]-8, posRobot[1]+9):
                if ((((i==(posRobot[0]-8)) or (i==(posRobot[0]+8)) and (posRobot[1]-8<=j<=posRobot[1]+8)) or (((j==(posRobot[1]-8)) or (j==(posRobot[1]+8))) and (posRobot[0]-7<=i<=posRobot[0]+7)))):
                    val = self.grid.getVal(i, j)
                    if (found == False and mapIm[j, i] == 255):
                        found = True
                        valMin = val
                        target = [i, j]
                    else:
                        if(val < valMin and mapIm[j, i] == 255):
                            target = [i, j]
                            valMin = val
        return target

    def absolutas2relativas(self, x, y, rx, ry, rt):
        # Convert to relatives
        dx = x - rx
        dy = y - ry

        # Rotate with current angle
        x = dx*math.cos(-rt) - dy*math.sin(-rt)
        y = dx*math.sin(-rt) + dy*math.cos(-rt)

        return x,y



    """ Write in this method the code necessary for looking for the shorter
        path to the desired destiny.
        The destiny is chosen in the GUI, making double click in the map.
        This method will be call when you press the Generate Path button. 
        Call to grid.setPath(path) mathod for setting the path. """
    def generatePath(self):

        print("LOOKING FOR SHORTER PATH")
        # mapIm is the image of the map
        mapIm = self.grid.getMap()
        # dest is the selected destination, and is a tuple such that (x, y)  
        dest = self.grid.getDestiny()
        # griPose is the position on the map, (x, y)
        gridPos = self.grid.getPose()

        #TODO

        # Position of the robot
        world_robotX = self.sensor.getRobotX()
        world_robotY = self.sensor.getRobotY()
        posRobot = self.grid.worldToGrid(world_robotX, world_robotY)

        # We need some variables in the loop while
        fin = "false"
        margin = 20
        #fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        #out = cv2.VideoWriter('Expansion_Penalizacion.avi', fourcc, 30, (400, 400),False)

        # Evaluating the value of the field on position (dest[0], dest[1])
        if (mapIm[dest[1]][dest[0]] == 255):
            self.grid.setVal(dest[0], dest[1], 0.0)
            nodo = [[dest[0], dest[1]]]


        imagen = np.zeros((400, 400),np.uint8)
        x=1
        o=1

        # New nodes
        nodos = []

        # Expansion of the field
        while (fin == "false"):
            for i in range(0, len(nodo)):
                if ((mapIm[nodo[i][1], nodo[i][0]] == 255) and nodo[i][0] >= 0 and nodo[i][0] < mapIm.shape[0] and nodo[i][1] >= 0 and nodo[i][1] < mapIm.shape[1]):
                    # Wave fronts of each node
                    frente1 = [[nodo[i][0]-1, nodo[i][1]], [nodo[i][0], nodo[i][1]-1], [nodo[i][0]+1, nodo[i][1]], [nodo[i][0], nodo[i][1]+1]]
                    frente2 = [[nodo[i][0]-1, nodo[i][1]-1], [nodo[i][0]+1, nodo[i][1]-1], [nodo[i][0]+1, nodo[i][1]+1], [nodo[i][0]-1, nodo[i][1]+1]]
                    val_init = self.grid.getVal(nodo[i][0], nodo[i][1])
                    for j in range(0, len(frente1)):
                        if (frente1[j][1] >= 0) and (frente1[j][1] < 400) and (frente1[j][0] >= 0) and (frente1[j][0] < 400):
                            if mapIm[frente1[j][1], frente1[j][0]] == 255:
                                val = self.grid.getVal(frente1[j][0], frente1[j][1])
                                if ((math.isnan(val)) or ((val_init + 1.0) < val) or (val <= 0)):
                                    if frente1[j][0] != dest[0] or frente1[j][1] != dest[1]:
                                        self.grid.setVal(frente1[j][0], frente1[j][1], val_init+1.0)
                                        nodos = self.incorporateNode(frente1[j][0], frente1[j][1], nodos)
                            else:
                                self.incorporatePosObstacle(frente1[j][0], frente1[j][1])
                            #imagen[frente1[j][1]][frente1[j][0]] = self.grid.getVal(frente1[j][0], frente1[j][1])
                            #if (x/o) == 100:
                            #    out.write((imagen))
                            #    o = o + 1
                    for j in range(0, len(frente2)):
                        if (frente2[j][1] >= 0) and (frente2[j][1] <400) and (frente2[j][0] >= 0) and (frente2[j][0] < 400):
                            if mapIm[frente2[j][1], frente2[j][0]] == 255:
                                val = self.grid.getVal(frente2[j][0], frente2[j][1])
                                if ((math.isnan(val)) or ((val_init + math.sqrt(2.0)) < val) or (val <= 0)):
                                    if frente2[j][0] != dest[0] or frente2[j][1] != dest[1]:
                                        self.grid.setVal(frente2[j][0], frente2[j][1], val_init+math.sqrt(2.0))
                                        nodos = self.incorporateNode(frente2[j][0], frente2[j][1], nodos)
                            #imagen[frente2[j][1]][frente2[j][0]] = self.grid.getVal(frente2[j][0], frente2[j][1])
                            #if (x/o) == 100:
                            #    out.write((imagen))
                            #    o = o + 1
                # Cases of the margins
                fin = self.findStopExpansion(dest, posRobot, margin, nodo[i][0], nodo[i][1], fin)
                #x = x + 1
            if (nodos != []):
                nodo = nodos[0]
                nodos.pop(0)
        #out.release()


        # Obstacles penalties
        for i in range(0, len(self.posObstaclesBorder)):
            for k in range(self.posObstaclesBorder[i][0]-4, self.posObstaclesBorder[i][0]+5):
                for l in range(self.posObstaclesBorder[i][1]-4, self.posObstaclesBorder[i][1]+5):
                    if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
                        if (mapIm[l][k] == 255):
                            self.penaltiesObstacles(k, l, self.posObstaclesBorder[i][0], self.posObstaclesBorder[i][1], dest)
                    #imagen[l][k] = self.grid.getVal(k, l)
                    #if (x/o) == 100:
                    #    out.write((imagen))
                    #    o = o+1
            #x=x+1
        #out.release()

        self.grid.grid = self.rejilla+self.grid.grid



        # Find the path
        pixelCentral = [posRobot[0], posRobot[1]]
        valMin = self.grid.getVal(posRobot[0], posRobot[1])
        posMin = pixelCentral
        self.grid.setPathVal(posRobot[0], posRobot[1], valMin)
        found = "false"
        posPath= []

        while (found == "false"):
            foundNeighbour = "false"
            for i in range(pixelCentral[0]-1, pixelCentral[0]+2):
                for j in range(pixelCentral[1]-1, pixelCentral[1]+2):
                    if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400) and (mapIm[j][i] !=0)):
                        val = self.grid.getVal(i, j)
                        posFound = self.checkPositionPath(posPath, i, j)
                        if (foundNeighbour == "false" and posFound == "false"):
                            foundNeighbour = "true"
                            valNeighbour = val
                        if posFound == "false":
                            if ((val < valMin) and (val >=  0.0)):
                                if (((val == 0.0) and (i == dest[0]) and (j == dest[1])) or (val > 0.0)):
                                    valMin = val
                                    posMin = [i, j]
                            elif val <= valNeighbour:
                                valMin = val
                                valNeighbour = val
                                posMin = [i, j]

                        #print("posactual",i, j, "posMin", posMin,"dest", dest, "posicion central", pixelCentral)
                        #print("valMin", valMin, "val pos actual", val, "val dest", self.grid.getVal(dest[0], dest[1]))
            self.grid.setPathVal(posMin[0], posMin[1], valMin)
            pixelCentral = posMin
            posPath.append(posMin)
            if ((valMin == 0.0) and (posMin[0] == dest[0]) and (posMin[1] == dest[1])):
                found = "true"
                self.grid.setPathFinded()


        # Represent the Gradient Field in a window using cv2.imshow
        self.grid.showGrid()



    """ Write in this mehtod the code necessary for going to the desired place,
        once you have generated the shorter path.
        This method will be periodically called after you press the GO! button. """
    def execute(self):
        # Add your code here
        print("GOING TO DESTINATION")

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.vel.setV(10)
        #self.vel.setW(5)
        #self.vel.sendVelocities()

        # Position of the robot
        posRobotX = self.sensor.getRobotX()
        posRobotY = self.sensor.getRobotY()
        orientationRobot = self.sensor.getRobotTheta()

        # Destination
        dest = self.grid.getDestiny()
        destWorld = self.grid.gridToWorld(dest[0], dest[1])

        print("robot",posRobotX, posRobotY, orientationRobot)
        print(dest, destWorld)

        posRobotImage = self.grid.worldToGrid(posRobotX, posRobotY)


        if (abs(posRobotX)<(abs(destWorld[0])+3) and abs(posRobotX)>(abs(destWorld[0])-3)) and (abs(posRobotY)<(abs(destWorld[1])+3) and abs(posRobotY)>(abs(destWorld[1])-3)):
            self.vel.setV(0)
            self.vel.setW(0)
            print("DESTINATION")
        else:
            targetImage = self.getTargetWorld(posRobotImage)
            target = self.grid.gridToWorld(targetImage[0], targetImage[1])
            self.grid.settpoint(targetImage[0], targetImage[1])

            # Convert target[0] y target[1] to relative coordinates
            directionx,directiony = self.absolutas2relativas(target[0],target[1],posRobotX,posRobotY,orientationRobot)

            print("direction", directionx, directiony)
            angle = math.atan((directionx/directiony))
            print("angle",angle)

            # Correct position
            if directiony > 0:
                self.vel.setW(angle*24.5)
            elif abs(angle) >= 0.7:
                self.vel.setW(-angle*35.5)
            elif abs(angle) > 0.5 and abs(angle) <=  0.7:
                #self.vel.setW(-angle*12.5)
                self.vel.setW(-angle*30.5)
            else:
                #self.vel.setW(-angle*6.5)
                self.vel.setW(-angle*31.5)

            if abs(angle) >= 0.65:
                speed = 0
            elif abs(angle) > 0.5 and abs(angle) <= 0.65:
                speed = 3
            elif abs(angle) > 0.3 and abs(angle) <= 0.5:
                speed = 8
            else:
                speed = 100


            if directiony > 0:
                speed = 0
      
            print('speed', speed)
            self.vel.setV(speed)

