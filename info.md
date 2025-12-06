# Hydro-Quebec 
- Hydro-Québec offers multiple savings programs based on peak events. More details are available on Hydro-Québec's website:
  - [English](https://www.hydroquebec.com/residential/energy-wise/offers-to-save-this-winter/index.html)
  - [Français](https://www.hydroquebec.com/residentiel/mieux-consommer/offres-pour-economiser-cet-hiver/index.html)

- This integration uses Hydro-Québec Open Data to provide peak event information and helps you prepare and optimize your energy usage during these times.

## Configuration

- When adding the Hydro-Peak integration to Home Assistant, you will need to know your rate plan offer. For example:
  - **Flex-D**: Your offer is `TPC-DPC`
  - **Winter Credit**: Your offer is `CPC-D`

- You can configure the integration directly within Home Assistant to align with your specific rate plan and needs.
- For a list of rate plan offers, visit [Hydro-Québec Rate Plan Offers](https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/information/)

## Automations

A blueprint is a template that simplifies the process of creating automations by providing pre-configured settings and triggers. 
Using these blueprints, you can quickly set up automations tailored to Hydro-Peak.

####  Blueprint in english: <br>
[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FBeat-YT%2Fhydropeak-ha%2Frefs%2Fheads%2Fmain%2Fblueprints%2Fhydropeak-english.yaml)

#### Blueprint en français: <br>
[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FBeat-YT%2Fhydropeak-ha%2Frefs%2Fheads%2Fmain%2Fblueprints%2Fhydropeak-french.yaml)


## Notes

- Ensure you configure the integration with the correct rate plan offer for accurate results.
- Use the sensors in your automations to turn off non-essential devices, adjust heating, or prepare your smart home for peak events.
- Do not rely on diagnostic sensors for triggering automations.
