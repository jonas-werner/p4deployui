########################################################
#          ___     _            _                   _
#         /   |   | |          | |                 (_)
#  _ __  / /| | __| | ___ _ __ | | ___  _   _ _   _ _
# | '_ \/ /_| |/ _` |/ _ \ '_ \| |/ _ \| | | | | | | |
# | |_) \___  | (_| |  __/ |_) | | (_) | |_| | |_| | |
# | .__/    |_/\__,_|\___| .__/|_|\___/ \__, |\__,_|_|
# | |                    | |             __/ |
# |_|                    |_|            |___/
#
########################################################
# Title:    p4deployui
# Version:  3.3
# Author:   Jonas Werner
########################################################

import os
import json
import uuid
from flask import Flask, render_template, redirect, request, url_for, make_response
import hashlib
import requests
import datetime
import random
# from types import SimpleNamespace



app = Flask(__name__)
my_uuid = str(uuid.uuid1())
offset = random.randint(0,500)
timestamp   = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')

# ENV
#############################################3

# Endpoints
urlDockerLocal = "192.168.2.93:5100/api/v1/docker"
urlVagrantLocal = "192.168.2.93:5200/api/v1/vagrant"



# View docker  images
@app.route('/dockerImageViewLocal')
def dockerImageViewLocal():

    url = "http://%s/info?command=getImages" % urlDockerLocal
    res = requests.get(url)

    results = res.json()

    content = make_response(render_template('deployCont.html', \
                        title1="Docker deployment on local system", \
                        bodyText1="Please make a selection from the available images below. ", \
                        results=results \
                        ))

    return content

# Stop docker containers
@app.route('/dockerContStopLocal', methods=['GET'])
def dockerContStopLocal():

    req = request.args
    container = req['container']

    url = "http://%s/stop?cont=%s" % (urlDockerLocal, container)
    res = requests.get(url)

    url = "http://%s/info?command=getCont" % urlDockerLocal
    res = requests.get(url)

    results = res.json()

    content = make_response(render_template('deployTable.html', \
                        title1="Currently active containers", \
                        bodyText1="Termination and / or deletion options available below. ", \
                        contLocation="Local cluster", \
                        results=results \
                        ))


    return content

# View docker containers
@app.route('/dockerContViewLocal')
def dockerContViewLocal():

    url = "http://%s/info?command=getCont" % urlDockerLocal
    res = requests.get(url)
    contLocal = res.json()

    url = "http://%s/info?command=getPubCont" % urlDockerLocal
    res = requests.get(url)
    contPub = res.json()

    content = make_response(render_template('deployTable.html', \
                        title1="Currently active containers", \
                        bodyText1="Termination and / or deletion options available below. ", \
                        contLocation="Local cluster", \
                        contLocal=contLocal, \
                        contPub=contPub \
                        ))

    return content


# Start docker containers
@app.route('/dockerContStart')
def dockerContStart():

    req = request.args
    cont = req['cont']
    location = req['location']

    url = "http://%s/start?cont=%s&location=%s" % (urlDockerLocal, cont, location)
    res = requests.get(url)

    url = "http://%s/info?command=getCont" % urlDockerLocal
    res = requests.get(url)
    contLocal = res.json()

    url = "http://%s/info?command=getPubCont" % urlDockerLocal
    res = requests.get(url)
    contPub = res.json()

    content = make_response(render_template('deployTable.html', \
                        title1="Currently active containers", \
                        bodyText1="Termination and / or deletion options available below. ", \
                        contLocation="Local cluster", \
                        contLocal=contLocal, \
                        contPub=contPub \
                        ))

    return content



