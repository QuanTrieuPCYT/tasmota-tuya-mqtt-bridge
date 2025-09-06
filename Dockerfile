FROM python:3.13-alpine
WORKDIR /tasmota-tuya-mqtt-bridge
COPY . .
RUN adduser -D tasmqtt
USER tasmqtt
RUN pip3.13 install -r ./requirements.txt
CMD ["python3.13", "./main.py"]1
