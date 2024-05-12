import sqlite3
from datetime import datetime
import time
import serial.tools.list_ports
import serial


class SMSSender:
    def __init__(self):
        self.ser = serial.Serial(self.connect_to_usb_port(), baudrate=9600, timeout=1)
        self.conn = sqlite3.connect('/home/pi/smser-pi/sms_data.db')
        self.cursor = self.conn.cursor()

    def connect_to_usb_port(self):
        while True:
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                if port.startswith(('/dev/tty.usb', '/dev/cu.usb', 'COM', '/dev/ttyACM')):
                    print("Connected to port: "+port)
                    return port
            print("No suitable USB port found. Retrying in 2 seconds...")
            time.sleep(2)

    def write_to_uart(self, recipient, message):
        uart_data = "SEND Message: "+message+" Sender: "+recipient+""
        uart_data = uart_data.replace('\n', '').replace('\r', '')
        uart_data = uart_data + "\n"
        self.ser.write(uart_data.encode())
        print("To: "+recipient+"\nMessage: "+message+"")

    def check_confirmation(self, timeout=15):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                uart_input = self.ser.readline().decode().strip()
                print(""+uart_input+"")
                if uart_input == "SMS Sent!":
                    print("***************************\n")
                    return True
                else:
                    print("...")
        return False

    def send_sms(self):
        try:
            while True:
                self.cursor.execute("SELECT recipient, message, id FROM outgoing_sms WHERE sent_at IS NULL")
                unsent_data = self.cursor.fetchall()

                for row in unsent_data:
                    recipient, message, sms_id = row
                    self.write_to_uart(recipient, message)

                    if self.check_confirmation():
                        self.cursor.execute("UPDATE outgoing_sms SET sent_at = ? WHERE id = ?",
                                            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sms_id))
                        self.conn.commit()
                    else:
                        print("Confirmation not received. Retrying...")

                time.sleep(30)

        except KeyboardInterrupt:
            self.conn.close()
            self.ser.close()


if __name__ == "__main__":
    sms_sender = SMSSender()
    sms_sender.send_sms()
