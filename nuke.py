#!/usr/bin/env python

from airquality import db
from airquality.models import *

for node in SensorNode.objects():
    node.delete()
    
for reading in SensorReading.objects():
    reading.delete()