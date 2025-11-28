from datetime import datetime, timedelta, timezone
import logging

from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_UPDATE_INTERVAL, DEFAULT_PREHEAT_DURATION, DEFAULT_UPDATE_INTERVAL, DEFAULT_ANCHOR_OFFSET, DEFAULT_ANCHOR_DURATION, OFFRES_DESCRIPTION

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
    "anchor_start": {
        "name": "Next Anchor Begin",
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "anchor_end": {
        "name": "Next Anchor End",
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HydroPeak sensors from a config entry."""
    
    offre_hydro = entry.data[CONF_OFFRE_HYDRO]
    preheat_duration = entry.data.get(CONF_PREHEAT_DURATION, DEFAULT_PREHEAT_DURATION)
    coordinator = hass.data[DOMAIN]['coordinator']
    description_fr = entry.data.get('description_fr', OFFRES_DESCRIPTION.get(offre_hydro, offre_hydro))
    
    _LOGGER.debug("Adding Sensors for %s", offre_hydro)
    is_CPC = offre_hydro.startswith("CPC")
    
    # only add the anchor sensors for CPC offers
    async_add_entities(
        HydroPeakSensor(coordinator, sensor_id, details, offre_hydro, description_fr, preheat_duration)
        for sensor_id, details in SENSORS.items()
        if is_CPC or not sensor_id.startswith("anchor")
    )

class HydroPeakSensor(CoordinatorEntity, SensorEntity):
    """Representation of a HydroPeak Sensor."""

    def __init__(self, coordinator, sensor_id, details, offre_hydro, description_fr, preheat_duration):
        super().__init__(coordinator, context=offre_hydro)

        if sensor_id == "preheat_start":
            self.preheat_duration = preheat_duration
        
        self._state = None
        self.offre_hydro = offre_hydro
        self.sensor_id = sensor_id
        self.unique_id = f"{offre_hydro}_{sensor_id}"
        self.name = details["name"]
        self.icon = details["icon"]
        self.device_class = details["device_class"]
        self.device_info = DeviceInfo(
            name=offre_hydro,
            manufacturer=description_fr,
            model=OFFRES_DESCRIPTION.get(offre_hydro, offre_hydro),
            identifiers={(DOMAIN, offre_hydro)},
            entry_type=DeviceEntryType.SERVICE,
        )
        
        
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.update_from_coordinator()
        
        
    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        self.update_from_coordinator()
        
    def update_from_coordinator(self):
        """Update the state of the sensor."""
        events = self.coordinator.data.get(self.offre_hydro)
        if events is None or not events:
            _LOGGER.debug(f"No events for {self.offre_hydro}")
            self.set_state(None)
            return
        
        evenement = next(
            (event for event in events if event["dateDebut"] <= datetime.now(timezone.utc) <= event["dateFin"]),
            next((event for event in events if event["dateDebut"] >= datetime.now(timezone.utc)), None)
        )
        
        if evenement is None:
            _LOGGER.debug(f"No event for {self.offre_hydro}")
            self.set_state(None)
            return
        
        if self.sensor_id == "event_start":
            self.set_state(evenement["dateDebut"])
        elif self.sensor_id == "event_end":
            self.set_state(evenement["dateFin"])
        elif self.sensor_id == "preheat_start":
            preheat_start = evenement["dateDebut"] - timedelta(minutes=self.preheat_duration)
            self.set_state(preheat_start)
        elif self.sensor_id == "anchor_start":
            anchor_start = evenement["dateDebut"] - timedelta(minutes=DEFAULT_ANCHOR_OFFSET)
            self.set_state(anchor_start)
        elif self.sensor_id == "anchor_end":
            anchor_end = evenement["dateDebut"] - timedelta(minutes=DEFAULT_ANCHOR_OFFSET - DEFAULT_ANCHOR_DURATION)
            self.set_state(anchor_end)
        else:
            raise ValueError(f"Unknown sensor_id: {self.sensor_id}")
        
        _LOGGER.debug(f"Updated {self.offre_hydro} {self.sensor_id} to {self._state}")
        
    @property
    def state(self):
        return self._state

    def set_state(self, new_state):
        """Set the sensor state."""
        if isinstance(new_state, datetime):
            self._state = new_state.isoformat()
        else:
            self._state = new_state
        
        self.async_write_ha_state()
