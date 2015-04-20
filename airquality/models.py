from airquality import db
from datetime import datetime

class SensorNode(db.Document):
    created = db.DateTimeField(required=True, default=datetime.now)
    sensor_id = db.StringField(required=True)
    approved = db.BooleanField(required=True, default=False)
    name = db.StringField()
    region = db.StringField()
    
    def __unicode__(self):
        return self.sensor_id
    

class SensorReading(db.Document):
    created = db.DateTimeField(required=True, default=datetime.now)
    node = db.ReferenceField(SensorNode, required=True)
    value = db.IntField(required=True)
    
    def __unicode__(self):
        return u'{} {}'.format(self.sensor, self.value)
