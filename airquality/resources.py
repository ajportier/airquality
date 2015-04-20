from flask import jsonify, request
from flask.ext import restful
from flask.ext.restful import reqparse
from datetime import (datetime, timedelta)

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

        timestamp = datetime.now() - timedelta(seconds=args['seconds'])
        region = args['region']
        region_nodes = SensorNode.objects(region=region)
        readings = SensorReading.objects(node__in=region_nodes, created__gt=timestamp).exclude('id')

        return jsonify({'region':region, 'readings':readings})
