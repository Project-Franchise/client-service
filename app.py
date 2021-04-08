"""
Runs flask app
"""
import os

from service_api import flask_app

if __name__ == "__main__":
    flask_app.run(port=os.environ["CS_HOST_PORT"],
                  host=os.environ["CS_HOST_IP"])
