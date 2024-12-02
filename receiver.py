import serial, sys
from struct import pack, unpack
import time
from PyQt5.QtWidgets import *
import pyqtgraph as pg

# Se configura el puerto y el BAUD_Rate
PORT = '/dev/ttyUSB0'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32

window_size = 10
accel_x = []
accel_y = []
accel_z = []
gyro_x = []
gyro_y = []
gyro_z = []

# Se abre la conexion serial
try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()  # Limpia el buffer de entrada
    ser.reset_output_buffer()  # Limpia el buffer de salida
    print(f'Puerto {PORT} abierto correctamente.\n')
except serial.SerialException as e:
    print(f'No se pudo abrir el puerto {PORT}: {e}')
    exit()

# Funciones
def send_message(message):
    """ Funcion para enviar un mensaje a la ESP32 """
    ser.write(message)

def receive_data():
    """ Funcion para recibir un mensaje de la ESP32 """
    response = ser.read_all()
    return response

def receive_floats(n):
    """ Funcion que recibe n floats de la ESP32 
    y los imprime en consola """
    data = receive_data()
    format_string = 'f' * n
    data = unpack(format_string, data)
    return data

def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

def wait_OK():
    while True:
        try:
            message = ser.readline().decode("utf-8")
            if message == "OK\n":
                # Lee un byte en blanco, residuo del OK recibido
                ser.readline(1)
                break
        except:
            print("except clause wait_OK")

def send_OK():
    send_message(pack('3s','OK\0'.encode()))

def receive_window_size():
    global window_size

    print('Recibiendo tamaño de ventana de datos...')
    send_message(pack('7s','BEGIN4\0'.encode()))

    wait_OK()
    print('OK de send_window_size recibido!\n')

    # Le da tiempo al ESP para enviar los datos
    time.sleep(0.5)
    while True:
        if ser.in_waiting > 0:
            try:
                message = receive_data()
                message = unpack("f", message)
            except:
                print('receive_window_size: error en leer mensaje')
                continue
            else:
                window_size = message
                return int(window_size[0])

