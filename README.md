# Client-service
## Installation

Install with pip:

```
> pip install -r requirements.txt
```

Before running shell commands, set next environment variables:
 - ```DATABASE_URL``` by template ```postgresql+psycopg2://<user>:<password>t@localhost/<DB_name>```
 - ``` CS_HOST_PORT, CS_HOST_IP``` from [.flask_env](.flask_env)

### How to set environment variables and activate venv:
In bash:
```
# set environment variables
export VARIABLE=value

# set environment variables from file (exmpl. from [.flask_env](.flask_env))
export $(xargs < .flask_env)

# activate venv (considering you are at the same level as venv)
source ./venv/bin/activate
```

In CMD:
```
# set environment variables
set VARIABLE=value

# activate venv (considering you are at the same level as venv)
./venv/Scripts/activate.bat
```

In PowerShell:
```
# set environment variables
$env:VARIABLE="value"

# activate venv (considering you are at the same level as venv)
./venv/Scripts/Activate.ps1
```


To create user run
```
psql -U postgres
```
Create your user and grant the necessary permissions
```angular2html
CREATE USER username WITH PASSWORD password;
```

## Alembic
To migrate, all what is needed is to run
```
alembic upgrade head
```
To make new migrations
```
alembic revision --autogenerate -m "Migration message"
```
## Run app
Python version: 3.9.2
```
python manage.py runserver
```

## Run Celery
To run celery_app use command:
```angular2html
python manage.py run_celery
```
You can use the flower extension to demonstrate the work of celery.
To do this, run it with the next command and go to the specified address
```angular2html
celery -A service_api.celery_app flower
```

## Flask Application Structure
```
.
├── service_api/
│   ├─── __init__.py
│   ├─── models.py
│   └─── client_api/
│        ├─── __init__.py
│        └─── resources.py
│   └─── grabbing_api/
│        └─── __init__.py
├── alembic/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│        ├── 0f0002bf91cc_initial_migration.py
│        └── ...
├── __init__.py
├── app.py
├── setup.py
├── config.py
├── alembic.ini
├── requirements.txt
├── dev-requirements.txt
├── Dockerfile
├── README.md
├── .flak_env
└── .gitignore

```
