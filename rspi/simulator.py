#!/usr/bin/env python

from requests.exceptions import ConnectionError
from time import sleep

import requests
import json
import random
import argparse

parser = argparse.ArgumentParser(description='Send sensor readings to central node')
parser.add_argument('--config', required=True)


def gen_identifier():
   return ''.join([random.choice('0123456789ABCDEF') for x in range(10)])


def send_value(val):
    uri = 'http://127.0.0.1:5000/api/gas/reading/add'
    data = {
        'value':val,
        'sensor_id':sensor_id
        }
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(uri, data=json.dumps(data), headers=headers)
        print "{} {}".format(str(val),r.status_code)
    except ConnectionError:
        print "Error connecting to server"
        pass


if __name__ == '__main__':
    
    args, remaining_argv = parser.parse_known_args()
    sensor_id = ''
    try:
        f = open(args.config, 'r')
        sensor_id = f.read()
        f.close()
    except IOError:
        sensor_id = gen_identifier()
        f = open(args.config, 'wb')
        f.write(sensor_id)
        f.close
            
    while True:
        try:
            send_value(random.randint(1,10))
            sleep(1)
        except KeyboardInterrupt:
            exit()