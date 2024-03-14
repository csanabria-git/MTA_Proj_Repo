import os
from datetime import datetime
from flask import Flask, render_template, request
import sys
from subprocess import Popen, PIPE
import requests
import json
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
############################################################# Train section ################################################################################################

#Since I would need to run the same 6 commands for 36st station trains and they remain constsnat this line is to put all the commands into a dict
CommandDict={1:"underground stops N --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N",
             2:"underground stops N --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S",
             3:"underground stops D --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N",
             4:"underground stops D --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S",
             5:"underground stops R --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N",
             6:"underground stops R --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S",
             }
#This dict takes all the text from the commands and actually runs them in terminal and this is what sends back the train station ID + all the times i.e R36N 12:17 12:26 12:37 12:43 12:52 12:58 13:08 13:17 13:23 13:32
TrainTimesDict = {1:os.popen("underground stops N --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N").read(),
                  2:os.popen("underground stops N --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S").read(),
                  3:os.popen("underground stops D --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N").read(),
                  4:os.popen("underground stops D --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S").read(),
                  5:os.popen("underground stops R --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N").read(),
                  6:os.popen("underground stops R --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S").read(),        
                   }
# This dict will stores a particular train's destination, arrival times, and the current time. This line is to initialize it
#Individual Train Dicts
MasterDict = {1:[],2:[],3:[],4:[],5:[],6:[]}
NTrainDict = {1:[],2:[]}
DTrainDict = {1:[],2:[]}
RTrainDict = {1:[],2:[]}
#Function to Parse all information that the CLI commands in TrainDict spit out
def ParseTrainAndDestination(CommandDict,TrainTimesDict):
    #parse Train and destination from CLI command that calls from the MTA API
    currenttime = datetime.now()
    if "stops N" in CommandDict:
        train = 'N'
        if "R36N" in CommandDict:
            destination = "Astoria-Ditmars"
        if "R36S" in CommandDict:
            destination = "ConeyIsland-Stillwell"
    if "stops D" in CommandDict:
        train = 'D'
        if "R36N" in CommandDict:
            destination = "Norwood - 205"
        if "R36S" in CommandDict:
            destination = "ConeyIsland-Stillwell"
    if "stops R" in CommandDict:
        train = 'R'
        if "R36N" in CommandDict:
            destination = "Forest Hills - 71st"
        if "R36S" in CommandDict:
            destination = "Bay Ridge - 95th"
    #Put train times output into a variable of type string then remove spaces so its easier to parse
    TrainTimes=TrainTimesDict
    TrainTimes=TrainTimes.replace(" ", "")

    # Parse arrival1 and 2 from TrainTimes string
    arrival1=TrainTimes[4:9]
    arrival2=TrainTimes[9:14]
    arrival1 = parse(arrival1)
    arrival2 = parse(arrival2)
    arrival1 = int(timedelta.total_seconds(arrival1-currenttime) /60)
    arrival2 = int(timedelta.total_seconds(arrival2-currenttime) /60)

    TrainDict={"Train":train,
               "Dst":destination,
               "Train1":arrival1,
               "Train2":arrival2
               }
    return TrainDict
#For loop to populate MasterDict with all parsed train info
for i in CommandDict:
    MasterDict.update({i:ParseTrainAndDestination(CommandDict[i],TrainTimesDict[i])})
# Populate individual train Dicts
NTrainDict [1] = MasterDict [1]
NTrainDict [2] = MasterDict [2]
DTrainDict [1] = MasterDict[3]
DTrainDict [2] = MasterDict [4]
RTrainDict [1] = MasterDict[5]
RTrainDict [2] = MasterDict[6]
print(MasterDict)
############################################################# Bus section ################################################################################################
URLDict = {1:"https://bustime.mta.info/api/siri/stop-monitoring.json?key=1478dc0f-cec1-4f45-bef6-12a38f290a20&OperatorRef=MTA&MonitoringRef=305438&LineRef=MTA NYCT_B63",
           2:"https://bustime.mta.info/api/siri/stop-monitoring.json?key=1478dc0f-cec1-4f45-bef6-12a38f290a20&OperatorRef=MTA&MonitoringRef=305363&LineRef=MTA NYCT_B63"}
BusDict = {"Northbound":[],"Southbound":[]}

def ExtractBusTimes (URLDict):
    L0 = []
    L1 = []
    Currenttime = datetime.now()

    for i in URLDict:
        response =  requests.get(URLDict[i])
        JSON = response.json()
        for i in range(2):
            #DirectionRef is binary, 0 means Northbound towards Pier 6 and 1 means Southound towards Bay Ridge
            destination = JSON["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"][i]["MonitoredVehicleJourney"]["DirectionRef"]
            time = JSON["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"][i]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
            #Take stringthat has the next bus arrival time and parse it into its elements day/year/hours/minutes etc.
            time = parse(time)
            #Take the parsed time variable (now of type datetime.datetime and make it timezone unaware)
            time = time.replace(tzinfo=None)
            #Compare now time variable with Currenttime variable (which is also a datetime.datetime)
            time = int(timedelta.total_seconds(time-Currenttime) /60)
            #Depending on the direction (0 or 1/ North/South) I want the corresponding list to be updated with the time. L0 gets updates when direction is 0 and vice versa for L1
            if destination == "0":
                L0.insert(i,time)
            if destination == "1":
                L1.insert(i,time)
    #This conditional will check which list is empty, whichever one is not empty will get put into the proper key of BusDict
        if not L0:
            BusDict["Southbound"] = L1
        else:
            BusDict["Northbound"] = L0

ExtractBusTimes(URLDict)
print(BusDict)


