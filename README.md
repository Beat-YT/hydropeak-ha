# HydroPeak - Home Assistant Integration for Hydro-Québec Peak Events

HydroPeak is a Home Assistant integration designed to help you monitor Hydro-Québec peak events. This integration helps you optimize your energy consumption and potentially reduce costs by leveraging preheat events and peak event timings.

## How to Setup

### 1. Install the Extension
- You can install the **HydroPeak** integration manually.
    
    **Manual Installation:**
    - Download the repository files and place them in the `custom_components/hydropeak` directory of your Home Assistant instance.

### 2. Add the Integration in Home Assistant
- After installation, add the **HydroPeak** integration in Home Assistant by navigating to **Configuration** > **Integrations** > **Add Integration** > search for **HydroPeak**.
- Configure the integration:
    - **Select Your Hydro-Québec Savings Offer:** Choose from available options such as **Flex-D** or **Winter Credit**.
    - Set your **Preheat Start** time (when your devices should prepare before the peak event starts).

## Sensors

Once configured, HydroPeak will create the following sensors in Home Assistant:

- **Event Begin**: A timestamp showing when the peak event will begin.
- **Event End**: A timestamp indicating when the peak event will end.
- **Preheat Start**: A timestamp when devices should start preheating or preparing, as configured during setup.

These sensors allow you to automate and monitor your energy usage based on the upcoming peak events.

## About

HydroPeak uses **open data** provided by Hydro-Québec to monitor peak events. The integration pulls data related to peak event schedules and offers to provide a smooth user experience with real-time updates.

A detailed list of Hydro-Québec offers and descriptions, as well as information about open data, can be found here: [Hydro-Québec Open Data - Peak Events](https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/information/).

By integrating this data with Home Assistant, users can automate their devices, manage their energy consumption more efficiently, and stay informed about peak events to reduce unnecessary energy use during peak times.

## Contributing

- Contributions are welcome! Please feel free to open an issue or submit a pull request if you'd like to improve this integration.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
