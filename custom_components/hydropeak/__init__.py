import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_OFFRE_HYDRO
from .coordinator import HydroPeakCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up HydroPeak integration."""
    _LOGGER.debug("Setting up Integration coordinator")
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    # We only have a single coordinator for all entry
    coordinator = HydroPeakCoordinator(hass)
    hass.data[DOMAIN]["coordinator"] = coordinator
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a HydroPeak entry."""
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        
    offre = entry.data.get(CONF_OFFRE_HYDRO)
    _LOGGER.debug("Entry Setup for %s", offre)
    
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator is None:
        _LOGGER.error("Coordinator is not setup")
        return False
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    await coordinator.async_refresh()
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    return True
