import aiohttp
from datetime import datetime
import logging

from .const import DOMAIN
from homeassistant.exceptions import HomeAssistantError
_LOGGER = logging.getLogger(__name__)

def handle_exception(response):
    if response.status == 429:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="rate_limit"
        )
    elif response.status != 200:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="http_error",
            translation_placeholders={"status": response.status}
        )
    response.raise_for_status()

async def fetch_events_json():
    """Fetch events from Hydro JSON"""
    url = "https://donnees.solutions.hydroquebec.com/donnees-ouvertes/data/json/pointeshivernales.json"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                handle_exception(response)
                data = await response.json(content_type=None)
            except Exception as e:
                _LOGGER.error("Error fetching json events: %s", e)
                return []
    
    events = data["evenements"]
    for event in events:
        event["dateDebut"] = datetime.fromisoformat(event["dateDebut"])
        event["dateFin"] = datetime.fromisoformat(event["dateFin"])
        
    return sorted(events, key=lambda e: e["dateDebut"])


async def fetch_available_offers():
    """Fetch available offers from Hydro API."""
    url = "https://donnees.solutions.hydroquebec.com/donnees-ouvertes/data/json/pointeshivernales.json"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            handle_exception(response)
            try:
                data = await response.json(content_type=None)
            except Exception as e:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="json_error"
                ) from e
    
    return data["offresDisponibles"]

async def fetch_offers_descriptions():
    """Fetch offers descriptions from Hydro API."""
    url = "https://donnees.hydroquebec.com/api/explore/v2.1/catalog/datasets/evenements-de-pointe-offres-disponibles/records"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            handle_exception(response)
            try:
                data = await response.json(content_type=None)
            except Exception as e:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="json_error"
                ) from e
    
    return data["results"]
