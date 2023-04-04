import logging
import requests
import json
from datetime import datetime
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

def get_eur_czk_exchange_rate():
    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.split("\n")
        for line in lines:
            if "EUR" in line:
                exchange_rate = float(line.split("|")[4].replace(",", "."))
                return exchange_rate
    return None

def convert_to_czk(eur_amount, exchange_rate):
    czk_amount = eur_amount * exchange_rate
    return round(czk_amount / 1000, 3)

def setup_platform(hass, config, add_entities, discovery_info=None):
    energy_price_sensor = EnergyPriceSensor()
    energy_price_sensor.update()
    add_entities([
        energy_price_sensor,
        LowestCumulativePriceSensor(energy_price_sensor._attributes["hourly_prices"]),
        HighestCumulativePriceSensor(energy_price_sensor._attributes["hourly_prices"])
    ])

class EnergyPriceSensor(Entity):

    def __init__(self):
        self._name = "energy_price_ib"
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
        exchange_rate = get_eur_czk_exchange_rate()
        if exchange_rate is None:
            _LOGGER.error("Failed to update exchange rate.")
            return

        url = "https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data"
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)
            hours_prices = {}

            for point in data["data"]["dataLine"][1]["point"]:
                hour = int(point["x"])
                price = float(point["y"])
                czk_price = convert_to_czk(price, exchange_rate)
                if hour not in hours_prices or hours_prices[hour] != czk_price:
                    hours_prices[hour] = czk_price

            self._state = hours_prices.get(datetime.now().hour+1)
            self._attributes = {
                "hourly_prices": hours_prices,
            }
        else:
            _LOGGER.error("Failed to update energy price.")

class LowestCumulativePriceSensor(Entity):

    def __init__(self, hourly_prices):
        self._name = "2h_lowest_cumulative_price_ib"
        self._state = None
        self._hourly_prices = hourly_prices
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        cumulative_prices = {}
        for hour in range(0, 23):
            cumulative_prices[hour] = self._hourly_prices.get(hour, 0) + self._hourly_prices.get(hour + 1, 0)

        lowest_hours = sorted(cumulative_prices, key=cumulative_prices.get)[:2]
        self._state = lowest_hours[0]

class HighestCumulativePriceSensor(Entity):

    def __init__(self, hourly_prices):
        self._name = "2h_highest_cumulative_price_ib"
        self._state = None
        self._hourly_prices = hourly_prices
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        cumulative_prices = {}
        for hour in range(0, 23):
            cumulative_prices[hour] = self._hourly_prices.get(hour, 0) + self._hourly_prices.get(hour + 1, 0)

        highest_hours = sorted(cumulative_prices, key=cumulative_prices.get, reverse=True)[:2]
        self._state = highest_hours[0]
