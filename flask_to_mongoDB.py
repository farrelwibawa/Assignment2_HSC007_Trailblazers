from machine import Pin, ADC
import ujson
import network
import utime as time
import dht
import urequests as requests

# Sensor setup
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
DHT_PIN = Pin(4)
PIR_PIN = Pin(5, Pin.IN)

DEVICE_ID = "trailblazers"
WIFI_SSID = "FARREL_FIONA"
WIFI_PASSWORD = "b@mb@ng2f"

# Flask Server URL (Change to your Flask Server IP)
FLASK_SERVER_URL = "http://192.168.1.8:5000/flask_server"

def send_data(temperature, humidity, light, motion):
    headers = {"Content-Type": "application/json"}
    data = {
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "light": light,
        "motion": motion
    }
    try:
        response = requests.post(FLASK_SERVER_URL, json=data, headers=headers)
        print("Data Sent!")
        print("Response:", response.text)
    except Exception as e:
        print("Error sending data:", e)

# Connect to WiFi
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting")
    time.sleep(0.1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

# Sensor instance
dht_sensor = dht.DHT11(DHT_PIN)

while True:
    try:
        dht_sensor.measure()
        ldr_value = ldr.read()
        motion_status = PIR_PIN.value()
    except Exception as e:
        print("Error reading sensors:", e)
        continue

    time.sleep(0.5)
    
    send_data(dht_sensor.temperature(), dht_sensor.humidity(), ldr_value, motion_status)

    time.sleep(0.1)
