from datetime import datetime
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import time
from influxdb import InfluxDBClient


influxClient = InfluxDBClient('localhost', 8086, 'kali', 'kali', 'openhab_db')
client = ModbusClient('127.0.0.1', port=5020)
client.connect()
print("Starting Client-Connection")
while True:
    time.sleep(10)  # send all data every 10 seconds
    print("getting data...")
    currentDT = datetime.fromtimestamp(datetime.now().timestamp()+60000)
    measurementNames = ["temperature", "CO2_Level", "Sunlight_Angle","Window","Shutters"]
    for i in range(3):
        Result = client.read_input_registers(address=i, count=10, unit=0x00)
        decoder = BinaryPayloadDecoder.fromRegisters(Result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        decodedData = decoder.decode_16bit_uint()
        # print(measurementNames[i], decodedData) for debugging
        JSON = [
            {
                "measurement": measurementNames[i],
                "time": currentDT,
                "fields": {
                    "value": decodedData
                }
            }
        ]
        influxClient.write_points(JSON)
    for i in range[3,4]:
        Result = client.read_holding_registers(address=i, count=10, unit=0x00)
        decoder = BinaryPayloadDecoder.fromRegisters(Result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        decodedData = decoder.decode_16bit_uint()
        # print(measurementNames[i], decodedData) for debugging
        JSON = [
            {
                "measurement": measurementNames[i],
                "time": currentDT,
                "fields": {
                    "value": decodedData
                }
            }
        ]
        influxClient.write_points(JSON)
    print("got it!")

client.close()
