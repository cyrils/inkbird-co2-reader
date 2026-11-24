import asyncio
import configparser
import json
import logging
import os
import sys

import paho.mqtt.publish as publish
from bleak import BleakClient, BleakScanner

characteristic = "0000ffe4-0000-1000-8000-00805f9b34fb"
command_characteristic = "0000ffe9-0000-1000-8000-00805f9b34fb"
request_measurement = bytes.fromhex("55 aa 09 06 01 0f")
wait_time = 120

class InkBird:
    def __init__(self, config):
        self.config: configparser.ConfigParser = config

    async def connect(self):
        logging.info('Searching for device..')
        inkbird = await BleakScanner.find_device_by_name(self.config['device']['alias'])

        if not inkbird:
            return logging.error('Device not found!')
        else:
            logging.info(f'Found device {inkbird}')

        async with BleakClient(inkbird) as client:
            logging.info(f"Client connection: {client.is_connected}")
            measurement = asyncio.get_running_loop().create_future()

            def receive_measurement(_sender, data):
                if not measurement.done() and len(data) >= 16 and data.startswith(b"\x55\xaa\x01"):
                    measurement.set_result(bytes(data))

            await client.start_notify(characteristic, receive_measurement)
            await client.write_gatt_char(command_characteristic, request_measurement, response=True)
            try:
                data = await asyncio.wait_for(measurement, timeout=wait_time)
            except asyncio.TimeoutError:
                logging.error("No measurement received within %s seconds", wait_time)
                return

        self.publish_measurement(data)

    def publish_measurement(self, data):
        sign = data[4]
        temperature = data[5] << 8 | data[6]
        json_data = {
            'temperature': (temperature if sign == 0 else -temperature) / 10,
            'co2': data[9] << 8 | data[10],
            'humidity': (data[7] << 8 | data[8]) / 10,
            'atmospheric_pressure': data[11] << 8 | data[12]
        }
        logging.info(json_data)
        if self.config.getboolean('mqtt', 'enabled', fallback=True):
            self.publish_mqtt(json_data)

    def publish_mqtt(self, json_data):
        user = self.config['mqtt']['user']
        password = self.config['mqtt']['password']
        auth = None if not user or not password else {"username": user, "password": password}

        publish.single(
            self.config['mqtt']['topic'], payload=json.dumps(json_data),
            hostname=self.config['mqtt']['server'], port=self.config['mqtt'].getint('port'),
            auth=auth, client_id="inkbird-reader"
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)
    config = configparser.ConfigParser(inline_comment_prefixes=('#'))
    config.read(config_path)

    asyncio.run(InkBird(config).connect())
