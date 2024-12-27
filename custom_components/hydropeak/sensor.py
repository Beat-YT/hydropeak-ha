from datetime import datetime, timedelta, timezone
import asyncio
import aiohttp
import logging

from .donnees_ouvertes import fetch_events, fetch_events_json
from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_UPDATE_INTERVAL, DEFAULT_PREHEAT_DURATION, DEFAULT_UPDATE_INTERVAL

from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    "event_start": {
        "name": "Event Begin",
        "icon": "mdi:clock-start",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "event_end": {
        "name": "Event End",
        "icon": "mdi:clock-end",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "preheat_start": {
        "name": "Preheat Start",
        "icon": "mdi:clock-start",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up HydroPeak sensors from a config entry."""
    _LOGGER.debug("Setting up HydroPeak Sensors")
    
    settings = entry.data
    offre_hydro = settings[CONF_OFFRE_HYDRO]
    preheat_duration = settings.get(CONF_PREHEAT_DURATION, DEFAULT_PREHEAT_DURATION)
    update_interval = settings.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    
    sensors = [HydroPeakSensor(sensor_id, details, entry.entry_id, offre_hydro) for sensor_id, details in SENSORS.items()]
    async_add_entities(sensors)
    asyncio.create_task(update_sensors(sensors, offre_hydro, update_interval, preheat_duration))    

async def update_sensors(sensors, offre_hydro, update_interval, preheat_duration):
    """Update sensor states."""
    peak_start_sensor = next((s for s in sensors if s.sensor_id == "event_start"), None)
    peak_end_sensor = next((s for s in sensors if s.sensor_id == "event_end"), None)
    preheat_sensor = next((s for s in sensors if s.sensor_id == "preheat_start"), None)
    
    while True:
        _LOGGER.debug("Updating HydroPeak sensors")
        events = await fetch_events(offre_hydro)
        now = datetime.now(timezone.utc)
        
        # Determine current and next events
        current_event = next((e for e in events if e["datedebut"] <= now <= e["datefin"]), None)
        next_event = next((e for e in events if e["datedebut"] > now), None)
        
        if not current_event and not next_event:
            _LOGGER.debug("No events found") 
            peak_start_sensor.set_state(None)
            peak_end_sensor.set_state(None)
            preheat_sensor.set_state(None)
            continue
        
        if next_event:
            _LOGGER.debug(f"Next event: {next_event['datedebut']} - {next_event['datefin']}")
            peak_start_sensor.set_state(next_event["datedebut"])
            preheat_sensor.set_state(next_event["datedebut"] - timedelta(minutes=preheat_duration))
        
        if current_event:
            _LOGGER.debug(f"Current event: {current_event['datedebut']} - {current_event['datefin']}")
            peak_end_sensor.set_state(current_event["datefin"])
        elif next_event:
            peak_end_sensor.set_state(next_event["datefin"])
            
        await asyncio.sleep(update_interval * 60)

class HydroPeakSensor(SensorEntity):
    """Representation of a HydroPeak Sensor."""

    def __init__(self, sensor_id, details, entry_id, offre_hydro):
        self.sensor_id = sensor_id
        self.name = details["name"]
        self.icon = details["icon"]
        self.device_class = details["device_class"]
        self.unique_id = f"{offre_hydro}_{sensor_id}"
        self.entity_category = EntityCategory.DIAGNOSTIC  # Set to DIAGNOSTIC
        self.device_info = DeviceInfo(
            name=offre_hydro,
            model=f"Offre {offre_hydro}",
            identifiers={(DOMAIN, entry_id)},
            entry_type=DeviceEntryType.SERVICE,
        )
        self._state = None

    def set_state(self, new_state):
        """Set the sensor state."""
        self._state = new_state.isoformat() if isinstance(new_state, datetime) else None
        self.async_write_ha_state()