def receive_window_data(win_size):
    # Para pedir una ventana de datos
    # Envía mensaje de 'quiero esta opción'
    send_message(pack('7s','BEGIN1\0'.encode()))
    wait_OK()

    print("OK recibido!")
    # Le da tiempo al ESP para enviar los datos
    time.sleep(0.5)
    counter = 0
    log_message('Raw data de aceleración y giroscopio en ejes x, y, z:')

    while True:
        # Recibe dator brutos
        if ser.in_waiting > 0:
            try:
                message = receive_floats(6)
                # message = receive_data()
            except:
                print('Error en leer mensaje')
                continue
            else:
                print(f'Dato bruto {counter+1}')
                for i in range(0, len(message)):
                    print(float(message[i]))            
                print()

                accel_x.append(float(message[0]))
                accel_y.append(float(message[1]))
                accel_z.append(float(message[2]))
                gyro_x.append(float(message[3]))
                gyro_y.append(float(message[4]))
                gyro_z.append(float(message[5]))

                log_message(f'Muestra {counter+1}')
                log_message(f'Aceleración en x: {float(message[0])} g')
                log_message(f'Aceleración en y: {float(message[1])} g')
                log_message(f'Aceleración en z: {float(message[2])} g')
                log_message(f'Giroscopio en x: {float(message[3])} rad/s')
                log_message(f'Giroscopio en y: {float(message[4])} rad/s')
                log_message(f'Giroscopio en z: {float(message[5])} rad/s')
                log_message('\n')

                # Idea: que el time sleep sea adaptativo con el tamaño
                # de ventana (ventana más grande = más demora en enviar)
                time.sleep(0.6)
                send_OK()
                time.sleep(0.6)
                counter += 1
                
            finally:
                if counter == win_size:
                    print('Lecturas listas de datos brutos.')
                    print()
                    break
    counter = 0
    log_message('Cinco peaks de mayor a menor')
    while True:
        # Pasa a recibir datos
        if ser.in_waiting > 0:
            try:
                message = receive_floats(6)
                # message = receive_data()
            except:
                print('Error en leer mensaje')
                continue
            else:
                print(f'Máximos valores {counter+1}')
                for i in range(0, len(message)):
                    print(float(message[i]))
                print()
                # Idea: que el time sleep sea adaptativo con el tamaño
                # de ventana (ventana más grande = más demora en enviar)

                log_message(f'Peak {counter+1} de cada una de las variables')
                log_message(f'Aceleración en x: {float(message[0])} g')
                log_message(f'Aceleración en y: {float(message[1])} g')
                log_message(f'Aceleración en z: {float(message[2])} g')
                log_message(f'Giroscopio en x: {float(message[3])} rad/s')
                log_message(f'Giroscopio en y: {float(message[4])} rad/s')
                log_message(f'Giroscopio en z: {float(message[5])} rad/s')
                log_message('\n')

                time.sleep(0.6)
                send_OK()
                time.sleep(0.6)
                counter += 1
                
            finally:
                if counter == 5:
                    print('Lecturas listas de los 5 max valores.')
                    print()
                    break
    counter = 0
    while True:
        # Pasa a recibir datos
        if ser.in_waiting > 0:
            try:
                message = receive_floats(12)
                # message = receive_data()
            except:
                print('Error en leer mensaje')
                continue
            else:
                print(f'Valores de FFT (Re Im Re Im ....)')
                for i in range(0, len(message)):
                    print(float(message[i]))
                print()

                log_message(f'FFT {counter+1}')
                log_message(f'Aceleración en x FFT parte real: {float(message[0])}')
                log_message(f'Aceleración en x FFT parte imaginaria: {float(message[1])}')
                
                log_message(f'Aceleración en y FFT parte real: {float(message[2])}')
                log_message(f'Aceleración en y FFT parte imaginaria: {float(message[3])}')

                log_message(f'Aceleración en z FFT parte real: {float(message[4])}')
                log_message(f'Aceleración en z FFT parte imaginaria: {float(message[5])}')
                
                log_message(f'Giroscopio en x FFT parte real: {float(message[6])}')
                log_message(f'Giroscopio en x FFT parte imaginaria: {float(message[7])}')

                log_message(f'Giroscopio en y FFT parte real: {float(message[8])}')
                log_message(f'Giroscopio en y FFT parte imaginaria: {float(message[9])}')
                
                log_message(f'Giroscopio en z FFT parte real: {float(message[10])}')
                log_message(f'Giroscopio en z FFT parte imaginaria: {float(message[11])}')
                log_message('\n')

                # Idea: que el time sleep sea adaptativo con el tamaño
                # de ventana (ventana más grande = más demora en enviar)
                time.sleep(0.6)
                send_OK()
                time.sleep(0.6)
                counter += 1
                
            finally:
                if counter == win_size:
                    print('Lecturas listas de FFT')
                    print()
                    break
    counter = 0
    log_message(f'Valor RMS de cada variable:')
    while True:
        # Pasa a recibir datos
        if ser.in_waiting > 0:
            try:
                message = receive_floats(6)
                # message = receive_data()
            except:
                print('Error en leer mensaje')
                continue
            else:
                print(f'Valores RMS de cada variable')
                for i in range(0, len(message)):
                    print(float(message[i]))
                print()

                log_message(f'RMS aceleración en x: {float(message[0])}')
                log_message(f'RMS aceleración en y: {float(message[1])}')
                log_message(f'RMS aceleración en z: {float(message[2])}')
                log_message(f'RMS giroscopio en x: {float(message[3])}')
                log_message(f'RMS giroscopio en y: {float(message[4])}')
                log_message(f'RMS giroscopio en z: {float(message[5])}')
                log_message('\n')

                # Idea: que el time sleep sea adaptativo con el tamaño
                # de ventana (ventana más grande = más demora en enviar)
                time.sleep(0.6)
                send_OK()
                time.sleep(0.6)
                counter += 1
                
            finally:
                if counter == 1:
                    print('Lecturas listas de RMS')
                    print()
                    break

def send_window_size(new_value):
    global window_size
    # Para pedir una ventana de datos
    # Envía mensaje de 'quiero esta opción'
    send_message(pack('7s','BEGIN2\0'.encode()))
    
    wait_OK()
    print("OK recibido!")

    window_size = new_value
    send_message(pack('4s', f'{new_value}\0'.encode()))
    # 4 bytes para los 3 dígitos y el cierre \0

    wait_OK()
    print("OK de NVS llegó\n")
    log_message(f'Valor NVS cambiado exitosamente a {new_value}.')

def end_connection():
    # Para pedir una ventana de datos
    # Envía mensaje de 'quiero esta opción'
    send_message(pack('7s','BEGIN3\0'.encode()))

