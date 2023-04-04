import logging
import requests
import json
from datetime import datetime
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    energy_price_sensor = EnergyPriceSensor()
    energy_price_sensor.update()
    lowest_cumulative_price_sensor = LowestCumulativePriceSensor(energy_price_sensor.attributes)
    highest_cumulative_price_sensor = HighestCumulativePriceSensor(energy_price_sensor.attributes)
    add_entities([energy_price_sensor, lowest_cumulative_price_sensor, highest_cumulative_price_sensor])

class EnergyPriceSensor(Entity):

    def __init__(self):
        self._name = "energy_price_bojkas_ib"
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

            self._state = hours_prices.get(datetime.now().hour-1)
            self._attributes = {
                "hourly_prices": hours_prices,
            }
        else:
            _LOGGER.error("Failed to update energy price.")

class LowestCumulativePriceSensor(Entity):

    def __init__(self, attributes):
        self._name = "2h_lowest_cumulative_price_ib"
        self._state = None
        self._attributes = attributes
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        if self._attributes:
            hours_prices = self._attributes["hourly_prices"]
            cumulative_prices = {}
            for hour in range(0, 23):
                cumulative_prices[hour] = hours_prices.get(hour, 0) + hours_prices.get(hour + 1, 0)

            lowest_hours = sorted(cumulative_prices, key=cumulative_prices.get)[:2]
            self._state = lowest_hours[0]

class HighestCumulativePriceSensor(Entity):

    def __init__(self, attributes):
        self._name = "2h_highest_cumulative_price_ib"
        self._state = None
        self._attributes = attributes
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        if self._attributes:
            hours_prices = self._attributes["hourly_prices"]
            cumulative_prices = {}
            for hour in range(0, 23):
                cumulative_prices[hour] = hours_prices.get(hour, 0) + hours_prices.get(hour + 1, 0)

            highest_hours = sorted(cumulative_prices, key=cumulative_prices.get, reverse=True)[:2]
            self._state = highest_hours[0]
