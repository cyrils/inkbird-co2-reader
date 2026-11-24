# INKBIRD CO2 Reader
BLE reader for INKBIRD IAM-T1 Air Quality Monitor

![inkbird](https://github.com/cyrils/inkbird-co2-reader/assets/5549113/637bb8c9-2aec-4d40-a5bd-bc2191fa5619)


## How to
Update `config.ini` with yout MQTT config
```
pip3 install bleak

python3 inkbird-co2-reader/reader.py
```

## Sample output

```text
INFO:root:Searching for device..
INFO:root:Found device <device-id>: Ink@IAM-T1
INFO:root:Client connection: True
INFO:root:{'temperature': 20.1, 'co2': 643, 'humidity': 58.0, 'atmospheric_pressure': 1016}
```
