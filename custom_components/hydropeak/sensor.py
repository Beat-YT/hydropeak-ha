from datetime import datetime, timedelta, timezone
import asyncio
import aiohttp
import logging

from .donnees_ouvertes import fetch_events, fetch_events_json
from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_UPDATE_INTERVAL, DEFAULT_PREHEAT_DURATION, DEFAULT_UPDATE_INTERVAL, OFFRES_DESCRIPTION

from homeassistant.core import callback
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    "event_start": {
        "name": "Next Event Begin",
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "event_end": {
        "name": "Next Event End",
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "preheat_start": {
        "name": "Next Preheat Start",
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HydroPeak sensors from a config entry."""
    
    offre_hydro = entry.data[CONF_OFFRE_HYDRO]
    preheat_duration = entry.data.get(CONF_PREHEAT_DURATION, DEFAULT_PREHEAT_DURATION)
    _LOGGER.debug("Adding HydroPeak Sensors for %s", offre_hydro)
    
    coordinator = hass.data[DOMAIN]['coordinator']
    
    async_add_entities(
        HydroPeakSensor(coordinator, sensor_id, details, offre_hydro, preheat_duration) for sensor_id, details in SENSORS.items()
    )

class HydroPeakSensor(CoordinatorEntity, SensorEntity):
    """Representation of a HydroPeak Sensor."""

    def __init__(self, coordinator, sensor_id, details, offre_hydro, preheat_duration):
        
        # Subscribe to the coordinator for updates
        super().__init__(coordinator, context=offre_hydro)
        self.offre_hydro = offre_hydro
        
        if sensor_id == "preheat_start":
            self.preheat_duration = preheat_duration
        
        self._state = None
        self.sensor_id = sensor_id
        self.unique_id = f"{offre_hydro}_{sensor_id}"
        self.name = details["name"]
        self.icon = details["icon"]
        self.device_class = details["device_class"]
        self.device_info = DeviceInfo(
            name=offre_hydro,
            model=OFFRES_DESCRIPTION.get(offre_hydro, offre_hydro),
            identifiers={(DOMAIN, offre_hydro)},
            entry_type=DeviceEntryType.SERVICE,
        )
        
    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        
        event = self.coordinator.data.get(self.offre_hydro)
        
        if event is None:
            _LOGGER.debug(f"No data for {self.offre_hydro}")
            self.set_state(None)
            return
        
        # Update the sensor state using the coordinator data, based on what sensor we are
        if (self.sensor_id == "event_start"):
            self.set_state(event["datedebut"])
        elif (self.sensor_id == "event_end"):
            self.set_state(event["datefin"])
        elif (self.sensor_id == "preheat_start"):
            self.set_state(event["datedebut"] - timedelta(minutes=self.preheat_duration))
        elif (self.sensor_id == "peak_today"):
            # check if the event is today using the datedebut
            event_start = event["datedebut"]
            now = datetime.now(timezone.utc)
            
            if event_start.date() == now.date():
                self.set_state(event_start)
            elif event_start.date() < now.date():
                self.set_state(None)
        else:
            raise HomeAssistantError(f"Updating unknown sensor_id: {self.sensor_id}")
        
        _LOGGER.debug(f"Updated {self.offre_hydro} {self.sensor_id} to {self._state}")
        
    @property
    def state(self):
        return self._state

    def set_state(self, new_state):
        """Set the sensor state."""
        
        if isinstance(new_state, datetime):
            new_state_str = new_state.isoformat()
        else:
            new_state_str = new_state
        
        if new_state_str == self._state:
            return
        
        self._state = new_state_str
        self.async_write_ha_state()
