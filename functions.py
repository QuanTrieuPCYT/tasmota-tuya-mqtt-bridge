import configparser
import json

import requests
import tinytuya
from miio import Yeelight

config = configparser.ConfigParser()
config.read('config.conf')


def conf(bs1: str, bs2: str):
    return config.get(bs1, bs2)


headers = {'Authorization': 'Bearer ' + conf("Authorization", "HomeAssistantToken")}


# Tuya methods
def tuya_rgbtoggle(deviceid: str, ip: str, key: str, dpids: str):
    dpid_list = [int(x.strip()) for x in dpids.split(',')]

    # initialize a device on the first pass to send initial DPIDs
    d = tinytuya.BulbDevice(deviceid, ip, key)
    d.set_version(3.3)
    print(f"DPID Send Status: {d.updatedps(index=dpid_list)}")
    del d

    # after sending DPIDs, a device might not be usable until reinitialization
    d = tinytuya.BulbDevice(deviceid, ip, key)
    d.set_version(3.3)
    if d.status()['dps']['20']:
        d.turn_off()
    else:
        d.turn_on()
    return d.status()  # this time send the updated status


def tuya_switchtoggle(deviceid: str, ip: str, key: str, dpids: str, isnewversion: bool = False):
    version = 3.4 if isnewversion else 3.3
    dpid_list = [int(x.strip()) for x in dpids.split(',')]

    # initialize a device on the first pass to send initial DPIDs
    d = tinytuya.OutletDevice(deviceid, ip, key)
    d.set_version(version)
    print(f"DPID Send Status: {d.updatedps(index=dpid_list)}")
    del d

    # after sending DPIDs, a device might not be usable until reinitialization
    d = tinytuya.OutletDevice(deviceid, ip, key)
    d.set_version(version)
    if d.status()['dps']['1']:
        d.turn_off()
    else:
        d.turn_on()
    return d.status()  # this time send the updated status


# miot methods
def miot_toggle(ip: str, token: str):
    try:
        return Yeelight(ip, token).toggle()
    except Exception as e:
        return e


# Home Assistant methods
def hass_toggle(entity: str):
    url = f'{conf("Authorization", "BaseURL").rstrip("/")}/api/services/homeassistant/toggle'
    data = {
        'entity_id': entity
    }
    requests.post(url, headers=headers, json=data)
    urlstate = f'{conf("Authorization", "BaseURL").rstrip("/")}/api/states/{entity}'
    responsestate = requests.get(urlstate, headers=headers)
    return responsestate.text


def hass_fan_toggle(entity: str):
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


def hass_climate_toggle(entity: str):
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
