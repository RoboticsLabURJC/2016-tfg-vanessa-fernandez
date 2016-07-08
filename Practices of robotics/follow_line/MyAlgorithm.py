from sensors import sensor
import numpy as np
import threading
import cv2


class MyAlgorithm():

    def __init__(self, sensor):
        self.sensor = sensor
        self.imageRight=None
        self.imageLeft=None
        self.lock = threading.Lock()



    def execute(self):
        #GETTING THE IMAGES
        imageLeft = self.sensor.getImageLeft()
        imageRight = self.sensor.getImageRight()


        # Add your code here
        print "Runing"

        # Cambiamos de modelo RGB a HSV
        imageRight_HSV = cv2.cvtColor(imageRight, cv2.COLOR_RGB2HSV)
        imageLeft_HSV = cv2.cvtColor(imageLeft, cv2.COLOR_RGB2HSV)

        # Minimo y maximo valores del rojo
        value_min_HSV = np.array([0, 235, 60])
        value_max_HSV = np.array([180, 255, 255])

        # Filtramos las imagenes
        imageRight_HSV_filtered = cv2.inRange(imageRight_HSV, value_min_HSV, value_max_HSV)
        imageLeft_HSV_filtered = cv2.inRange(imageLeft_HSV, value_min_HSV, value_max_HSV)


        #Crear una mascara con solo los pixeles dentro del rango de rojos
        imageRight_HSV_filtered_Mask = np.dstack((imageRight_HSV_filtered, imageRight_HSV_filtered, imageRight_HSV_filtered))
        imageLeft_HSV_filtered_Mask = np.dstack((imageLeft_HSV_filtered, imageLeft_HSV_filtered, imageLeft_HSV_filtered))


        # Con shape miramos el numero de filas y columnas de una imagen
        tamano = imageLeft.shape
        filas = tamano[0]
        columnas = tamano[1]


        # Busqueda de pixeles que cambian de tono
        position_pixel_left = []
        position_pixel_right  = []

        for i in range(0, columnas-1):
            value = imageLeft_HSV_filtered[365, i] - imageLeft_HSV_filtered[365, i-1]
            if(value != 0):
                if (value == 255):
                    position_pixel_left.append(i)
                else:
                    position_pixel_right.append(i-1)


        # Calculo de la posicion intermedia de la carretera
        if ((len(position_pixel_left) != 0) and (len(position_pixel_right) != 0)):
            position_middle = (position_pixel_left[0] + position_pixel_right[0]) / 2
        elif ((len(position_pixel_left) != 0) and (len(position_pixel_right) == 0)):
            position_middle = (position_pixel_left[0] + columnas) / 2
        elif ((len(position_pixel_left) == 0) and (len(position_pixel_right) != 0)):
            position_middle = (0 + position_pixel_right[0]) / 2
        else:
            position_pixel_right.append(1000)
            position_pixel_left.append(1000)
            position_middle = (position_pixel_left[0] + position_pixel_right[0])/ 2


        # Calculo de la desviacion
        desviation = position_middle - (columnas/2)
        print " desviation    ", desviation

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS

        if (desviation == 0):
             self.sensor.setV(10)
        elif (position_pixel_right[0] == 1000):
             self.sensor.setW(-0.0000035)
        elif ((abs(desviation)) < 85):
             if ((abs(desviation)) < 15):
                 self.sensor.setV(6)
             else:
                 self.sensor.setV(3.5)
             self.sensor.setW(-0.000045 * desviation)
        elif ((abs(desviation)) < 150):
             if ((abs(desviation)) < 120):
                 self.sensor.setV(1.8)
             else:
                 self.sensor.setV(1.5)
             self.sensor.setW(-0.00045 * desviation)
        else:
             self.sensor.setV(1.5)
             self.sensor.setW(-0.005 * desviation)



        #SHOW THE FILTERED IMAGE ON THE GUI
        self.setRightImageFiltered(imageRight_HSV_filtered_Mask)
        self.setLeftImageFiltered(imageLeft_HSV_filtered_Mask)



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

