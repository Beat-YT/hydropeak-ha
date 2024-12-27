from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup(hass, config):
    """Set up HydroPeak integration."""
    if DOMAIN not in config:
        return True
    
    await hass.config_entries.async_forward_entry_setups(config, ["sensor"])
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HydroPeak from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True
