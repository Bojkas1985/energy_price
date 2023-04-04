import requests
import json
from datetime import datetime

from homeassistant.helpers.entity import Entity

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([EnergyPriceSensor()])

class EnergyPriceSensor(Entity):
    def __init__(self):
        self._state = None
        self._hours_prices = {}

    @property
    def name(self):
        return "energy_price_on_spot"

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return self._hours_prices

    def update(self):
        url = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)

            hours_prices = {}
            for point in data["data"]["dataLine"][1]["point"]:
                hour = int(point["x"])
                price = float(point["y"])
                hours_prices[hour] = price

            self._hours_prices = hours_prices
            current_hour = datetime.now().hour
            self._state = self._hours_prices.get(current_hour, None)
        else:
            self._state = None
