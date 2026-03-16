# boot.py
# This script is executed on every boot (including wake-up from deepsleep)
import network
import esp
import gc

esp.osdebug(None)
gc.collect()

WIFI_SSID = 'YOUR_WIFI_SSID'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'

def connect_wifi():
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        print('Connecting to network...')
        station.active(True)
        station.connect(WIFI_SSID, WIFI_PASSWORD)
        while not station.isconnected():
            pass
    print('Network config:', station.ifconfig())

connect_wifi()
