import paho.mqtt.client as mqtt
import logging
import threading
import time

class MQTTClient():
    """
    Represents an MQTT client for publishing data to a broker.

    Attributes:
        broker (str): The IP address or hostname of the MQTT broker.
        port (int): The port of the MQTT broker.
        client (mqtt.Client): The MQTT client instance.
        connected_event (threading.Event): The event signaling that the client is connected to the broker.
    """
    def __init__(self, broker, port, user=None, pw=None, client_id=""):
        logging.info("Initializing MQTT client...")
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client.username_pw_set(user, pw)
        self.broker = broker
        self.port = port
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connected_event = threading.Event()

    def connect(self):
        """
        Connects to the MQTT broker (blocking). Reconnects automatically if the connection is lost.
        """
        logging.info("Connecting to MQTT broker on %s...", self.broker)
        while not self.connected_event.is_set():
            try:
                self.client.connect(self.broker, self.port)
                self.connected_event.wait()
            except:
                time.sleep(1)

    def disconnect(self):
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected_event.set()
            logging.info("Connected to MQTT broker")
        else:
            logging.error("MQTT connection failed: connection result: %s" + reason_code)

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected_event.clear()
        if reason_code == 0:
            logging.info("Disconnected from MQTT broker")
        else:
            logging.warning("Disconnected from MQTT broker. Reconnecting...")

    def start(self):
        self.client.loop_start()
        logging.info("Started MQTT client")

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()

