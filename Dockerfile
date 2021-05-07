FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.9 python3-pip


WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt -r dev-requirements.txt

CMD ["python3", "-u", "app.py"]
