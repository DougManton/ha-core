"""Constants for the Ohme Smart EV Charger integration."""

DOMAIN = "ohme_charger"
DATA_INFO = "info"
DATA_COORDINATOR = "coordinator"

# Platforms
SENSOR = "sensor"
BINARY_SENSOR = "binary_sensor"
SELECT = "select"
NUMBER = "number"
PLATFORMS = [BINARY_SENSOR, SELECT, NUMBER]

CONF_APIKEY = "api_key"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
