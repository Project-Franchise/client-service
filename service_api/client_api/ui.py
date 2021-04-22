from flask import render_template
from service_api import flask_app
from flask_restful import Resource


@flask_app.route('/main')
def index():
    return render_template('index.html')

