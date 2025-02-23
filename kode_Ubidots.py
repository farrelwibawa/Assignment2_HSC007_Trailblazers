from machine import Pin, ADC
import ujson
import network
import utime as time
import dht
import urequests as requests

# Konfigurasi sensor
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
DHT_PIN = Pin(4)
PIR_PIN = Pin(5, Pin.IN)

DEVICE_ID = "trailblazers"
WIFI_SSID = "FARREL_FIONA"
WIFI_PASSWORD = "b@mb@ng2f"
TOKEN = "BBUS-dB97GE1wAk8TkPTvhHA8kdRZqNmraa"

def did_receive_callback(topic, message):
    print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

def create_json_data(temperature, humidity, light, motion):
    data = ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "light": light,
        "motion": motion,
        "type": "sensor"
    })
    return data

def send_data(temperature, humidity, light, motion):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "ldr_value": light,
        "motion": motion
    }
    response = requests.post(url, json=data, headers=headers)
    print("Done Sending Data!")
    print("Response:", response.text)

wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting")
    time.sleep(0.1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

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