import serial
import paho.mqtt.client as paho
from threading import Timer
import logging

import config

def on_connect(mosq, obj, rc):
	logging.info("Connect with RC " + str(rc))
	
def on_disconnect(client, userdata, rc):
	logging.warning("Disconnected (RC " + str(rc) + ")")
	if rc <> 0:
		try_reconnect(client)

def on_log(client, userdata, level, buf):
	logging.debug(buf)

# MQTT reconnect
def try_reconnect(client, time = 60):
	try:
		logging.info("Trying reconnect")
		client.reconnect()
	except:
		logging.warning("Reconnect failed. Trying again in " + str(time) + " seconds")
		Timer(time, try_reconnect, [client]).start()

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# initialize MQTT
logging.info("Initializing MQTT")
mqttc = paho.Client("")
mqttc.username_pw_set(config.broker["user"], config.broker["password"])
mqttc.connect(config.broker["hostname"], config.broker["port"], 60)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_log = on_log

mqttc.loop_start()

while True:
	with serial.Serial('/dev/ttyUSB0', 2400, timeout=60) as ser:
		input = ser.read()
		for remote_id, values in config.buttons.iteritems():
			try:
				btn = values.index(hex(ord(input)))
				logging.info("Key " + remote_id + str(btn) + " pressed")
				mqttc.publish(config.topic, remote_id + str(btn))
				break
			except ValueError:
				pass
			except TypeError:
				break

