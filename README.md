# ❄️ Hydro-Québec Peak Events in Home Assistant

![illo-hero-periodes-pointe-16-9](https://github.com/user-attachments/assets/d329116b-6cbd-4cf9-9088-4a1f529f60bf)

> [!IMPORTANT]
> **This repository is archived and no longer maintained.**
>
> HydroPeak is now part of Home Assistant core as the official **[Hydro-Québec Peak Events](https://www.home-assistant.io/integrations/hydroquebec_peak/)** integration, available starting with **Home Assistant 2026.11**. No HACS install is needed anymore.

## Migrating to the official integration

1. Update Home Assistant to **2026.11** or newer.
2. Remove the HydroPeak integration from **Settings** > **Devices & services**.
3. Uninstall HydroPeak from HACS (or delete `custom_components/hydropeak` if installed manually), then restart Home Assistant.
4. Go to **Settings** > **Devices & services** > **Add Integration** and select **Hydro-Québec Peak Events**.
5. Pick your peak savings offer and update your automations to use the new entities.

[![Open your Home Assistant instance and start setting up the integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=hydroquebec_peak)

Full documentation: <https://www.home-assistant.io/integrations/hydroquebec_peak/>

## About this project

HydroPeak was a lightweight custom integration for monitoring Hydro-Québec winter peak events using Hydro-Québec open data, with no account or login required. It supported both Residential and Business peak savings programs such as **Flex-D** and **Winter Credit**.

Thanks to everyone who installed it, reported issues and shared automations along the way. 💙

### Sources

- [Événements de pointe, Saison hivernale (offers and descriptions)](https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/information/)
- [Événements de pointe, Saison hivernale (all published events)](https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/table/?sort=datedebut)

## Community

Questions about the official integration or want to share automations? Join the Domo-Québec Discord in the #general-hydropeak channel:
https://discord.gg/M8UabTrZAj

## License

This project is licensed under the MIT License, see the [LICENSE](LICENSE) file for details.
