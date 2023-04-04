import logging
import requests
import json
from datetime import datetime
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([BojkasEnergyPriceSensor(), BojkasLowestCumulativePriceSensor(), BojkasHighestCumulativePriceSensor()])

class BojkasEnergyPriceSensor(Entity):

    def __init__(self):
        self._name = "bojkas_energy_price"
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

            # Get all hourly prices and store them in a dictionary
            for point in data["data"]["dataLine"][1]["point"]:
                hour = int(point["x"])
                price = float(point["y"])
                hours_prices[hour] = price

            # Calculate cumulative prices for each consecutive hour pair
            cumulative_prices = {}
            for hour in range(0, 23):
                cumulative_prices[hour] = hours_prices.get(hour, 0) + hours_prices.get(hour + 1, 0)

            # Find the two hours with the lowest and highest cumulative prices
            lowest_hours = sorted(cumulative_prices, key=cumulative_prices.get)[:2]
            highest_hours = sorted(cumulative_prices, key=cumulative_prices.get, reverse=True)[:2]

            # Set the state and attributes of the sensor
            self._state = hours_prices.get(datetime.now().hour)
            self._attributes = {
                "hourly_prices": hours_prices,
                "lowest_cumulative_hours": lowest_hours,
                "highest_cumulative_hours": highest_hours
            }
        else:
            _LOGGER.error("Failed to update energy price.")
            
class BojkasLowestCumulativePriceSensor(Entity):

    def __init__(self):
        self._name = "bojkas_2h_lowest_cumulative_price"
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

            # Get all hourly prices and store them in a dictionary
            for point in data["data"]["dataLine"][1]["point"]:
                hour = int(point["x"])
                price = float(point["y"])
                hours_prices[hour] = price

            # Calculate cumulative prices for each consecutive hour pair
            cumulative_prices = {}
            for hour in range(0, 23):
                cumulative_prices[hour] = hours_prices.get(hour, 0) + hours_prices.get(hour + 1, 0)

            # Find the two hours with the lowest and highest cumulative prices
            lowest_hours = sorted(cumulative_prices, key=cumulative_prices.get)[:2]
            highest_hours = sorted(cumulative_prices, key=cumulative_prices.get, reverse=True)[:2]

            # Set the state and attributes of the sensor
            self._state = hours_prices.get(datetime.now().hour)
            self._attributes = {
                "hourly_prices": hours_prices,
                "lowest_cumulative_hours": lowest_hours,
                "highest_cumulative_hours": highest_hours
            }
        else:
            _LOGGER.error("Failed to update energy price.")

        # Find the two hours with the lowest cumulative prices
        lowest_hours = sorted(cumulative_prices, key=cumulative_prices.get)[:2]

        # Set the state of the sensor
        self._state = lowest_hours[0]
        
class BojkasHighestCumulativePriceSensor(Entity):

    def __init__(self):
        self._name = "bojkas_2h_highest_cumulative_price"
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

            # Get all hourly prices and store them in a dictionary
            for point in data["data"]["dataLine"][1]["point"]:
                hour = int(point["x"])
                price = float(point["y"])
                hours_prices[hour] = price

            # Calculate cumulative prices for each consecutive hour pair
            cumulative_prices = {}
            for hour in range(0, 23):
                cumulative_prices[hour] = hours_prices.get(hour, 0) + hours_prices.get(hour + 1, 0)

            # Find the two hours with the lowest and highest cumulative prices
            lowest_hours = sorted(cumulative_prices, key=cumulative_prices.get)[:2]
            highest_hours = sorted(cumulative_prices, key=cumulative_prices.get, reverse=True)[:2]

            # Set the state and attributes of the sensor
            self._state = hours_prices.get(datetime.now().hour)
            self._attributes = {
                "hourly_prices": hours_prices,
                "lowest_cumulative_hours": lowest_hours,
                "highest_cumulative_hours": highest_hours
            }
        else:
            _LOGGER.error("Failed to update energy price.")

        # Find the two hours with the highest cumulative prices
        highest_hours = sorted(cumulative_prices, key=cumulative_prices.get, reverse=True)[:2]

        # Set the state of the sensor
        self._state = highest_hours[0]
