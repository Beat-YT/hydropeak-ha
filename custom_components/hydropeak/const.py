DOMAIN = "hydropeak"

CONF_OFFRE_HYDRO = "offre_hydro"
CONF_PREHEAT_DURATION = "preheat_duration"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_DEVICE_VER = "description_fr"

# time is in minutes
DEFAULT_PREHEAT_DURATION = 180
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_ANCHOR_OFFSET = 300
DEFAULT_ANCHOR_DURATION = 180

OFFRE_TABLE_URL = "https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/table/?sort=datedebut"
OFFRES_DESCRIPTION = {
    "CPC-D": "CPC-D (Winter Credit Residential)",
    "TPC-DPC": "TPC-DPC (Flex D)",
    "OEA": "OEA (option d’électricité additionnelle)",
}