**1. Raspberry Pi Side: Print IP on LCD**

Here's a step-by-step tutorial on how to display the local IP address on an LCD using a Raspberry Pi and Python.

Title: Display Local IP Address on LCD with Raspberry Pi and Python

Objective:
Display the local IP address of the Raspberry Pi on an LCD display.

Requirements:
- Raspberry Pi (any model with GPIO pins)
- I2C LCD Display (e.g., 16x2 or 20x4)
- Python 3 installed on Raspberry Pi
- smbus2 Python library for I2C communication
- Basic knowledge of Raspberry Pi and Python

Steps:

Step 1: Connect the I2C LCD Display

1. Connect the I2C LCD display to the Raspberry Pi's GPIO pins. Typically, this involves connecting:
   - VCC to 5V
   - GND to GND
   - SDA to GPIO2 (SDA)
   - SCL to GPIO3 (SCL)

Step 2: Install Required Packages

Make sure your Raspberry Pi is connected to the internet.
Open a terminal on your Raspberry Pi and install the `smbus2` Python library:

sudo pip install netifaces smbus2

++++++++++++++++++++++++++<br>
**2. Download and Save into SQLite DB**

Requirements;
sudo apt install sqlite

++++++++++++++++++++++++++<br>
**3. Fetch from DB and Send via Serial**

Requirements;
sudo apt install sqlite



