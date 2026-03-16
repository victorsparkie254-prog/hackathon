# main.py
import time
import dht
import machine
import urequests
import ujson
try:
    from umqttsimple import MQTTClient
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

# --- Configuration ---
DEVICE_ID = "esp32_farm_01"
BACKEND_HTTP_URL = "http://192.168.1.100:8000/api/sensors" # Replace with your backend IP
MQTT_SERVER = "192.168.1.100" # Replace with your Mosquitto broker IP
USE_MQTT = False # Set to True to use MQTT instead of HTTP POST

# --- Sensors ---
# DHT11 on GPIO 4
sensor_dht = dht.DHT11(machine.Pin(4))
# Capacitive soil moisture sensor on GPIO 34 (ADC)
soil_adc = machine.ADC(machine.Pin(34))
soil_adc.atten(machine.ADC.ATTN_11DB) # Full range: 3.3v

# --- MQTT Setup (Optional) ---
def connect_mqtt():
    if not MQTT_AVAILABLE:
        print("umqttsimple not found, please install/upload it.")
        return None
    client = MQTTClient(DEVICE_ID, MQTT_SERVER)
    client.connect()
    print("Connected to MQTT broker")
    return client

client = None
if USE_MQTT:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("MQTT connection failed:", e)

print(f"Starting Sensor Node {DEVICE_ID}...")

while True:
    try:
        # Measure DHT
        sensor_dht.measure()
        temp = sensor_dht.temperature()
        hum = sensor_dht.humidity()
        
        # Read soil (invert if needed based on calibration: 0 is dry, 4095 is wet or vice versa)
        # Assuming typical 0-4095 range, with higher voltage meaning drier. 
        # Example calibration: 3000 in air (dry), 1500 in water (wet)
        raw_soil = soil_adc.read()
        
        # Simple map to percentage
        moisture_percent = max(0, min(100, (3000 - raw_soil) / (3000 - 1500) * 100))
        
        payload = {
            "device_id": DEVICE_ID,
            "temperature": temp,
            "humidity": hum,
            "soil_moisture": int(moisture_percent)
        }
        
        print("Sensor readings:", payload)
        
        if USE_MQTT and client:
            client.publish(b"farm/sensors", ujson.dumps(payload))
            print("Sent via MQTT")
        else:
            headers = {'Content-Type': 'application/json'}
            response = urequests.post(BACKEND_HTTP_URL, data=ujson.dumps(payload), headers=headers)
            print("HTTP Response:", response.status_code)
            response.close()
            
    except Exception as e:
        print("Error reading sensors or sending data:", e)
        
    time.sleep(30) # Delay between readings (30 seconds for prototype)
