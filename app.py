from flask import Flask, request, Response, jsonify
from flask import json
from init_pro import *

# from flaskext.mysql import MySQL

from database import mysql

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Vanhuy@123'
app.config['MYSQL_DATABASE_DB'] = 'linktest'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
def hello_world():
    return 'Job Recommend System! Ahihii'


# --- GET ---
@app.route('/job-to-candidate/<idJob>', methods=['GET'])
def getListCandidate(idJob):
    pprint(idJob)
    listCandidate = selectForJob(idJob)
    return jsonify(listCandidate), 200


@app.route('/candidate-to-job/<idCandidate>', methods=['GET'])
def getListJob(idCandidate):
    pprint(idCandidate)
    listJob = selectForCandidate(idCandidate)
    return jsonify(listJob), 200


# --- COMPUTE ---
@app.route('/job-vs-candidate', methods=['POST'])
def computeJob():
    if request.method == 'POST':
        job = request.json
        jobVsCandidate(job)
        return jsonify({"Success": True}), 200


@app.route('/candidate-vs-job', methods=['POST'])
def computeCandidate():
    if request.method == 'POST':
        candidate = request.json
        candidateVsPost(candidate)
        return jsonify({"Success": True}), 200


if __name__ == '__main__':
    app.run()
