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
            "offre": record["offre"],
            "dateDebut": datetime.fromisoformat(record["datedebut"]),
            "dateFin": datetime.fromisoformat(record["datefin"]),
            "plageHoraire": record["plagehoraire"],
            "duree": record["duree"],
            "secteurClient": record["secteurclient"],
        }
        for record in data["results"]
    ]
    return sorted(events, key=lambda e: e["dateDebut"])

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
