import sys
import time
from struct import pack, unpack
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
)
import serial

class DataWindowApp(QWidget):
    def __init__(self, port, baud_rate):
        super().__init__()
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        self.window_size = 0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Data Window Manager")
        self.resize(1280, 720)

        # Initialize UI components
        self.button_request_data = QPushButton("Solicitar ventana de datos")
        self.button_change_window = QPushButton("Cambiar tamaño ventana de datos")
        self.button_close_connection = QPushButton("Cerrar la conexión")
        self.menu_button = QPushButton("Ir a menú principal")
        self.input_window_size = QLineEdit()
        self.send_window_button = QPushButton("Enviar ventana")

        # Connect signals to slots
        self.button_request_data.clicked.connect(self.handle_request_data)
        self.button_change_window.clicked.connect(self.show_window_size_input)
        self.button_close_connection.clicked.connect(self.close_connection)
        self.menu_button.clicked.connect(self.return_to_main_menu)
        self.send_window_button.clicked.connect(self.update_window_size)

        # Set up layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button_request_data)
        self.layout.addWidget(self.button_change_window)
        self.layout.addWidget(self.button_close_connection)

        self.setLayout(self.layout)

    def clear_main_buttons(self):
        """Hide and remove main buttons from the layout."""
        for button in [self.button_request_data, self.button_change_window, self.button_close_connection]:
            self.layout.removeWidget(button)
            button.hide()

    def add_menu_button(self):
        """Add the menu button to the layout."""
        self.layout.addWidget(self.menu_button)
        self.menu_button.show()

    def handle_request_data(self):
        """Handle logic for requesting data."""
        self.clear_main_buttons()

        message1 = pack('2s', '1\0'.encode())
        self.send_message(message1)

        print('Solicitando ventana de datos...\n')
        time.sleep(1)

        message2 = pack('6s', 'BEGIN\0'.encode())
        self.send_message(message2)

        time.sleep(3)
        self.receive_window_data()
        self.send_end_message()

        self.add_menu_button()

    def show_window_size_input(self):
        """Show input and button for changing window size."""
        self.clear_main_buttons()
        self.layout.addWidget(self.input_window_size)
        self.input_window_size.show()
        self.layout.addWidget(self.send_window_button)
        self.send_window_button.show()
        self.menu_button.show()

    def update_window_size(self):
        """Update the window size based on user input."""
        try:
            new_window_size = int(self.input_window_size.text())
            message1 = pack('2s', '2\0'.encode())
            self.send_message(message1)

            time.sleep(4)

            message2 = pack('4s', str(new_window_size).encode())
            self.send_message(message2)

            time.sleep(4)
            self.window_size = new_window_size
            self.add_menu_button()
        except ValueError:
            print("Invalid window size input.")

    def close_connection(self):
        """Close the serial connection."""
        self.clear_main_buttons()
        self.add_menu_button()
        self.ser.close()

    def return_to_main_menu(self):
        """Return to the main menu."""
        self.layout.removeWidget(self.menu_button)
        self.menu_button.hide()

        for widget in [self.input_window_size, self.send_window_button]:
            if widget in self.layout:
                self.layout.removeWidget(widget)
                widget.hide()

        for button in [self.button_request_data, self.button_change_window, self.button_close_connection]:
            self.layout.addWidget(button)
            button.show()

    def send_message(self, message):
        """Send a message over the serial connection."""
        self.ser.write(message)

    def receive_response(self):
        """ Funcion para recibir un mensaje de la ESP32 """
        response = self.ser.readline()
        return response

    def receive_data(self):
        """ Funcion que recibe tres floats (fff) de la ESP32 
        y los imprime en consola """
        data = self.receive_response()
        data = unpack("ffff", data)
        print("Temperature: ", data[0])
        print("Pressure: ", data[1])
        return data

    def receive_data_size(self):
        """ Funcion que recibe tres floats (fff) de la ESP32 
        y los imprime en consola """
        data = self.receive_response()
        data = unpack("ffff", data)
        return data

    def receive_window_data(self):
        """Placeholder for receiving window data."""
        print("Receiving window data...")

    def send_end_message(self):
        """Send an end message."""
        print("Sending end message...")
        self.ser.write(b"END\0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    port = "COM3"  # Replace with actual port
    baud_rate = 115200  # Replace with actual baud rate
    window = DataWindowApp(port, baud_rate)
    window.show()
    sys.exit(app.exec_())
