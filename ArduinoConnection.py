import serial
import os
import threading
import time
from getmac import get_mac_address as gma

threadLock = threading.Lock()
comandos = {"posix": {'puertoSerie': '/dev/ttyUSB0'},
            "nt": {'puertoSerie': 'COM3'}}


class ArduinoConnection(threading.Thread):

    __instance = None
    arduino = None

    @staticmethod
    def get_instance():
        if ArduinoConnection.__instance == None:

            threadLock.acquire()  # Asi se evita que dos hilos accedan simultameamente

            """Se comprueba de nuevo si instance es nula, ya que si entran dos hilos
            A la vez, uno de ellos podria haberla inicializado ya antes del actual"""

            if ArduinoConnection.__instance == None:
                ArduinoConnection()

            threadLock.release()  # Se notifica que se acabo el bloqueo

        return ArduinoConnection.__instance

    def __init__(self):
        threading.Thread.__init__(self)

        # Lanza una excepcion si instance no es None
        if ArduinoConnection.__instance != None:
            raise Exception("Es una clase singleton")
        else:
            self.arduino = serial.Serial(
                comandos[os.name]["puertoSerie"], 9600, timeout=5)
            self.arduino.readline()  # Vacia el buffer completamente

            ArduinoConnection.__instance = self

    def getDataArduino(self):
        userID = gma()

        threadLock.acquire()
        try:

            self.arduino.flushInput()
            self.arduino.flushOutput()

        except serial.SerialException:
            return None, None

        self.arduino.write(b'enviame')

        self.arduino.flush()

        self.arduino.readline()  # Elimina la palabra enviada anteriormente

        datos = self.arduino.readline()  # Recibe los datos reales

        threadLock.release()
        return userID, datos

    def sendDataArduino(self, orden):

        threadLock.acquire()

        self.arduino.write(orden.encode())
        self.arduino.flush()

        # Elimina los datos del buffer y la palabra enviada anteriormente
        self.arduino.readline()

        confirmacion = self.arduino.readline().decode(
            "utf-8").replace('\r\n', '')  # Recibe la confirmacion de recepcion

        threadLock.release()

        if confirmacion == "OK":
            return "OK-Orden realizada"
        elif confirmacion == "No":
            return "No existe la orden: <" + orden + ">"
        else:
            return "Error desconocido"
