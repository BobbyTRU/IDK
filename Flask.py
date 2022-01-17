
from flask import Flask, request
# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import connector

# # client = ModbusClient('127.0.0.1', port=5020)
# client.connect()
app = Flask(__name__)
p1 = connector.web3Connection()
import time
import datetime
d =datetime.datetime.today()


#region get target Values -------------------------
@app.route('/getShuttersTarget')
def getshuttersTarget():
    value = p1.getTargetValue("shutters")
    if(value):
        state = "hoch"
    else:
        state = "runter"
    return "Rollläden werden " + state + " fahren."

@app.route('/getWindowTarget')
def getWindowTarget():
    value = p1.getTargetValue("window")
    if(value):
        state = "auf"
    else:
        state = "zu"
    return "Fenster wird " + state + " gehen."

@app.route('/getTempTarget')
def getTemperatureTarget():
    value = p1.getTargetValue("temperature")
    return "Temperatur wird auf " + str(value) + " gesetzt." 
#endregion 

#region get current Values -------------------------
@app.route('/getShuttersCurrent')
def getshuttersCurrent():
    value = p1.getCurrentValue("shutters")
    if(value):
        state = "oben"
    else:
        state = "unten"
    return "Rollläden sind " + state

@app.route('/getWindowCurrent')
def getWindowCurrent():
    value = p1.getCurrentValue("window")
    if(value):
        state = "auf"
    else:
        state = "zu"
    return "Fenster sind " + state

@app.route('/getTempCurrent')
def getTemperatureCurrent():
    value = p1.getCurrentValue("temperature")
    return "Temperatur ist bei " + str(value) + "°C"
#endregion 

#region set target Values -------------------------
@app.route('/setShuttersTarget')
def setShuttersTarget():
    value = request.args["target"]
    if(value == "hoch"):
        passedValue = True
    else:
        passedValue = False
    txn = p1.setTargetValue(passedValue,"shutters")
    if(txn == 1):
        msg =  "Rollläden sollen " + value +" fahren."
        print(msg)
        return msg
    else:
        return "Die Transaktion wurde durch EVM rückgängig gemacht."

@app.route('/setWindowTarget')
def setWindowTarget():
    value = request.args["target"]
    if(value == "auf"):
        passedValue = True
    else:
        passedValue = False
    txn = p1.setTargetValue(passedValue,"window")
    if(txn == 1):
        msg = "Fenster sollen " + value +" gehen."
        print(msg)
        return msg
    else:
        return "Die Transaktion wurde durch EVM rückgängig gemacht."

@app.route('/setTempTarget')
def setTemperatureTarget():
    value = request.args["target"]
    txn = p1.setTargetValue(int(value),"temperature")
    if(txn == 1):
        msg = "Temperature wird auf " + str(value) +" gesetzt."
        print(msg)
        return msg
    else:
        return "Die Transaktion wurde durch EVM rückgängig gemacht."

@app.route('/setTempTargetTimer')
def setTemperatureTargetTimer():
    print(d)
    value = request.args["time"]
    timerDate = datetime(d.year,d.month,d.day,d.hour,value)
    print(timerDate)
    txn = p1.setTargetValueWithTime(value)
    if(txn == 1):
        msg = "Temperature wird auf " + str(value) +" gesetzt."
        print(msg)
        return msg
    else:
        return "Die Transaktion wurde durch EVM rückgängig gemacht."

@app.route('/grantRightFranz')
@app.route('/grantRightJonas')
def grantRight():
    if(request.path == '/grantRightFranz'):
        person = "Franz"
        address = "0x862c0236e6010acc067987f67040a38f3b6c6e68get"
    if(request.path == '/grantRightJonas'):
        person = "Jonas"
        address = "0x4045c515879caac1cf40f633e9d8abf7eeed0108"
    value = request.args["right"] 
    txn = p1.giveRight(address,value)
    if(txn == 1):
        msg = person + "bekommt nun Zugriff auf" + str(value) +"."
        print(msg)
        return msg
    else:
        return "Die Transaktion wurde durch EVM rückgängig gemacht."
        
@app.route('/denyRightFranz')
@app.route('/denyRightJonas')
def denyRight():
    if(request.path == '/grantRightFranz'):
        person = "Franz"
        address = "0x862c0236e6010acc067987f67040a38f3b6c6e68"
    if(request.path == '/grantRightJonas'):
        person = "Jonas"
        address = "0x4045c515879caac1cf40f633e9d8abf7eeed0108"
    value = request.args["right"] 
    txn = p1.denyRight(address,value)
    if(txn == 1):
        msg = person + " hat keinen Zugriff mehr auf " + str(value) +"."
        print(msg)
        return msg
    else:
        return "Die Transaktion wurde durch EVM rückgängig gemacht."
        

#endregion

if __name__ == '__main__':
    app.run(host='localhost')
