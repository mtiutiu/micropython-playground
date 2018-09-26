import network
import utime
import machine
from lib import mtypes
from lib.mysensors import MySensors
from lib.mymessage import MyMessage
from lib.neopixel.effects import WS2812FX
from lib import utils


APP_DEBUG = True
machine.loglevel("*", machine.LOG_NONE)

WIFI_CFG_FILE = 'config/wifi.json'
MYSENSORS_CFG_FILE = 'config/mysensors.json'
WS2812FX_CFG_FILE = 'config/ws2812.json'

WIFI_CFG = utils.load_cfg(WIFI_CFG_FILE)
MYSENSORS_CFG = utils.load_cfg(MYSENSORS_CFG_FILE)
WS2812FX_CFG = utils.load_cfg(WS2812FX_CFG_FILE)

mdns = network.mDNS()
mysensors = MySensors(MYSENSORS_CFG, APP_DEBUG)
ws2812fx = WS2812FX(WS2812FX_CFG['data_pin'], WS2812FX_CFG['led_count'])


def debug(msg):
    if APP_DEBUG:
        print(msg)


def send_presentation():
    mysensors.send_sketch_info(MYSENSORS_CFG['name'])
    for sensor in MYSENSORS_CFG['sensors']:
        msg = MyMessage(sensor['id'], mtypes.V_STATUS)
        mysensors.present(sensor['id'], mtypes.S_BINARY, sensor['alias'])
        mysensors.send(msg.set(1))


def on_message(msg):
    debug("[MYSENSORS] Got payload: {}".format(msg['payload']))


def on_presentation():
    send_presentation()


def wifi_cb(event):
    DISCONNECTED_EVT = 5
    GOT_IP_EVT = 7
    status = event[0]

    if status == GOT_IP_EVT:
        debug("[WiFi] Connected!")
        mdns.start("mys-esp32", "Mysensors ESP32 Node")
        mdns.addService('_telnet', '_tcp', 23, "MicroPython", {"board": "ESP32", "service": "mPy Telnet REPL"})
        network.telnet.start(user="micro", password="python", timeout=300)
        mysensors.begin()
    if status == DISCONNECTED_EVT:
        debug("[WiFi] Disconnected!")
        mysensors.end()
        mdns.stop()
        network.telnet.stop()


def setup():
    # WS2812 init
    ws2812fx.init()
    ws2812fx.set_brightness(WS2812FX_CFG['brightness'])
    ws2812fx.set_speed(WS2812FX_CFG['speed'])
    ws2812fx.set_mode(WS2812FX_CFG['mode'])
    ws2812fx.start()
    # WiFi init
    network.WLANcallback(wifi_cb)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(WIFI_CFG['ssid'], WIFI_CFG['password'])
    debug("[WiFi] Connecting ...")
    # MySensors init
    mysensors.register_on_message_cb(on_message)
    mysensors.register_presentation_cb(on_presentation)


def main():
    setup()
    while True:
        ws2812fx.service()
        utime.sleep_ms(5)


main()
