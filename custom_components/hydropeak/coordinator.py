import logging
from datetime import timedelta
from .donnees_ouvertes import fetch_events_json
from .const import DEFAULT_UPDATE_INTERVAL

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

class HydroPeakCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="Peak Event Data",
            update_interval=timedelta(minutes=DEFAULT_UPDATE_INTERVAL),
            always_update=True
        )

    async def _async_update_data(self):
        try:
            listening_idx = set(self.async_contexts())
            _LOGGER.debug(f"Updating coordinator data, listeners: {listening_idx}")
                        
            data = await fetch_events_json()
            _LOGGER.debug(f"Data: {data}")
            
            offres = set([event["offre"] for event in data])
            return {offre: [event for event in data if event["offre"] == offre] for offre in offres}
        except Exception as err:
            raise UpdateFailed(f"Error updating coordinator data: {err}")