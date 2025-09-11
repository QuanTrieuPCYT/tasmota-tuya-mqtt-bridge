FROM python:3.13-alpine AS builder
WORKDIR /builder
COPY requirements.txt .
RUN pip3.13 -r ./requirements.txt

FROM python:3.13-alpine
WORKDIR /tasmota-tuya-mqtt-bridge
COPY . .
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
RUN adduser -D tasmqtt
USER tasmqtt
CMD ["python3.13", "./main.py"]
