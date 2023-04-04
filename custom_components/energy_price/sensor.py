import logging
import requests
import json
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DOMAIN = "energy_price"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([EnergyPriceSensor()])


class EnergyPriceSensor(Entity):

    def __init__(self):
        self._state = None
        self._attributes = {}
        self.update()

    @property
    def name(self):
        return "Energy Price"

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return self._attributes

    @property
    def unit_of_measurement(self):
        return "CZK/MWh"

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
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

            self._state = hours_prices.get(datetime.now().hour)
            self._attributes = hours_prices
        else:
            _LOGGER.error("Failed to fetch data.")
