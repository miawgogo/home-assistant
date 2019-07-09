"""The tests for the Proximity component."""
import unittest

from homeassistant.components import zone_occupancy
from homeassistant.components.zone_occupancy import DOMAIN

from homeassistant.setup import setup_component
from tests.common import get_test_home_assistant


class TestZoneOccupancy(unittest.TestCase):
    """Test the Proximity component."""

    def setUp(self):
        """Set up things to be run when tests are started."""
        self.hass = get_test_home_assistant()
        self.hass.states.set(
            'zone.home', 'zoning',
            {
                'name': 'home',
                'latitude': 2.1,
                'longitude': 1.1,
                'radius': 10
            })
        self.hass.states.set(
            'zone.work', 'zoning',
            {
                'name': 'work',
                'latitude': 2.3,
                'longitude': 1.3,
                'radius': 10
            })

    def tearDown(self):
        """Stop everything that was started."""
        self.hass.stop()

    def test_proximities(self):
        """Test a list of proximities."""
        config = {
            'proximity': {
                'home': {
                    'ignored_zones': [
                        'work'
                    ],
                    'devices': [
                        'device_tracker.test1',
                        'device_tracker.test2'
                    ],
                    'tolerance': '1'
                },
                'work': {
                    'devices': [
                        'device_tracker.test1'
                    ],
                    'tolerance': '1'
                }
            }
        }

        assert setup_component(self.hass, DOMAIN, config)

        proximities = ['home', 'work']

        for prox in proximities:
            state = self.hass.states.get('proximity.' + prox)
            assert state.state == 'not set'
            assert state.attributes.get('nearest') == 'not set'
            assert state.attributes.get('dir_of_travel') == 'not set'

            self.hass.states.set('proximity.' + prox, '0')
            self.hass.block_till_done()
            state = self.hass.states.get('proximity.' + prox)
            assert state.state == '0'

    def test_proximities_setup(self):
        """Test a list of proximities with missing devices."""
        config = {
            'proximity': {
                'home': {
                    'ignored_zones': [
                        'work'
                    ],
                    'devices': [
                        'device_tracker.test1',
                        'device_tracker.test2'
                    ],
                    'tolerance': '1'
                },
                'work': {
                    'tolerance': '1'
                }
            }
        }

        assert setup_component(self.hass, DOMAIN, config)

    def test_proximity(self):
        """Test the proximity."""
        config = {
            'proximity': {
                'home': {
                    'ignored_zones': [
                        'work'
                    ],
                    'devices': [
                        'device_tracker.test1',
                        'device_tracker.test2'
                    ],
                    'tolerance': '1'
                }
            }
        }

        assert setup_component(self.hass, DOMAIN, config)

        state = self.hass.states.get('proximity.home')
        assert state.state == 'not set'
        assert state.attributes.get('nearest') == 'not set'
        assert state.attributes.get('dir_of_travel') == 'not set'

        self.hass.states.set('proximity.home', '0')
        self.hass.block_till_done()
        state = self.hass.states.get('proximity.home')
        assert state.state == '0'

    def test_device_tracker_test1_in_zone(self):
        """Test for tracker in zone."""
        config = {
            'proximity': {
                'home': {
                    'ignored_zones': [
                        'work'
                    ],
                    'devices': [
                        'device_tracker.test1'
                    ],
                    'tolerance': '1'
                }
            }
        }

        assert setup_component(self.hass, DOMAIN, config)

        self.hass.states.set(
            'device_tracker.test1', 'home',
            {
                'friendly_name': 'test1',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.block_till_done()
        state = self.hass.states.get('proximity.home')
        assert state.state == '0'
        assert state.attributes.get('nearest') == 'test1'
        assert state.attributes.get('dir_of_travel') == 'arrived'

    def test_device_trackers_in_zone(self):
        """Test for trackers in zone."""
        config = {
            'proximity': {
                'home': {
                    'devices': [
                        'device_tracker.test1',
                        'device_tracker.test2'
                    ],
                    'tolerance': '1'
                }
            }
        }

        assert setup_component(self.hass, DOMAIN, config)

        self.hass.states.set(
            'device_tracker.test1', 'home',
            {
                'friendly_name': 'test1',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.block_till_done()
        self.hass.states.set(
            'device_tracker.test2', 'home',
            {
                'friendly_name': 'test2',
                'latitude': 2.1,
                'longitude': 1.1
            })
        self.hass.block_till_done()
        state = self.hass.states.get('proximity.home')
        assert state.state == '0'
        assert ((state.attributes.get('nearest') == 'test1, test2') or
                (state.attributes.get('nearest') == 'test2, test1'))
        assert state.attributes.get('dir_of_travel') == 'arrived'
