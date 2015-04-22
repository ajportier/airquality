from flask import jsonify, request
from flask.ext import restful
from flask.ext.restful import reqparse
from datetime import (datetime, timedelta)
import time

from airquality import (app, api)
from models import (SensorNode, SensorReading)


basic_parser = reqparse.RequestParser()
basic_parser.add_argument('sensor_id', type=str, required=True)


''' Adds a gas reading to the database using POST data from a RESTful call '''
class AddGasReading(restful.Resource):
    def post(self):
        parser = basic_parser.copy()
        parser.add_argument('value', type=int, required=True)
        args = parser.parse_args()
        node, created = SensorNode.objects.get_or_create(sensor_id=args['sensor_id'])
        reading = SensorReading(node=node, value=args['value'])

        if node.approved:
            reading.save()
            return {'response':'created'}, 201
        else:
            return {'response':'forbidden'}, 403


''' Gets all gas reading data points for a single node over the requested seconds '''
class GetGasReading(restful.Resource):
    def get(self):
        parser = basic_parser.copy()
        parser.add_argument('seconds', type=int)
        args = parser.parse_args()
        
        timestamp = datetime.now() - timedelta(seconds=args['seconds'])
        node = SensorNode.objects.get(sensor_id=args['sensor_id'])
        readings = SensorReading.objects(node=node, created__gt=timestamp).exclude('id')

        return jsonify({'node':node.sensor_id,'readings':readings})


''' Gets the average of all the data points in a region over the given interval, one value for
    each second of the interval. Does not include node identifier in the response (since it's a grouping)
    TODO: Figure out why this is coming back as localtime and not UTC
'''
class GetRegionReading(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('seconds', type=int)
        parser.add_argument('region', type=str, required=True)
        args = parser.parse_args()

        timestamp = datetime.now()
        current_interval = args['seconds']
        region = args['region']
        region_nodes = SensorNode.objects(region=region)
        readings = []
        
        # Stepping down from the requested number of seconds, pull
        # all values between the current number of seconds and the next second
        while current_interval > 0:
            val = 0
            current_timestamp = timestamp - timedelta(seconds=current_interval)
            next_timestamp = current_timestamp + timedelta(seconds=1)
            
            current_readings = SensorReading.objects(node__in=region_nodes,
                created__gt=current_timestamp,
                created__lte=next_timestamp).exclude('id')

            # If any readings exist for this second, average them and generate a single value
            if len(current_readings) > 0:
                for reading in current_readings:
                    val += reading.value
                val = val / len(current_readings)
                
                # Generate a POSIX timestamp of this averaged data set with millisecond precision
                posix_time = int(time.mktime(current_timestamp.timetuple())*1000 + current_timestamp.microsecond/1000)
                
                # ...And add it to the return
                readings.append({'created':{'$date':posix_time},'value':val})
            
            # Decrement the seconds interval we are looking at
            current_interval += -1

        return jsonify({'region':region, 'readings':readings})