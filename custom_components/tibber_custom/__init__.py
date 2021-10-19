"""Tibber custom"""
import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.helpers import discovery


DOMAIN = "tibber_custom"

CONF_USE_DARK_MODE = "use_dark_mode"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_USE_DARK_MODE, default=False): cv.boolean,
    })
}, extra=vol.ALLOW_EXTRA)


DEPENDENCIES = ["tibber"]

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Setup component."""

    use_dark_mode = config[DOMAIN][CONF_USE_DARK_MODE]

    def ha_started(_):
        discovery.load_platform(hass, "camera", DOMAIN, {}, config)

    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, ha_started)

    return True
