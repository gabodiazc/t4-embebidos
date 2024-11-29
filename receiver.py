from struct import pack, unpack
from PyQt5.QtWidgets import *
from typing import List
import time
import serial

# Se configura el puerto y el BAUD_Rate
PORT = 'COM3'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32

# Funciones
def send_message(message):
    """ Funcion para enviar un mensaje a la ESP32 """
    ser.write(message)

def receive_response():
    """ Funcion para recibir un mensaje de la ESP32 """
    response = ser.readline()
    return response

def receive_data():
    """ Funcion que recibe tres floats (fff) de la ESP32 
    y los imprime en consola """
    data = receive_response()
    data = unpack("ffff", data)
    print("Temperature: ", data[0])
    print("Pressure: ", data[1])
    return data

def receive_data_size():
    """ Funcion que recibe tres floats (fff) de la ESP32 
    y los imprime en consola """
    data = receive_response()
    data = unpack("ffff", data)
    return data

def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

def receive_handshake():
    """ Función que recibe un mensaje de la ESP32 y lo imprime en consola """
    # El mensaje que vamos a enviar
    message = pack('6s', 'Okay\0'.encode())

    # Recibir el primer mensaje de la ESP32
    data = receive_response()

    # Decodificar el mensaje recibido para poder hacer la comparación
    data = data.decode('utf-8', errors='ignore').strip()

    # Mantener el ciclo mientras el mensaje no sea 'Okay'
    while data != 'Okay':
        # Enviar el mensaje 'Okay' a la ESP32
        send_message(message)
        
        # Recibir el siguiente mensaje
        data = receive_response()
        
        # Decodificar y limpiar el mensaje
        data = data.decode('utf-8', errors='ignore').strip()
    return


def receive_window_data():
# Se lee data por la conexion serial
    counter = 0
    while True:
        if ser.in_waiting > 0:
            try:
                message = receive_data()
            except:
                #print('Error en leer mensaje')
                continue
            else: 
                counter += 1
                print(counter)
            finally:
                if counter == window_size:
                    print()
                    print("Temperature Rms: ", message[2])
                    print("Pressure Rms: ", message[3])
                    print('Lecturas listas!')
                    print()
                    # Se envia el mensaje de termino de comunicacion
                    send_end_message()
                    break

def receive_window_size():
    global window_size

    print("Recibiendo tamaño de ventana de datos...")
    message = pack('6s','ready\0'.encode())
    send_message(message)

    time.sleep(1)
    counter = 0
    while True:
        if ser.in_waiting > 0:
            try:
                message = receive_data_size()
            except:
                #print('Error en leer mensaje')
                continue
            else: 
                counter += 1
            finally:
                if counter == 1:
                    print()
                    print("Tamaño de ventana de datos almacenado: ", int(message[0]))
                    window_size = int(message[0])
                    # Se envia el mensaje de termino de comunicacion
                    send_end_message()
                    break
    return

def button1click():
    layout.removeWidget(button1)
    layout.removeWidget(button2)
    layout.removeWidget(button3)
    button1.hide()
    button2.hide()
    button3.hide()

    message1 = pack('2s','1\0'.encode())
    send_message(message1)
    time.sleep(1)
    message2 = pack('6s','BEGIN\0'.encode())
    send_message(message2)
    time.sleep(3)
    receive_window_data()
    send_end_message()
    
    layout.addWidget(menubutton)
    menubutton.show()

def button2click():
    layout.removeWidget(button1)
    layout.removeWidget(button2)
    layout.removeWidget(button3)
    button1.hide()
    button2.hide()
    button3.hide()
    layout.addWidget(windowinput)
    windowinput.show()
    layout.addWidget(windowbutton)
    windowbutton.show()
    menubutton.show()

def button2click2():
    global window_size
    message = pack('2s','2\0'.encode())
    send_message(message)
    time.sleep(4)
    new_window_size = int(windowinput.text())
    message2 = pack('4s', str(new_window_size).encode())
    send_message(message2)
    time.sleep(4)
    window_size = new_window_size
    layout.addWidget(menubutton)

def button3click():
    layout.removeWidget(button1)
    layout.removeWidget(button2)
    layout.removeWidget(button3)
    button1.hide()
    button2.hide()
    button3.hide()
    layout.addWidget(menubutton)
    menubutton.show()
    ser.close()

def buttonmenuclick():
    layout.removeWidget(menubutton)
    menubutton.hide()
    layout.removeWidget(windowinput)
    windowinput.hide()
    layout.removeWidget(windowbutton)
    windowbutton.hide()
    layout.addWidget(button1)
    layout.addWidget(button2)
    layout.addWidget(button3)
    button1.show()
    button2.show()
    button3.show()

time.sleep(2)
# Se envia el mensaje de inicio de comunicacion
receive_handshake()
print('Conexión establecida!')
time.sleep(1)

# Se recibe el tamaño de la ventana de datos
receive_window_size()

# Se abre la conexion serial

ser = serial.Serial(PORT, BAUD_RATE, timeout = 1)

window_size = 0

app = QApplication([])

window = QWidget()
window.resize(1280, 720)

button1 = QPushButton("Solicitar ventana de datos")
button1.clicked.connect(button1click)
button2 = QPushButton("Cambiar tamaño ventana de datos")
button2.clicked.connect(button2click)
button3 = QPushButton("Cerrar la conexion")
button3.clicked.connect(button3click)
menubutton = QPushButton("Ir a menu principal")
menubutton.clicked.connect(buttonmenuclick)
windowinput = QLineEdit()
windowbutton = QPushButton("Enviar ventana")
windowbutton.clicked.connect(button2click2)


layout = QVBoxLayout()
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(button3)
window.setLayout(layout)

window.show()

app.exec_()
