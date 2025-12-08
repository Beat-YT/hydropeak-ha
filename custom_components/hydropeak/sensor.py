from datetime import datetime, timedelta, timezone
import logging

from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_DEVICE_VER, DEFAULT_PREHEAT_DURATION, DEFAULT_ANCHOR_OFFSET, DEFAULT_ANCHOR_DURATION, OFFRES_DESCRIPTION

from homeassistant.core import callback
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    "event_start": {
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "event_end": {
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "preheat_start": {
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "anchor_start": {
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "anchor_end": {
        "icon": "mdi:home-clock",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HydroPeak sensors from a config entry."""
    
    offre_hydro = entry.data[CONF_OFFRE_HYDRO]
    preheat_duration = entry.data.get(CONF_PREHEAT_DURATION, DEFAULT_PREHEAT_DURATION)
    coordinator = hass.data[DOMAIN]['coordinator']
    device_ver = entry.data.get(CONF_DEVICE_VER, None)
    
    _LOGGER.debug("Adding Sensors for %s", offre_hydro)
    is_CPC = offre_hydro.startswith("CPC")
    
    # only add the anchor sensors for CPC offers
    async_add_entities(
        HydroPeakSensor(coordinator, sensor_id, details, offre_hydro, device_ver, preheat_duration)
        for sensor_id, details in SENSORS.items()
        if is_CPC or not sensor_id.startswith("anchor")
    )

class HydroPeakSensor(CoordinatorEntity, SensorEntity):
    """Representation of a HydroPeak Sensor."""

    _attr_has_entity_name = True
    _state = None

    def __init__(self, coordinator, sensor_id, details, offre_hydro, device_ver, preheat_duration):
        super().__init__(coordinator, context=offre_hydro)

        if sensor_id == "preheat_start":
            self.preheat_duration = preheat_duration
        
        self.offre_hydro = offre_hydro
        self.sensor_id = sensor_id
        self._attr_unique_id = f"{offre_hydro}_{sensor_id}"
        self._attr_translation_key = sensor_id
        self._attr_icon = details["icon"]
        self._attr_device_class = details["device_class"]
        self._attr_device_info = DeviceInfo(
            name=offre_hydro,
            manufacturer=None,
            sw_version=device_ver,
            model=OFFRES_DESCRIPTION.get(offre_hydro, offre_hydro),
            identifiers={(DOMAIN, offre_hydro)},
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/table/?sort=datedebut&refine.offre={offre_hydro}",
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
