FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.9 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3"]

CMD ["app.py"]