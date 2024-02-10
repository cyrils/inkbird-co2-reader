import asyncio
from bleak import BleakClient

address = "5EF4D0CB-BE4F-F4C0-EF94-56A2EE08C932"
characteristic = "0000ffe4-0000-1000-8000-00805f9b34fb"
wait_time = 120 # I haven't yet figured out how to make ad-hoc read

def notification_callback(sender, data):
    sign = data[4]
    temperature = data[5] << 8 | data[6]
    print ("Temperature:", temperature if sign == 0 else -temperature) # °C
    print ("CO2:", data[9] << 8 | data[10]) # ppm
    print ("Humidity:", data[7] << 8 | data[8]) # %
    print ("Air Pressure:", data[11] << 8 | data[12]) # hPa

async def main():
    # Connect to the BLE device
    async with BleakClient(address) as client:
        # Check if connection was successful
        print(f"Client connection: {client.is_connected}")

        # Subcribe to notification
        await client.start_notify(characteristic, notification_callback)

        await asyncio.sleep(wait_time)

        # Stop notifications on the characteristic
        await client.stop_notify(characteristic)

        # Disconnect from the BLE device
        await client.disconnect()

asyncio.run(main())
