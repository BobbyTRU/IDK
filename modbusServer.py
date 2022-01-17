import json
from datetime import datetime
from math import sin, sqrt, radians

import time
import requests
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from random import randint
import logging

import connector

from twisted.internet.task import LoopingCall

from influxdb import InfluxDBClient

influxClient = InfluxDBClient('localhost', 8086, 'kali', 'kali', 'openhab_db')

p1 = connector.web3Connection()

# region logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)
# endregion

# region all starting variables

# region temperature sensor
currentTemperature = 20  
targetTemperature = None  
targetTempReached = True  
targetTempChangedOnce = False
previousTempControllerValue = 1
# endregion

# region window control and co2 levels
currentCO2PPM = 250  
isWindowOpen = False 
isWindowFullOpen = False  
co2DecreaseMultiplier = 0 
# endregion

# region sunlight sensor
gotAngle = False  
currentSLAngle = 90  
angleTimeStamp = None  
# endregion

# endregion all starting variables


def updating_writer(a):
    print("Server now running on Port:5020")
    log.debug("updating the context")
    context = a[0]
    register = 4  # holding registers

    # region temperature_sensor
    global previousTempControllerValue, targetTemperature, targetTempReached, targetTempChangedOnce
    newVal = p1.getTargetValue("temperature")
    if newVal != previousTempControllerValue:
        targetTempReached = False
        targetTempChangedOnce = True
        targetTemperature = newVal
        context[0x00].setValues(register, 0, [newVal])

    temperature = get_temperature()
    p1.setCurrentValue(temperature,"temperature")
    context[0x00].setValues(register, 0, [temperature])
    # endregion


    # region co2_sensor
    global isWindowOpen
    # check if the windowController is set to open
    # if yes, check if the second windowController is set to fully open or partially open (tilted)
    targetWindowValue = p1.getTargetValue("window")
    currentWindowValue = p1.getCurrentValue("window")
    if(targetWindowValue != currentWindowValue):
        if(targetValue):
            client.write_registers(address=2,unit=0x00, values=[1], payload=[1])
            client.write_registers(address=3,unit=0x00, values=[1], payload=[1])
        else:
            client.write_registers(address=2,unit=0x00, values=[0], payload=[0])
            client.write_registers(address=3,unit=0x00, values=[0], payload=[0])
        
        isWindowOpen = targetWindowValue
        p1.setCurrentValue(targetWindowValue,"window")

    targetShuttersValue = p1.getTargetValue("shutters")
    currentShuttersValue = p1.getCurrentValue("shutters")
    if(targetShuttersValue != currentShuttersValue):
        if(targetValue):
            client.write_registers(address=4,unit=0x00, values=[1], payload=[1])
        else:
            client.write_registers(address=4,unit=0x00, values=[0], payload=[0])
        
        p1.setCurrentValue(targetShuttersValue,"shutters")

    
    
    co2PPM = get_co2()
    context[0x00].setValues(register, 2, [co2PPM])
    # endregion

    # region light_angle_sensor
    sunlight_angle = get_light_angle()
    context[0x00].setValues(register, 3, [sunlight_angle])
    # endregion


# region Temperature method
def get_temperature():
    global currentTemperature, targetTemperature, targetTempReached, previousTempControllerValue, targetTempChangedOnce
    # if there is a targetTemp and it has not been reached yet, do this
    if not targetTempReached:
        x = randint(0, 3)
        if targetTemperature > currentTemperature:
            # increase temp if smaller than target temp
            currentTemperature += x
        elif targetTemperature < currentTemperature:
            # decrease temp if higher than target temp
            currentTemperature -= x
        if targetTemperature == currentTemperature:
            # targetTempReached set to true, temperature will now fluctuate around the targetTemp
            targetTempReached = True
            previousTempControllerValue = currentTemperature
    else:
        x = randint(0, 2)
        if targetTempChangedOnce:
            # check if temperature has been changed once,
            # if yes, fluctuate around the set ControllerTemperature
            if currentTemperature >= (previousTempControllerValue+2):
                currentTemperature -= 1
                return currentTemperature
            elif currentTemperature <= (previousTempControllerValue-2):
                currentTemperature += 1
                return currentTemperature
        else:
            # randomly increase/decrease temp without any boundaries
            if x == 1:
                currentTemperature += 1
            if x == 2:
                currentTemperature -= 1
    return currentTemperature
# endregion


# region get_co2 method
# Increases co2-level by a random number between 1 and 4 including boundary conditions
def get_co2():
    global currentCO2PPM, isWindowOpen
    minimumC02Level = 200
    # check if window is open
    if isWindowOpen:
        co2DecreaseAmount = randint(1, 4)
        if currentCO2PPM >= 200:
            # decrease co2-levels if above 200
            # multiplier is set in the co2_sensor region
            currentCO2PPM = currentCO2PPM - (2 * co2DecreaseAmount)
        else:
            # fluctuate around 200 if not
            x = randint(0, 2)
            if currentCO2PPM >= (minimumC02Level+4):
                currentCO2PPM -= 1
            elif currentCO2PPM <= (minimumC02Level - 4):
                currentCO2PPM += 1
            else:
                currentCO2PPM += x
    else:
        # when windows are closed, co2 levels rise or stay at the current level
        x = randint(0, 4)
        currentCO2PPM += x
    return currentCO2PPM
# endregion


# region sunlight angle method
# creates some value between 0° and 90° for the sunlight angle,
# i.e. starting at 90° which is solar noon, 0° being sunset
def get_light_angle():
    global currentSLAngle, gotAngle, angleTimeStamp
    if gotAngle:
        if datetime.now().timestamp() >= (angleTimeStamp + 300000):
            gotAngle = False
            return get_light_angle()
    else:
        angleTimeStamp = datetime.now().timestamp()
        currentSLAngle -= 1
        gotAngle = True

    return currentSLAngle
# endregion


def run_updating_server():
    # modbus context
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 100000),  # 1)Discrete Inputs - 1 bit read only
        co=ModbusSequentialDataBlock(0, [0] * 100000),  # 2)Coils - 1 bit read/write
        hr=ModbusSequentialDataBlock(0, [int(1)] * 100000),  # 3)Holding registers - 16 bits read/write
        ir=ModbusSequentialDataBlock(0, [0] * 100000))  # 4)Input registers - 16 bits read only

    # it's possible to use a multitude of slaves
    # but for simplicity, only a single slave will be used
    context = ModbusServerContext(slaves=store, single=True)
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    loopTime = 5  # seconds delay
    loop = LoopingCall(f=updating_writer, a=(context,))
    loop.start(loopTime, now=False)

    StartTcpServer(context, identity=identity, address=("localhost", 5020))


if __name__ == "__main__":
    run_updating_server()
