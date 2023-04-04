DOMAIN = "energy_price"

def setup(hass, config):
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)
    return True
