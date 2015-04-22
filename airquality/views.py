from flask import (request, render_template)
from flask.ext.wtf import Form
from wtforms.fields import (TextField, BooleanField)

from airquality import (app, api)
from resources import *
from models import *


class SensorApproveEditForm(Form):
    approve = BooleanField()
    name = TextField('Name')
    region = TextField('Region')


''' Generates a new sensor_form dict for approvals and edits '''
def generateApproveEditSensorForm(sensor):
    form = SensorApproveEditForm(prefix=str(sensor))
    sensor_form = {'sensor':sensor, 'form':form}
    return sensor_form


''' Fills in the sensor_form data fields with values from MongoDB '''
def populateApproveEditSensorForm(sensor_form):
    sensor = sensor_form['sensor']
    form = sensor_form['form']
    form.approve.data = sensor.approved
    form.name.data = sensor.name
    form.region.data = sensor.region


''' Sends a sensor_node object and a form and updates the MongoDB object in place '''
def updateSensorByForm(sensor, form):
    sensor.update(set__approved=form.approve.data)
    sensor.update(set__name=form.name.data)
    sensor.update(set__region=form.region.data)
    sensor.save()


api.add_resource(AddGasReading, '/api/gas/reading/add')
api.add_resource(GetGasReading, '/api/gas/reading/get')
api.add_resource(GetRegionReading, '/api/region/reading/get')


@app.route('/')
def index():
    sensors = SensorNode.objects(approved=True)
    regions = SensorNode.objects.distinct('region')
    return render_template('index.html', sensors=sensors, regions=regions)


@app.route('/graph', methods=['POST'])
def makeGraph():
    sensor_ids = request.form.getlist('sensor')
    regions = request.form.getlist('region')
    sensors = []
    for sensor in sensor_ids:
        s = SensorNode.objects.get(sensor_id = sensor)
        sensors.append(s)
    return render_template('graph.html', sensors=sensors, regions=regions)


''' Generates the view for the Admin page and handles forms '''
@app.route('/admin', methods=['GET','POST'])
def adminPage():
    
    #1. Generate forms for approved and unapproved sensor_nodes
    approved = []
    for sensor in SensorNode.objects(approved=True):
        approved.append(generateApproveEditSensorForm(sensor))

    unapproved = []
    for sensor in SensorNode.objects(approved=False):
        unapproved.append(generateApproveEditSensorForm(sensor))
    
    #2. Test if we are handling form submission
    if request.method == 'POST':

        #2a. If the user clicked "approve" look for unapproved sensor_nodes and update
        if request.form.has_key('approve'):
            for sensor_form in unapproved:
                form = sensor_form['form']
                sensor = sensor_form['sensor']
                if form.validate_on_submit():
                    updateSensorByForm(sensor, form)
                    if form.approve.data == True:
                        unapproved = [x for x in unapproved if not x['sensor'] == sensor]
                        approved.append(generateApproveEditSensorForm(sensor))

        #2b. If the user clicked "edit" look for approved sensor_nodes and edit in place
        if request.form.has_key('edit'):
            for sensor_form in approved:
                form = sensor_form['form']
                sensor = sensor_form['sensor']
                if form.validate_on_submit():
                    updateSensorByForm(sensor, form)
                    if form.approve.data == False:
                        approved = [x for x in approved if not x['sensor'] == sensor]
                        unapproved.append(generateApproveEditSensorForm(sensor))

    #3. If this is a GET, fill in the "approved" sensor node forms with values from the database
    else:
        for sensor_form in approved:
            populateApproveEditSensorForm(sensor_form)
    
    #4. Send everything off to get rendered
    return render_template('admin.html', approved = approved, unapproved = unapproved)
