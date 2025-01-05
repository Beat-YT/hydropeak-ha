from datetime import datetime, timedelta, timezone
import asyncio
import aiohttp
import logging

from .donnees_ouvertes import fetch_events, fetch_events_json
from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_UPDATE_INTERVAL, DEFAULT_PREHEAT_DURATION, DEFAULT_UPDATE_INTERVAL, OFFRES_DESCRIPTION

from homeassistant.core import callback
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = {
    "peak_active": {
        "name": "Cricital Peak in progress",
        "icon": "mdi:flash-alert"
    },
    "peak_today_AM": {
        "name": "Morning Peak Today",
        "icon": "mdi:message-flash"
    },
    "peak_tomorrow_AM": {
        "name": "Morning Peak Tomorrow",
        "icon": "mdi:message-flash"
    },
    "peak_today_PM": {
        "name": "Evening Peak Today",
        "icon": "mdi:message-flash"
    },
    "peak_tomorrow_PM": {
        "name": "Evening Peak Tomorrow",
        "icon": "mdi:message-flash"
    },
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensors."""
    
    offre_hydro = entry.data[CONF_OFFRE_HYDRO]
    coordinator = hass.data[DOMAIN]['coordinator']
    
    _LOGGER.debug("Adding Binary Sensors for %s", offre_hydro)
    async_add_entities(
        PeakBinarySensor(coordinator, sensor_id, details, offre_hydro) for sensor_id, details in BINARY_SENSORS.items()
    )
    
class PeakBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a peak binary sensor."""

    def __init__(self, coordinator, sensor_id, details, offre_hydro):
        super().__init__(coordinator, context=offre_hydro)
        
        self._state = False
        self.offre_hydro = offre_hydro
        self.sensor_id = sensor_id
        self.unique_id = f"{offre_hydro}_{sensor_id}"
        self.name = details["name"]
        self.icon = details["icon"]
        self.entity_category = EntityCategory.DIAGNOSTIC
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
            self._state = False
            self.async_write_ha_state()
            return
        
        # Using the following keys from the event:
        # - datedebut (timestamp)
        # - datefin (timestamp)
        # - plageHoraire (AM/PM)
        
        now = datetime.now(timezone.utc)
        if (self.sensor_id == "peak_active"):
            self._state = event.get("dateDebut", None) <= now <= event.get("dateFin", None)
        elif (self.sensor_id == "peak_today_AM"):
            self._state = event.get("plageHoraire", None) == "AM" and event.get("dateDebut", None).date() == now.date()
        elif (self.sensor_id == "peak_tomorrow_AM"):
            self._state = event.get("plageHoraire", None) == "AM" and event.get("dateDebut", None).date() == now.date() + timedelta(days=1)
        elif (self.sensor_id == "peak_today_PM"):
            self._state = event.get("plageHoraire", None) == "PM" and event.get("dateDebut", None).date() == now.date()
        elif (self.sensor_id == "peak_tomorrow_PM"):
            self._state = event.get("plageHoraire", None) == "PM" and event.get("dateDebut", None).date() == now.date() + timedelta(days=1)
        else:
            raise HomeAssistantError(f"Updating unknown sensor_id: {self.sensor_id}")
            
        _LOGGER.debug(f"Updated {self.offre_hydro} {self.sensor_id} to {self._state}")
        self.async_write_ha_state()
        
    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def available(self):
        if self.sensor_id == "peak_active":
            return True
        
        return self._state is True