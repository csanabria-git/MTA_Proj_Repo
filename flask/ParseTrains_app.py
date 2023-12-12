import os
from datetime import datetime
from flask import Flask, render_template, request
import sys
from subprocess import Popen, PIPE

#Since I would need to run the same 6 commands for 36st station trains and they remain constsnat this line is to put all the commands into a dict
CommandDict={1:"underground stops N --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N",
             2:"underground stops N --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S",
             3:"underground stops D --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N",
             4:"underground stops D --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S",
             5:"underground stops R --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36N",
             6:"underground stops R --api-key Yes7tAol8sKfqd1cGfF26W1C2nWTFiZ1mM8Z5uG8 | grep R36S",
             }
#This dict takes all the text from the commands and actually runs them in terminal and this is what sends back the train station ID + all the times i.e R36N 12:17 12:26 12:37 12:43 12:52 12:58 13:08 13:17 13:23 13:32
TrainTimesDict = {1:os.popen(CommandDict[1]).read(),
                  2:os.popen(CommandDict[2]).read(),
                  3:os.popen(CommandDict[3]).read(),
                  4:os.popen(CommandDict[4]).read(),
                  5:os.popen(CommandDict[5]).read(),
                  6:os.popen(CommandDict[6]).read(),        
                   }
# This dict will stores a particular train's destination, arrival times, and the current time. This line is to initialize it
MasterDict = {1:[],
                   2:[],
                   3:[],
                   4:[],
                   5:[],
                   6:[],
                   }
# Function to get current time and parse it into HH:MM (returns a string)
def GetCurrentTime():
    currenttime = datetime.now()
    currenttime = currenttime.strftime("%H:%M")
    return currenttime
#Function to Parse all information that the CLI commands in TrainDict spit out
def ParseTrainAndDestination(CommandDict,TrainTimesDict,CurrentTime):
    #parse Train and destination from CLI command that calls from the MTA API
    if "stops N" in CommandDict:
        train = 'N'
        if "R36N" in CommandDict:
            destination = "Astoria-Ditmars Blvd"
        if "R36S" in CommandDict:
            destination = "ConeyIsland-Stillwell Ave"
    if "stops D" in CommandDict:
        train = 'D'
        if "R36N" in CommandDict:
            destination = "Norwood - 205 St"
        if "R36S" in CommandDict:
            destination = "ConeyIsland-Stillwell Ave"
    if "stops R" in CommandDict:
        train = 'R'
        if "R36N" in CommandDict:
            destination = "Forest Hills - 71st Av"
        if "R36S" in CommandDict:
            destination = "Bay Ridge - 95 St"
    #Put train times output into a variable of type string then remove spaces so its easier to parse
    TrainTimes=TrainTimesDict
    TrainTimes=TrainTimes.replace(" ", "")
    # Parse arrival1 and 2 from TrainTimes string
    arrival1=TrainTimes[4:9]
    arrival2=TrainTimes[9:14]

    a1Hours = int(arrival1[0:2])
    a1Minutes = int(arrival1[3:5])
    a2Hours = int(arrival2[0:2])
    a2Minutes = int(arrival2[3:5])
    cHours = int(CurrentTime[0:2])
    cMinutes = int(CurrentTime[3:5])
    OneHour = 60
    if a1Hours == cHours:
        FirstTrain = a1Minutes - cMinutes
    else:
        FirstTrain = a1Minutes + OneHour - cMinutes
    if a2Hours == cHours:
        SecondTrain = a2Minutes -cMinutes
    else:  
        SecondTrain = a2Minutes + OneHour - cMinutes
    TrainDict={"Train":train,
               "Dst":destination,
               "A1":arrival1,
               "A2":arrival2,
               "CTime":CurrentTime,
               "Train 1":FirstTrain,
               "Train 2":SecondTrain
               }
    return TrainDict
#For loop to populate MasterDict with all parsed train info
for i in CommandDict:
    MasterDict.update({i:ParseTrainAndDestination(CommandDict[i],TrainTimesDict[i],GetCurrentTime())})

#Flask web app
from flask import Flask

app = Flask(__name__)

@app.route('/')
def my_route():
  i = 2
  train = MasterDict[i]["Train"]
  destination= MasterDict[i]["Dst"]
  nexttrain = MasterDict[i]["Train 1"]
  return render_template('index.html', train=train, destination=destination, nexttrain=nexttrain)
                                 
