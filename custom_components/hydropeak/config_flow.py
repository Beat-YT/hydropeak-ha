from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .donnees_ouvertes import fetch_available_offers
from .const import DOMAIN, CONF_OFFRE_HYDRO, CONF_PREHEAT_DURATION, CONF_UPDATE_INTERVAL, DEFAULT_PREHEAT_DURATION, DEFAULT_UPDATE_INTERVAL, OFFRES_DESCRIPTION

class HydroPeakConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HydroPeak."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            existing_entries = self._async_current_entries()
            for entry in existing_entries:
                if entry.data[CONF_OFFRE_HYDRO] == user_input[CONF_OFFRE_HYDRO]:
                    return self.async_abort(
                        reason="already_configured",
                        description_placeholders={
                            "offre": user_input[CONF_OFFRE_HYDRO]
                        }
                    )
            
            return self.async_create_entry(title=user_input[CONF_OFFRE_HYDRO], data=user_input)
        
        errors = {}
        try:
            available_offers = await fetch_available_offers()
            offers_with_descriptions = {offer: OFFRES_DESCRIPTION.get(offer, offer) for offer in available_offers}
        except Exception as e:
            errors["base"] = "failed_to_obtain_offers"
            offers_with_descriptions = {}
        
        schema = vol.Schema({
            vol.Required(CONF_OFFRE_HYDRO): vol.In(offers_with_descriptions) if offers_with_descriptions else str,
            vol.Required(CONF_PREHEAT_DURATION, default=DEFAULT_PREHEAT_DURATION): int,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for HydroPeak."""
    
    def __init__(self, config_entry):
        """Set config entry for backwards compatibility."""
        if not hasattr(self, "config_entry"):
            self.config_entry = config_entry
            
    async def async_step_init(self, user_input=None):
        """Handle the option menu."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={ **self.config_entry.data, CONF_PREHEAT_DURATION: user_input[CONF_PREHEAT_DURATION] }
            )
            return self.async_create_entry(title="", data=user_input)
        
        preheat_duration = self.config_entry.options.get(CONF_PREHEAT_DURATION, DEFAULT_PREHEAT_DURATION)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_PREHEAT_DURATION, default=preheat_duration): int,
            }),
            description_placeholders={
                preheat_duration: "preheat_duration"
            }
        )