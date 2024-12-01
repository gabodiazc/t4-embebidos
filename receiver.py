import serial
from struct import pack, unpack
import time

# Se configura el puerto y el BAUD_Rate
PORT = '/dev/ttyUSB1'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32

window_size = 10

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

def receive_floats():
    """ Funcion que recibe varios floats de la ESP32 
    y los imprime en consola """
    data = receive_data()
    data = unpack("ffffff", data)
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
    while True:
        # Pasa a recibir datos
        if ser.in_waiting > 0:
            try:
                message = receive_floats()
                # message = receive_data()
            except:
                print('Error en leer mensaje')
                continue
            else:
                print(f'Lectura {counter+1} de tamaño {len(message)} bytes')
                for i in range(0, len(message)):
                    print(float(message[i]))
                print()
                # Idea: que el time sleep sea adaptativo con el tamaño
                # de ventana (ventana más grande = más demora en enviar)
                time.sleep(0.6)
                send_OK()
                time.sleep(0.6)
                counter += 1
                
            finally:
                if counter == win_size + 5:
                    # ese 5 son los 5 top valores
                    print('Lecturas listas!')
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
    
# Se lee data por la conexion serial
while True:
        window_size = receive_window_size()

        print(f"El tamaño actual de la ventana de datos es {window_size}")
        print("1. Solicitar ventana de datos del sensor")
        print("2. Cambiar el tamaño de la ventana de datos. DEBE SER MAYOR O IGUAL A 5")
        print("3. Cerrar la conexión")
        option = int(input("Ingrese el número de la opción deseada: "))

        if option not in [1, 2, 3, 4]:
            print("Opción no válida")
            continue

        elif option == 1:
            receive_window_data(window_size)

        elif option == 2:
            new_value = input("Ingrese el tamaño de ventana requerido: ")
            send_window_size(new_value)
            wait_OK()
            print("OK de NVS llegó\n")
        
        elif option == 3:
            break