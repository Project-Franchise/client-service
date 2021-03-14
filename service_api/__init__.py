from flask import Flask
from flask_restful import Api, Resource

flask_app = Flask(__name__)
api_ = Api(flask_app)

from . import views