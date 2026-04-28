#import asyncio
import configparser
import json

#import aioesphomeapi
import requests
from miio import Yeelight

config = configparser.ConfigParser()
config.read('config.conf')


def conf(bs1: str, bs2: str):
    return config.get(bs1, bs2)


headers = {'Authorization': 'Bearer ' + conf("Authorization", "HomeAssistantToken")}


# ESPHome methods
"""
def esphome_toggle(ip: str, key: str, device_name: str):
    async def _toggle_task():
        client = aioesphomeapi.APIClient(
            address=ip,
            port=6053,
            password="",
            noise_psk=key
        )

        await client.connect(login=True)

        try:
            entities_services = await client.list_entities_services()
            entities = entities_services[0] if isinstance(entities_services, tuple) else entities_services

            target_light = None
            for entity in entities:
                if isinstance(entity, aioesphomeapi.LightInfo) and (
                        entity.name == device_name or entity.object_id == device_name
                ):
                    target_light = entity
                    break

            if not target_light:
                return {"error": f"Light '{device_name}' not found on {ip}"}

            current_state = None
            state_event = asyncio.Event()

            def state_callback(state):
                nonlocal current_state
                if state.key == target_light.key:
                    current_state = state
                    state_event.set()

            unsubscribe = client.subscribe_states(state_callback)

            try:
                await asyncio.wait_for(state_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                return {"error": "Timeout waiting for current device state"}
            finally:
                if callable(unsubscribe):
                    unsubscribe()

            new_state = not current_state.state
            client.light_command(key=target_light.key, state=new_state)

            return {
                "device": target_light.name,
                "state": "on" if new_state else "off"
            }

        finally:
            await client.disconnect()

    return asyncio.run(_toggle_task())
"""


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
