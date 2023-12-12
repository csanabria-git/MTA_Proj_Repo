from flask import Flask, render_template, request
import sys
from subprocess import Popen, PIPE
app = Flask(__name__)
@app.route('/')
"""def Train(train=train,MinsToTrain1=MinutesToNextTrain(arrival1,currenttime),MinsToTrain2=MinutesToNextTrain(arrival2,currenttime), destination=destination):
    return render_template('index.html', MinsToTrain1=MinsToTrain1, MinsToTrain2=MinsToTrain2, train=train, destination=destination )

app.run()
flask --app flask_app.py run to run the app
"""