# ------------------- Código versión anterior ----------------------------
# Se lee data por la conexion serial
# while True:
#         window_size = receive_window_size()
#         print(f"El tamaño actual de la ventana de datos es {window_size}")
#         print("1. Solicitar ventana de datos del sensor")
#         print("2. Cambiar el tamaño de la ventana de datos. DEBE SER MAYOR O IGUAL A 5")
#         print("3. Cerrar la conexión")
#         option = int(input("Ingrese el número de la opción deseada: "))

#         if option not in [1, 2, 3, 4]:
#             print("Opción no válida")
#             continue

#         elif option == 1:
#             receive_window_data(window_size)

#         elif option == 2:
#             new_value = input("Ingrese el tamaño de ventana requerido: ")
#             send_window_size(new_value)
        
#         elif option == 3:
#             break
# ------------------- Código versión anterior ----------------------------
def log_message(message):
    log_widget.append(message)
    QApplication.processEvents()  # Forzar la actualización de la interfaz

def button_request_window():
    receive_window_data(window_size)
    graph.clear()
    graph.addLegend()
    graph.plot(accel_x, pen=pg.mkPen('r', width=3), name='Accel X')
    graph.plot(accel_y, pen=pg.mkPen('g', width=3), name='Accel Y')
    graph.plot(accel_z, pen=pg.mkPen('b', width=3), name='Accel Z')
    graph.plot(gyro_x, pen=pg.mkPen('c', width=3), name='Gyro X')
    graph.plot(gyro_y, pen=pg.mkPen('m', width=3), name='Gyro Y')
    graph.plot(gyro_z, pen=pg.mkPen('y', width=3), name='Gyro Z')
    accel_x.clear()
    accel_y.clear()
    accel_z.clear()
    gyro_x.clear()
    gyro_y.clear()
    gyro_z.clear()

def button_change_windowsize():
    button1.hide()
    button2.hide()
    button3.hide()
    windowinput.show()
    acceptbutton.show()
    menubutton.show()

def button_accept_change_windowsize():
    new_window_size = int(windowinput.text())
    print(f"Nuevo tamaño de ventana: {new_window_size}")
    send_window_size(new_window_size)
    
    left_layout.addWidget(button1)
    left_layout.addWidget(button2)
    left_layout.addWidget(button3)

def button_return_main_menu():
    windowinput.hide()
    acceptbutton.hide()
    menubutton.hide()
    button1.show()
    button2.show()
    button3.show()
    left_layout.addWidget(menubutton)

def button_end_connection():
    end_connection()
    ser.close()
    app.quit()

window_size = receive_window_size()


# App
app = QApplication([])

window = QWidget()
window.setWindowTitle("Interfaz de Comunicación con ESP32")
window.resize(800, 600)

# Crear los widgets
button1 = QPushButton("Solicitar ventana de datos")
button1.clicked.connect(button_request_window)

button2 = QPushButton("Cambiar tamaño ventana de datos")
button2.clicked.connect(button_change_windowsize)

button3 = QPushButton("Cerrar la conexion")
button3.clicked.connect(button_end_connection)

menubutton = QPushButton("Volver al menu principal")
menubutton.clicked.connect(button_return_main_menu)

windowinput = QLineEdit()
windowinput.setPlaceholderText("Ingrese tamaño de ventana")

acceptbutton = QPushButton("Enviar")
acceptbutton.clicked.connect(button_accept_change_windowsize)

graph = pg.PlotWidget()
graph.setBackground('w')
graph.setYRange(0, 100)

log_widget = QTextEdit()
log_widget.setReadOnly(True)
log_widget.setFixedHeight(400)
log_widget.setFixedWidth(250)

# Crear el layout principal
main_layout = QHBoxLayout()

# Crear el layout izquierdo (log y botones)
left_layout = QVBoxLayout()
left_layout.addWidget(log_widget)
left_layout.addWidget(button1)
left_layout.addWidget(button2)
left_layout.addWidget(button3)
left_layout.addWidget(windowinput)
left_layout.addWidget(acceptbutton)
left_layout.addWidget(menubutton)
windowinput.hide()
menubutton.hide()
acceptbutton.hide()

# Añadir el layout izquierdo y el gráfico al layout principal
main_layout.addLayout(left_layout)
main_layout.addWidget(graph)

# Establecer el layout principal en la ventana
window.setLayout(main_layout)

window.show()
log_message(f'El valor de tamaño de ventana guardado en la NVS es {window_size}.')

app.exec_()