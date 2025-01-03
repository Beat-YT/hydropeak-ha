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
        
        available_offers = None
        errors = {}
                
        try:
            available_offers = await fetch_available_offers()
        except Exception as e:
            errors["base"] = f"Failed to obtain available offers: {e}"
            
        offers_with_descriptions = {}
        if available_offers:
            for offer in available_offers:
                description = OFFRES_DESCRIPTION.get(offer, offer)
                offers_with_descriptions[offer] = description
            sorted_offers = {key: value for key, value in sorted(offers_with_descriptions.items(), key=lambda item: item[1] != "")}

        schema = vol.Schema({
            vol.Required(CONF_OFFRE_HYDRO): vol.In(offers_with_descriptions) if available_offers else str,
            vol.Required(CONF_PREHEAT_DURATION, default=DEFAULT_PREHEAT_DURATION): int,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "offre_hydro": "offre_hydro",
                "preheat_duration": "preheat_duration",
            },
            errors=errors
        )