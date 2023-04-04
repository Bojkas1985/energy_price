import logging
import requests
import json
from datetime import datetime
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([EnergyPriceSensor(),
                  CheapestHoursSensor(2, True),
                  CheapestHoursSensor(3, True),
                  CheapestHoursSensor(4, True),
                  CheapestHoursSensor(2, False),
                  CheapestHoursSensor(3, False),
                  CheapestHoursSensor(4, False)])

class EnergyPriceSensor(Entity):

    def __init__(self):
        self._name = "energy_price_bojkas"
        self._state = None
        self._attributes = {}
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

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
            _LOGGER.error("Failed to update energy price.")


class CheapestHoursSensor(Entity):

    def __init__(self, hours_count, cheapest=True):
        self._hours_count = hours_count
        self._cheapest = cheapest
        self._name = f"{'cheapest' if cheapest else 'most_expensive'}_{hours_count}_hours"
        self._state = None
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

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

            cumulative_prices = []
            for i in range(len(hours_prices) - self._hours_count + 1):
                cumulative_price = sum(hours_prices[i + j] for j in range(self._hours_count))
                cumulative_prices.append((i, cumulative_price))

            sorted_cumulative_prices = sorted(cumulative_prices, key=lambda x: x[1], reverse=not self._cheapest)
            self._state = sorted_cumulative_prices[0][0]
        else:
            _LOGGER.error("Failed to update energy price.")
