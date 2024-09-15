import serial
import csv
import time


print("Iniciando programa de lectura de datos del puerto serial")

try:
    serialPort = serial.Serial('/dev/cu.usbmodemF412FA6BEE402', 9600)
    time.sleep(2)

    print("Conectado al puerto serial")

    with open('datosArduino.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Lectura', 'Valor adc', 'Voltaje'])
        print("Archivo CSV creado y listo para escribir")

        try:
            while True:
                if serialPort.in_waiting > 0:
                    line = serialPort.readline().decode('utf-8').strip()
                    print(f"Datos recibidos: {line}")
                    
                    data = line.split(',')
                    

                    writer.writerow(data)
                    print(f"Datos escritos al archivo: {data}")

        except KeyboardInterrupt:
            print("Programa terminado")

    serialPort.close()
    print("Puerto serial cerrado")

except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
