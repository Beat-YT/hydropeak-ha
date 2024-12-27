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

async def fetch_events(offre_hydro):
    """Fetch events from Hydro API."""
    url = "https://donnees.hydroquebec.com/api/explore/v2.1/catalog/datasets/evenements-pointe/records"
    params = {
        "select": "*",
        "limit": "20",
        "where": f"offre='{offre_hydro}'",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            try:
                handle_exception(response)
                data = await response.json()
            except Exception as e:
                _LOGGER.error("Error fetching events: %s", e)
                return []

    events = [
        {
            "datedebut": datetime.fromisoformat(record["datedebut"]),
            "datefin": datetime.fromisoformat(record["datefin"]),
        }
        for record in data["results"]
    ]
    return sorted(events, key=lambda e: e["datedebut"])

async def fetch_events_json(offre_hydro):
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
    
    evenements = data["evenements"]
    
    events = [event for event in evenements if event["offre"] == offre_hydro]
    for event in events:
        event["datedebut"] = datetime.fromisoformat(event["dateDebut"])
        event["datefin"] = datetime.fromisoformat(event["dateDebut"])
        
    return sorted(events, key=lambda e: e["datedebut"])


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
