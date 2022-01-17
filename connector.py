import web3
from web3.middleware import geth_poa_middleware


class web3Connection:
    def __init__(self):
        self.my_account = "0xc4a367797DF1C21e911f02CCBCd79bc0A9E60224"
        self.my_pwd = "test"
        self.w3 = web3.Web3(web3.Web3.HTTPProvider("http://141.19.96.203:8545")) #im VPN
        self.w3.geth.personal.unlock_account(self.my_account,self.my_pwd)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer = 0) # für Testnet mit POA
        print("Connection to Server: "+str(self.w3.isConnected()))
        self.myContract = self.w3.eth.contract(address = "0x74c0662F3567f6FDE63e52bbCBF11Db92a45946a", abi=controlABI)
        self.controlID = 0

   
    def getTargetValue(self,aktorType):
        self.loginUser()
        temp = self.myContract.functions
        print("getTargetValue")
        if aktorType == "shutters":
            return temp.getTargetShuttersState().call({"from":self.my_account})
        if aktorType == "window":
            return temp.getTargetWindowState().call({"from":self.my_account})
        if aktorType == "temperature":
            return temp.getTargetTemperature(self.controlID).call({"from":self.my_account})

    def getCurrentValue(self,aktorType):
        self.loginUser()
        temp = self.myContract.functions
        if aktorType == "shutters":
            return temp.getCurrentShuttersState().call({"from":self.my_account})
        if aktorType == "window":
            return temp.getCurrentWindowState().call({"from":self.my_account})
        if aktorType == "temperature":
            return temp.getCurrentTemp(self.controlID).call({"from":self.my_account})
        #co2 and lightangle

    def setTargetValue(self,val,aktorType):
        self.loginUser()
        temp = self.myContract.functions
        if aktorType == "shutters":
            #val is of type bool
            txn = temp.setTargetShuttersState(val).transact({"from":self.my_account})
        if aktorType == "window": 
            #val is of type bool
            txn = temp.setTargetWindowState(val).transact({"from":self.my_account})
        if aktorType == "temperature":
            #val is of type int
            txn = temp.setTargetTemp(val,self.controlID).transact({"from":self.my_account})

        receipt = self.w3.eth.wait_for_transaction_receipt(txn)
        return receipt["status"]

    def setTargetValueWithTime(self,time):
        self.loginUser()
        temp = self.myContract.functions
        targetValue = temp.getTargetTemp(self.tempControlId).call({"from":self.my_account})
        txn = temp.setTargetTempTimer(targetValue+5,self.controlID,time).transact({"from":self.my_account})
        receipt = self.w3.eth.wait_for_transaction_receipt(txn)
        return receipt["status"]

    def setCurrentValue(self,val,aktorType):
        self.loginUser()
        #only for sensors
        temp = self.myContract.functions
        if aktorType == "shutters":
            #val is of type bool
            txn = temp.setCurrentShuttersState(val).transact({"from":self.my_account})
        if aktorType == "window": 
            #val is of type bool
            txn = temp.setCurrentWindowState(val).transact({"from":self.my_account})
        if aktorType == "temperature":
            #val is of type int
            txn = temp.setCurrentTemp(val,self.controlID).transact({"from":self.my_account})
        receipt = self.w3.eth.wait_for_transaction_receipt(txn)
        return receipt["status"]

    def giveRight(person,right):
        self.loginUser()
        temp = self.myContract.functions
        if(person == "Franz"):
            address = ""
            txn = temp.grantRight(address,right).transact({"from":self.my_account})
        if(person == "Jonas"):
            address = ""
            txn = temp.grantRight(address,right).transact({"from":self.my_account})
        receipt = self.w3.eth.wait_for_transaction_receipt(txn)
        return receipt["status"]

    def denyRight(person,right):
        self.loginUser()
        temp = self.myContract.functions
        if(person == "Franz"):
            address = ""
            txn = temp.denyRights(address,right).transact({"from":self.my_account})
        if(person == "Jonas"):
            address = ""
            txn = temp.denyRights(address,right).transact({"from":self.my_account})
        receipt = self.w3.eth.wait_for_transaction_receipt(txn)
        return receipt["status"]

    def loginUser(self):
        self.w3.geth.personal.unlock_account(self.my_account,self.my_pwd)


