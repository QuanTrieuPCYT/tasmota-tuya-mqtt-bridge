FROM python:3.14-alpine AS builder
WORKDIR /builder
COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev linux-headers
RUN CFLAGS="-Wno-error=int-conversion" pip3.14 install -r ./requirements.txt

FROM python:3.14-alpine
WORKDIR /tasmota-tuya-mqtt-bridge
COPY . .
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
RUN adduser -D tasmqtt
USER tasmqtt
CMD ["python3.14", "./main.py"]