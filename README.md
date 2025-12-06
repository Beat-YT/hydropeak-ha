# ❄️ Hydro-Québec Peak Events in Home Assistant 

![illo-hero-periodes-pointe-16-9](https://github.com/user-attachments/assets/d329116b-6cbd-4cf9-9088-4a1f529f60bf)


Hydro-Peak is an easy to use Home Assistant integration designed to help you monitor Hydro-Québec peak events. This integration helps you optimize your energy consumption and potentially reduce costs by leveraging preheat events and peak event timings.


## Installation

### 1. Install the integration *(Recommended: via HACS)*

The easiest way to install **HydroPeak** is through [**HACS**](https://www.hacs.xyz/).  
Find HydroPeak in HACS and install it directly from the UI.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Beat-YT&repository=hydropeak-ha)


Alternatively, you may install it manually:

- Download the repository files.
- Copy `custom_components/hydropeak` and paste it into home assistant's `custom_components` folder.

### 2. Add the integration in Home Assistant

- After installation, go to **Configuration** > **Integrations** > **Add Integration** and search for **HydroPeak**.
- Configure the integration:
  - **Select Your Hydro-Québec Savings Offer:** Choose between options such as **Flex-D** or **Winter Credit**
  - Set your **Preheat Start** time (when your devices should pre-heat before a peak event begins)


## Sensors

Once configured, HydroPeak will create the following sensors in Home Assistant:

- **Event Begin**: A timestamp showing when the peak event will begin.
- **Event End**: A timestamp indicating when the peak event will end.
- **Preheat Start**: A timestamp when devices should start preheating or preparing, as configured during setup.

These sensors allow you to automate and regulate your energy usage based on the upcoming peak events.

## About

HydroPeak is a standalone integration, it does not connect to any Hydro-Québec customer account and does not require a login. It only uses publicly available open data from Hydro-Québec, which keeps the setup simple, reliable and privacy friendly.

The integration supports both Residential and Business peak savings programs. When you configure it in Home Assistant, it automatically retrieves the list of active offers for the current winter season along with their descriptions. It then keeps the peak event schedule updated during the day so your Home Assistant automations can use the correct times for preheat periods and peak events.

### Sources:
A detailed list of Hydro-Québec offers and descriptions, as well as information about open data, can be found here: <br> [Événements de pointe – Saison hivernale](https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/information/)

A list of all events published by Hydro-Québec is also available: <br> [Événements de pointe – Saison hivernale — Données ouvertes Hydro-Québec](https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/table/?sort=datedebut)

## Community & Support

Have questions, feature ideas, or want to share your automations using HydroPeak?

Join the Domo-Québec Discord community and chat with others in the #general-hydropeak channel!

📩 Discord invite:
https://discord.gg/M8UabTrZAj

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
