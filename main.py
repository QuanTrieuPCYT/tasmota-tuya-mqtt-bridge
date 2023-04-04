import paho.mqtt.client as mqtt
import functions
from functions import conf


# Define MQTT client parameters
mqtt_broker = conf("Authorization", "Address")
mqtt_port = int(conf("Authorization", "Port"))
mqtt_topic = conf("Configuration", "Topic")
mqtt_username = conf("Authorization", "User")
mqtt_password = conf("Authorization", "Password")


# Define MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"----------\nConnected to MQTT broker {mqtt_broker}.\nError code: {str(rc)}\n----------")
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    if msg.topic == mqtt_topic:
        if msg.payload.decode("utf-8") == "rgb":
            output = functions.rgbtoggle(conf("Devices", "tuyaid_rgb"), conf("Devices", "ip_rgb"), conf("Devices", "key_rgb"))
        elif msg.payload.decode("utf-8") == "desk":
            output = functions.switchtoggle(conf("Devices", "tuyaid_desk"), conf("Devices", "ip_desk"), conf("Devices", "key_desk"))
        elif msg.payload.decode("utf-8") == "decorate":
            output = functions.switchtoggle(conf("Devices", "tuyaid_decorate"), conf("Devices", "ip_decorate"), conf("Devices", "key_decorate"))
        elif msg.payload.decode("utf-8") == "alllights":
            output = functions.hass_toggle(conf("Devices", "hassid_lights"))
        elif msg.payload.decode("utf-8") == "climate":
            output = functions.hass_climate_toggle(conf("Devices", "hassid_climate"))
        elif msg.payload.decode("utf-8") == "fan":
            output = functions.hass_fan_toggle(conf("Devices", "hassid_fan"))
        else:
            output = "You requested an invalid device."
        print(f"Output:\n{output}")


# Create MQTT client instance and connect to broker
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)

# Start loop to receive MQTT messages
client.loop_forever()
