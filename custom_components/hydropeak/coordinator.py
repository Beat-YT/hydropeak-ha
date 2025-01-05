import logging
from datetime import timedelta
from .donnees_ouvertes import fetch_events, fetch_events_json

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
            update_interval=timedelta(hours=1),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True
        )

    async def _async_update_data(self):
        try:
            offres = set(self.async_contexts())
            _LOGGER.debug(f"Offres: {offres}")
            
            data = await fetch_events_json()
                                
            # Filter data to only include events offres that are relevant to the listeners
            # data = [event for event in data if event["offre"] in offres]
            
            _LOGGER.debug(f"Data: {data}")
            
            #group the data by offre, like in a object with the key being the offre
            return {event["offre"]: event for event in data}
        except Exception as err:
            raise UpdateFailed(f"Error updating coordinator data: {err}")