import requests
import json
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta


#key ='1478dc0f-cec1-4f45-bef6-12a38f290a20'
#API calls, one for Northbound B63 buses toward Pier 6 and Southbound towards Bay Ridge
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


