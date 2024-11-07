import serial
import csv
import time
import datetime
import sys
print("Iniciando programa de lectura de datos del puerto serial")


sistema = sys.platform
puerto = ""
if sistema == "darwin":
    puerto = "/dev/cu.usbmodemF412FA6BEE402"
elif sistema == "win32":
    puerto = "COM5"


try:
    serialPort = serial.Serial(port=puerto, baudrate=9600)
    time.sleep(2)

    print("Conectado al puerto serial")

    with open('datosArduino.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Año", "Mes", "Día", "Hora", "Minuto", "Segundo", "Dato"])
        print("Archivo CSV creado y listo para escribir")

        try:
            while True:
                if serialPort.in_waiting > 0:
                    line = serialPort.readline().decode('utf-8').strip()
                    print(f"Datos recibidos: {line}")
                    
                    data = datetime.datetime.now().strftime("%Y,%m,%d,%H,%M,%S")
                    data_list = data.split(",")
                    data_list.append(line)
                    print(data_list)

                    writer.writerow(data_list)

        except KeyboardInterrupt:
            print("Programa terminado")

    serialPort.close()
    print("Puerto serial cerrado")

except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")