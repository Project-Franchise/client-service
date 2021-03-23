from service_api import flask_app
import os

if __name__ == "__main__":
    flask_app.run(debug=True,
                  port=os.environ['CS_HOST_PORT'],
                  host=os.environ['CS_HOST_IP'])
