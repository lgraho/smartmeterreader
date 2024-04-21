#!/usr/bin/env python
import os
import sys
import logging
import yaml
import json

import mbus
import parser
import mqttclient

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

def load_config(file: str) -> dict:
    try:
        logging.info("Loading %s...", file)
        return yaml.safe_load(open(os.path.join(os.path.dirname(__file__), file)))
    except FileNotFoundError:
        logging.error("Failed loading %s: File not found", os.path.basename(file))
        sys.exit("Config file not found")

config = load_config("../config.yaml")
data_format = load_config("../data_format.yaml")

mbus_reader = mbus.MBus(config["mbus"], data_format["frame_format"])
frame_parser = parser.Parser(config["encryption_key"], data_format["frame_format"], data_format["apdu_format"])
mqtt = mqttclient.MQTTClient(config["mqtt"]["broker"], config["mqtt"]["port"], config["mqtt"]["user"], config["mqtt"]["password"])

mqtt.start()
mqtt.connect()

# Publish MQTT config topics for Home Assistant discovery
if "homeassistant" in config and "config_topics" in config["homeassistant"]:
    for topic in config["homeassistant"]["config_topics"]:
        mqtt.publish(topic["config_topic"], json.dumps(topic["config"]))
        logging.debug("Published config for: %s", str(topic["config_topic"]))
    logging.info("Published MQTT config topics")

logging.info("Running...")
try:
    while True:
        frame = mbus_reader.read_frame()
        data = frame_parser.extract_data(frame)
        if data:
            mqtt.publish(config["mqtt"]["data_topic"], json.dumps(data))
            logging.debug("Published data: %s", data)
        else:
            logging.error("Failed extracting data from frame")
except KeyboardInterrupt:
    logging.info("Exiting...")
    mbus_reader.close()
    mqtt.close()
