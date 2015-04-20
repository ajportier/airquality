from flask import Flask
from flask.ext import restful
from flask.ext.mongoengine import MongoEngine

from config import Config

app = Flask(__name__)
app.config.from_object(config.Config)

db = MongoEngine(app)
api = restful.Api(app=app)

import airquality.views