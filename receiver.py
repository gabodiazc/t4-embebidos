import serial
from struct import pack, unpack

# Se configura el puerto y el BAUD_Rate
PORT = '/dev/ttyUSB0'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32

window_size = 5

# Se abre la conexion serial
try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    print(f"Puerto {PORT} abierto correctamente.")
except serial.SerialException as e:
    print(f"No se pudo abrir el puerto {PORT}: {e}")
    exit()

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
    print(f"Data = {data}")
    data = unpack("fff", data)
    print(f'Received: {data}')
    return data

def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

# # Se lee data por la conexion serial
counter = 0
while True:
        print("1. Solicitar una ventana de datos")
        print("2. Cambiar el tamaño de la ventana de datos")
        print("3. Cerrar la conexión")
        print("4. Conocer el tamaño actual de la ventana")
        option = int(input("Ingrese el número de la opción deseada: \n"))

        if option not in [1, 2, 3, 4]:
            print("Opción no válida")
            continue

        elif option == 1:
            # Para pedir una ventana de datos
            message = pack('7s','BEGIN1\0'.encode())

            # Envía mensaje de 'quiero esta opción'
            send_message(message)
            
            break

        elif option == 2:
            break
        
        elif option == 3:
            break