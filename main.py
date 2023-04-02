import configparser
import paho.mqtt.client as mqtt
import functions

config = configparser.ConfigParser()
config.read('config.conf')


# Define MQTT client parameters
mqtt_broker = config.get("Authorization", "Address")
mqtt_port = int(config.get("Authorization", "Port"))
mqtt_topic = config.get("Configuration", "Topic")
mqtt_username = config.get("Authorization", "User")
mqtt_password = config.get("Authorization", "Password")


# Define MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"----------\nConnected to MQTT broker {mqtt_broker}.\nError code: {str(rc)}\n----------")
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    if msg.topic == mqtt_topic:
        if msg.payload.decode("utf-8") == "rgb":
            output = functions.rgbtoggle(config.get("Devices", "tuyaid_rgb"), config.get("Devices", "ip_rgb"), config.get("Devices", "key_rgb"))
        elif msg.payload.decode("utf-8") == "desk":
            output = functions.switchtoggle(config.get("Devices", "tuyaid_desk"), config.get("Devices", "ip_desk"), config.get("Devices", "key_desk"))
        elif msg.payload.decode("utf-8") == "decorate":
            output = functions.switchtoggle(config.get("Devices", "tuyaid_decorate"), config.get("Devices", "ip_decorate"), config.get("Devices", "key_decorate"))
        elif msg.payload.decode("utf-8") == "alllights":
            output = functions.hass_toggle(config.get("Devices", "hassid_alllights"))
        elif msg.payload.decode("utf-8") == "climate":
            output = functions.hass_climate_toggle(config.get("Devices", "hassid_climate"))
        elif msg.payload.decode("utf-8") == "fan":
            output = functions.hass_fan_toggle(config.get("Devices", "hassid_fan"))
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
