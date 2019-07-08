"""A Zone Occupancy Sensor"""
import logging

import voluptuous as vol

from homeassistant.const import (
    CONF_DEVICES, CONF_UNIT_OF_MEASUREMENT, CONF_ZONE)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_state_change
from homeassistant.helpers.condition import zone as zonecmp
from homeassistant.util.distance import convert
from homeassistant.util.location import distance

_LOGGER = logging.getLogger(__name__)
DOMAIN = 'zone_occupancy'

ZONE_SCHEMA = vol.Schema({
    vol.Optional(CONF_DEVICES, default=[]):
        vol.All(cv.ensure_list, [cv.entity_id]),
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: cv.schema_with_slug_keys(ZONE_SCHEMA),
}, extra=vol.ALLOW_EXTRA)

TRACKABLE_DOMAINS = ["person", "device_tracker"]

def setup_occupancy_component(hass, name, config):
    """Set up the individual proximity component."""
    occupancy_devices = config.get(CONF_DEVICES)

    invalid_occupancy_devices = False

    for device in occupancy_devices:
        if device.split(".")[0] not in TRACKABLE_DOMAINS:
            _LOGGER.error("%s Not trackable", device)
            invalid_occupancy_devices = True
    
    if invalid_occupancy_devices:
        _LOGGER.error("%s config contains untrackable device", name)
        return

    occupancy_zone = name
    zone_id = 'zone.{}'.format(name)

    proximity = Occupancy(hass, occupancy_zone, occupancy_devices, zone_id)
    proximity.entity_id = '{}.{}'.format(DOMAIN, occupancy_zone)

    proximity.schedule_update_ha_state()

    track_state_change(
        hass, occupancy_devices, proximity.check_proximity_state_change)

    return True


def setup(hass, config):
    """Get the zones to track."""
    for zone, occupancy_config in config[DOMAIN].items():
        setup_occupancy_component(hass, zone, occupancy_config)

    return True


class Occupancy(Entity):
    """Representation of a zone_occupancy."""

    def __init__(self, hass, zone_friendly_name, occupancy_devices, occupancy_zone):
        """Initialize the proximity."""
        self.hass = hass
        self.friendly_name = zone_friendly_name
        self._tracking_devices = occupancy_devices
        self._zone = occupancy_zone
        self._count = 0

    @property
    def name(self):
        """Return the name of the entity."""
        return self.friendly_name

    @property
    def state(self):
        """Return the state."""
        return self._count

    def check_proximity_state_change(self, entity, old_state, new_state):
        """Perform the proximity checking."""
        counter = 0
        for device in self._tracking_devices:
            if zonecmp(self.hass, self._zone, device):
                counter += 1
        self._count = counter
        _LOGGER.info("counted  %d", self._count)
        self.schedule_update_ha_state()
