import json
import requests
import tinytuya
import configparser

config = configparser.ConfigParser()
config.read('config.conf')


def conf(bs1, bs2):
    return config.get(bs1, bs2)


headers = {'Authorization': 'Bearer ' + conf("Authorization", "HomeAssistantToken")}


# I modified these to return the status of the device after toggling it
# Nothing serious, right?


def rgbtoggle(id, ip, key):
    d = tinytuya.BulbDevice(id, ip, key)
    d.set_version(3.3)
    data = d.status()
    if data['dps']['20']:
        d.turn_off()
    else:
        d.turn_on()
    return data


def switchtoggle(id, ip, key):
    d = tinytuya.OutletDevice(id, ip, key)
    d.set_version(3.3)
    data = d.status()
    if data['dps']['1']:
        d.turn_off()
    else:
        d.turn_on()
    return data


def hass_toggle(entity):
    url = f'{conf("Authorization", "BaseURL").rstrip("/")}/api/services/homeassistant/toggle'
    data = {
        'entity_id': entity
    }
    requests.post(url, headers=headers, json=data)
    urlstate = f'{conf("Authorization", "BaseURL").rstrip("/")}/api/states/{entity}'
    responsestate = requests.get(urlstate, headers=headers)
    return responsestate.text


def hass_fan_toggle(entity):
    payload = json.dumps({
        "entity_id": f"{entity}",
    })
    response = requests.get(f'{conf("Authorization", "BaseURL").rstrip("/")}/api/states/{entity}',
                            headers=headers)
    # If the fan is currently on, send a turn_off command
    if response.json()["state"] == "on":
        requests.post(conf("Authorization", "BaseURL").rstrip("/") + "/api/services/fan/turn_off",
                      headers=headers, data=payload)
    # If the fan is currently off, send a turn_on command
    else:
        requests.post(conf("Authorization", "BaseURL").rstrip("/") + "/api/services/fan/turn_on",
                      headers=headers, data=payload)
    return requests.get(f'{conf("Authorization", "BaseURL").rstrip("/")}/api/states/{entity}',
                        headers=headers).text


def hass_climate_toggle(entity):
    payload = json.dumps({
        "entity_id": f"{entity}",
    })
    response = requests.get(f'{conf("Authorization", "BaseURL").rstrip("/")}/api/states/{entity}',
                            headers=headers)
    # If the climate is currently off, send a turn_on command
    if response.json()["state"] == "off":
        requests.post(conf("Authorization", "BaseURL").rstrip("/") + "/api/services/climate/turn_on",
                      headers=headers, data=payload)
    # If the climate is currently on (its state will not be 'on', instead it will be one of the modes, then send a
    # turn_off command)
    else:
        requests.post(conf("Authorization", "BaseURL").rstrip("/") + "/api/services/climate/turn_off",
                      headers=headers, data=payload)
    return requests.get(f'{conf("Authorization", "BaseURL").rstrip("/")}/api/states/{entity}',
                        headers=headers).text
