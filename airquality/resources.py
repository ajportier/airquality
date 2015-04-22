from flask import jsonify, request
from flask.ext import restful
from flask.ext.restful import reqparse
from datetime import (datetime, timedelta)
import time

from airquality import (app, api)
from models import (SensorNode, SensorReading)


basic_parser = reqparse.RequestParser()
basic_parser.add_argument('sensor_id', type=str, required=True)


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


class GetGasReading(restful.Resource):
    def get(self):
        parser = basic_parser.copy()
        parser.add_argument('seconds', type=int)
        args = parser.parse_args()
        
        timestamp = datetime.now() - timedelta(seconds=args['seconds'])
        node = SensorNode.objects.get(sensor_id=args['sensor_id'])
        readings = SensorReading.objects(node=node, created__gt=timestamp).exclude('id')

        return jsonify({'node':node.sensor_id,'readings':readings})


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
        while current_interval > 0:
            val = 0
            current_timestamp = timestamp - timedelta(seconds=current_interval)
            current_readings = SensorReading.objects(node__in=region_nodes, created__gt=current_timestamp).exclude('id')
            if len(current_readings) > 0:
                for reading in current_readings:
                    val += reading.value
                val = val / len(current_readings)
                current_interval += -1
                
                # Generate a POSIX timestamp of this averaged data set with millisecond precision
                posix_time = int(time.mktime(current_timestamp.timetuple())*1000 + current_timestamp.microsecond/1000)
                readings.append({'created':{'$date':posix_time},'value':val})

        return jsonify({'region':region, 'readings':readings})
