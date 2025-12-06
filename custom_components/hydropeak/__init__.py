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
    
    await coordinator.async_refresh()
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a HydroPeak entry."""
    
    offre = entry.data.get(CONF_OFFRE_HYDRO)
    _LOGGER.debug("Entry Setup for %s", offre)
    
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator is None:
        _LOGGER.error("Coordinator is not setup")
        return False

    is_reload = hass.data[DOMAIN].get(f"unloaded_{offre}", False)
    if is_reload:
        _LOGGER.debug("Detected reload for %s, refreshing coordinator", offre)
        hass.data[DOMAIN].pop(f"unloaded_{offre}", None)
        await coordinator.async_refresh()
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    offre = entry.data.get(CONF_OFFRE_HYDRO)
    _LOGGER.debug("Unloading entry for %s", offre)

    # use this flag to detect entry reload
    hass.data[DOMAIN].pop(f"unloaded_{offre}", True)

    await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    _LOGGER.debug("Updating options for %s", entry.data.get(CONF_OFFRE_HYDRO))
    await hass.config_entries.async_reload(entry.entry_id)