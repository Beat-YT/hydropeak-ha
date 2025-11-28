from datetime import datetime, timedelta, timezone
import logging

from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_UPDATE_INTERVAL, DEFAULT_PREHEAT_DURATION, DEFAULT_UPDATE_INTERVAL, OFFRES_DESCRIPTION

from homeassistant.core import callback
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_point_in_utc_time

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = {
    "peak_active": {
        "name": "Peak in progress",
        "icon": "mdi:flash-alert"
    },
    "preheat_active": {
        "name": "Preheat in Progress",
        "icon": "mdi:flash-alert"
    },
    "peak_today_AM": {
        "name": "Morning Peak Today",
    },
    "peak_tomorrow_AM": {
        "name": "Morning Peak Tomorrow",
    },
    "peak_today_PM": {
        "name": "Evening Peak Today",
    },
    "peak_tomorrow_PM": {
        "name": "Evening Peak Tomorrow",
    },
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensors."""
    
    offre_hydro = entry.data[CONF_OFFRE_HYDRO]
    preheat_duration = entry.data.get(CONF_PREHEAT_DURATION, DEFAULT_PREHEAT_DURATION)
    coordinator = hass.data[DOMAIN]['coordinator']
    description_fr = entry.data.get('description_fr', OFFRES_DESCRIPTION.get(offre_hydro, offre_hydro))
    
    _LOGGER.debug("Adding Binary Sensors for %s", offre_hydro)
    async_add_entities(
        PeakBinarySensor(coordinator, sensor_id, details, offre_hydro, description_fr, preheat_duration) for sensor_id, details in BINARY_SENSORS.items()
    )
    
class PeakBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a peak binary sensor."""

    def __init__(self, coordinator, sensor_id, details, offre_hydro, description_fr, preheat_duration):
        super().__init__(coordinator, context=offre_hydro)
        
        if sensor_id == "preheat_active":
            self.preheat_duration = preheat_duration
            
        self.next_update_time = None
        self._unsub_next_update = None
        self._state = False
        self.offre_hydro = offre_hydro
        self.sensor_id = sensor_id
        self.unique_id = f"{offre_hydro}_{sensor_id}"
        self.name = details.get("name")
        self.icon = details.get("icon")
        self.entity_category = EntityCategory.DIAGNOSTIC
        self.device_info = DeviceInfo(
            name=offre_hydro,
            sw_version=description_fr,
            model=OFFRES_DESCRIPTION.get(offre_hydro, offre_hydro),
            identifiers={(DOMAIN, offre_hydro)},
            entry_type=DeviceEntryType.SERVICE,
        )
        
    async def async_added_to_hass(self):
        """Initial update from coordinator."""
        await super().async_added_to_hass()
        self.update_from_coordinator()
        
    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        self.update_from_coordinator()
        
    @callback
    def _handle_time_update(self, now):
        """Handle time-based updates."""
        self.update_from_coordinator()
        
    def update_from_coordinator(self):
        """Update the state of the sensor."""        

        events = self.coordinator.data.get(self.offre_hydro)
        if events is None or not events:
            self._state = False
            self.async_write_ha_state()
            return
        
        # Using the following keys from the event:
        # - dateDebut (timestamp)
        # - dateFin (timestamp)
        # - plageHoraire (AM/PM)
        
        now = datetime.now()
        if (self.sensor_id == "peak_active"):
            now = datetime.now(timezone.utc)
            event_active = next((event for event in events if event["dateDebut"] <= now <= event["dateFin"]), None)
            next_event = next((event for event in events if event["dateDebut"] > now), None)
            self._state = event_active is not None
            if event_active:
                self.schedule_next_update(event_active["dateFin"])
            elif next_event:
                self.schedule_next_update(next_event["dateDebut"])
        elif (self.sensor_id == "peak_today_AM"):
            event_today_AM = next((event for event in events if event["plageHoraire"] == "AM" and event["dateDebut"].date() == now.date()), None)
            self._state = event_today_AM is not None
        elif (self.sensor_id == "peak_tomorrow_AM"):
            event_tomorrow_AM = next((event for event in events if event["plageHoraire"] == "AM" and event["dateDebut"].date() == now.date() + timedelta(days=1)), None)
            self._state = event_tomorrow_AM is not None
        elif (self.sensor_id == "peak_today_PM"):
            event_today_PM = next((event for event in events if event["plageHoraire"] == "PM" and event["dateDebut"].date() == now.date()), None)
            self._state = event_today_PM is not None
        elif (self.sensor_id == "peak_tomorrow_PM"):
            event_tomorrow_PM = next((event for event in events if event["plageHoraire"] == "PM" and event["dateDebut"].date() == now.date() + timedelta(days=1)), None)
            self._state = event_tomorrow_PM is not None
        elif (self.sensor_id == "preheat_active"):
            now = datetime.now(timezone.utc)
            preheat_duration = timedelta(minutes=self.preheat_duration)
            next_event = next((event for event in events if event["dateDebut"] > now), None)
            if next_event:
                preheat_start_time = next_event["dateDebut"] - preheat_duration
                self._state = preheat_start_time <= now < next_event["dateDebut"]
                if self._state:
                    self.schedule_next_update(next_event["dateDebut"])
                else:
                    self.schedule_next_update(preheat_start_time)
            else:
                self._state = False
        else:
            raise ValueError(f"Updating unknown sensor_id: {self.sensor_id}")
        
        _LOGGER.debug(f"Updated {self.offre_hydro} {self.sensor_id} to {self._state}")
        self.async_write_ha_state()
                
    def schedule_next_update(self, next_update_time):
        """Set the next update time."""
        if self.next_update_time is None or next_update_time < self.next_update_time:
            if self._unsub_next_update:
                self._unsub_next_update()
            self.next_update_time = next_update_time
            _LOGGER.debug(f"Next update for {self.offre_hydro} {self.sensor_id} at {self.next_update_time}")
            self._unsub_next_update = async_track_point_in_utc_time(
                self.hass, self._handle_time_update, next_update_time
            )
            
    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def available(self):
        return True