# Deploy docker images
@app.route('/dockerContDeployLocal', methods=['GET','POST'])
def dockerContDeployLocal():

    if request.method == 'GET':

        url = "http://%s/info?command=getImages" % urlDockerLocal
        res = requests.get(url)

        results = res.json()

        content = make_response(render_template('deployCont.html', \
                            title1="Docker deployment on local system", \
                            bodyText1="Please make a selection from the available images below. ", \
                            results=results \
                            ))

    elif request.method == 'POST':

        dockerImage = request.form['dockerImage']

        try:
            dockerImage

        except NameError:
            print("dockerImage is undefined. Panicking!")

        else:
            title1 = "Deploying %s" % dockerImage
            bodyText1 = "Additional details required for deployment"

            if "grafana" in dockerImage.lower():
                portInt = "3000"
                portExt = "3000"
                name    = "Grafana"
                mode    = "detached"

            elif "influx" in dockerImage.lower():
                portInt = "1880"
                portExt = "1880"
                name    = "InfluxDB"
                mode    = "detached"

            content = make_response(render_template('deployCont2.html', \
                                title1=title1, \
                                bodyText1=bodyText1, \
                                dockerImage=dockerImage, \
                                portInt=portInt, \
                                portExt=portExt, \
                                name=name, \
                                mode=mode \
                                ))

    return content


# Deploy docker images
@app.route('/dockerContDeployLocalExec', methods=['POST'])
def dockerContDeployLocalExec():

    dockerImage = request.form['dockerImage']
    portInt     = request.form['portInt']
    portExt     = request.form['portExt']
    name        = request.form['name']
    mode        = request.form['mode']

    url = "http://%s/run?image=%s&name=%s&mode=%s&portInt=%s&portExt=%s" % (urlDockerLocal, dockerImage, name, mode, portInt, portExt)
    res = requests.get(url)

    results = res.text

    content = make_response(render_template('deployBasic.html', \
                        title1="Docker deployment on local system", \
                        bodyText1="Please provide additonal information below. ", \
                        results=results \
                        ))

    return content



# Vagrant VMs
###################################

def callVagrantApi(cmd):
    for cmd in cmdList:
        url = "http://%s/view?command=%s" % (urlVagrantLocal, cmd)
        res = requests.get(url)
        results = res.json()

        return results


# View VMs
@app.route('/vagrantVmViewLocal')
def vagrantVmViewLocal():

    cmdList = ['vms', 'runningvms', 'boxes']
    resultList = []

    for cmd in cmdList:
        url     = "http://%s/view?cmd=%s" % (urlVagrantLocal, cmd)
        res     = requests.get(url)
        resultList.append(res.json())

    content = make_response(render_template('deployTableVMs.html', \
                        title1="Vagrant VM overview", \
                        bodyText1="Current status of VMs on local cluster. ", \
                        vms=resultList[0], \
                        runningvms=resultList[1], \
                        boxes=resultList[2] \
                        ))

    return content


@app.route('/vagrantVmDeploy', methods=['GET','POST'])
def vagrantVmDeploy():

    if request.method == 'GET': # If it's a GET we show the available Vagrant images to choose from

        cmd     = "boxes"
        url     = "http://%s/view?cmd=%s" % (urlVagrantLocal, cmd)
        res     = requests.get(url)
        results = res.json()

        content = make_response(render_template('deployVM.html', \
                            title1="Vagrant VM deployment on local system", \
                            bodyText1="Please make a selection from the available images below. ", \
                            results=results \
                            ))

    elif request.method == 'POST': # If it's a POST we add the option to provide additional information

        boxImage    = request.form['boxImage']

        try:
            boxImage

        except NameError:
            print("boxImage is undefined. Panicking!")

        else:
            title1 = "Deploying %s" % boxImage
            bodyText1 = "Please be patient after submitting. It may take a minute for the VM to fully deploy. "

            content = make_response(render_template('deployVM2.html', \
                                title1=title1, \
                                bodyText1=bodyText1, \
                                boxImage=boxImage, \
                                boxName="", \
                                boxIp="192.168.11.xxx" \
                                ))

    return content


# Deploy docker images
@app.route('/vagrantVmDeployExec', methods=['POST'])
def vagrantVmDeployExec():

    boxImage    = request.form['boxImage']
    boxName     = request.form['boxName']
    boxIp       = request.form['boxIp']

    url = "http://%s/deploy?boxImage=%s&boxName=%s&boxIp=%s" % (urlVagrantLocal, boxImage, boxName, boxIp)
    res = requests.get(url)

    results = res.text

    content = make_response(render_template('deployBasic.html', \
                        title1="Vagrant VM deployment on local system", \
                        bodyText1="Log output below: ", \
                        results=results \
                        ))

    return content




if __name__ == "__main__":
	app.run(    debug=True, \
                host='0.0.0.0', \
                port=int(os.getenv('PORT', '5010')), threaded=True)
