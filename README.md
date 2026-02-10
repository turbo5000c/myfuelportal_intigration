# MyFuelPortal Home Assistant Integration

A Home Assistant custom integration for monitoring propane/fuel tank levels from MyFuelPortal customer portal.

## Features

- 🔐 **Secure Authentication**: Form-based login with CSRF token handling
- 📊 **Tank Level Monitoring**: Real-time percentage of fuel remaining
- ⛽ **Gallons Remaining**: Current gallons in your propane tank
- 🛢️ **Fuel Type**: Type of fuel in the tank (e.g., Propane)
- 💰 **Current Price**: Current fuel price per gallon
- 🔄 **Automatic Updates**: Updates every 5 minutes
- 🛡️ **Error Handling**: Robust error handling with automatic re-authentication

## Installation

### Manual Installation

1. Download this repository
2. Copy the `custom_components/myfuelportal` directory to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

### HACS Installation

1. Add this repository as a custom repository in HACS
2. Search for "MyFuelPortal" in HACS
3. Click Install
4. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** in Home Assistant
2. Click **+ ADD INTEGRATION**
3. Search for **MyFuelPortal**
4. Enter your MyFuelPortal account information:
   - **Email**: Your MyFuelPortal account email
   - **Password**: Your MyFuelPortal account password
   - **Fuel Vendor**: Your fuel vendor subdomain
5. Click **Submit**

### How to Determine Your Fuel Vendor

The fuel vendor is the subdomain in your MyFuelPortal URL. To find it:

1. Log in to your MyFuelPortal account in a web browser
2. Look at the URL in the address bar
3. Extract the subdomain (the part before `.myfuelportal.com`)

**Examples:**
- If your portal URL is `https://kbjohnson.myfuelportal.com`, set **fuel_vendor** to `kbjohnson`
- If your portal URL is `https://acme.myfuelportal.com`, set **fuel_vendor** to `acme`
- If your portal URL is `https://propanedelivery.myfuelportal.com`, set **fuel_vendor** to `propanedelivery`

## Sensors

The integration creates seven sensors for your tank:

### Tank Level
- **Entity ID**: `sensor.myfuelportal_tank_level`
- **Unit**: Percentage (%)
- **Icon**: 🛢️ mdi:propane-tank
- **Description**: Current fuel level as a percentage (0-100%)

### Gallons Remaining
- **Entity ID**: `sensor.myfuelportal_gallons_remaining`
- **Unit**: Gallons (gal)
- **Icon**: ⛽ mdi:gauge
- **Description**: Approximate gallons remaining in tank

### Tank Capacity
- **Entity ID**: `sensor.myfuelportal_tank_capacity`
- **Unit**: Gallons (gal)
- **Icon**: 🛢️ mdi:propane-tank
- **Description**: Total capacity of the propane tank

### Fuel Type
- **Entity ID**: `sensor.myfuelportal_fuel_type`
- **Unit**: None (string)
- **Icon**: ⛽ mdi:fuel
- **Description**: Type of fuel in the tank (e.g., PROPANE)

### Last Delivery Date
- **Entity ID**: `sensor.myfuelportal_last_delivery_date`
- **Unit**: None (date string)
- **Icon**: 📅 mdi:calendar-clock
- **Description**: Date of the last propane delivery

### Reading Date
- **Entity ID**: `sensor.myfuelportal_reading_date`
- **Unit**: None (date string)
- **Icon**: ✅ mdi:calendar-check
- **Description**: Date of the tank level reading

### Current Price
- **Entity ID**: `sensor.myfuelportal_current_price`
- **Unit**: $/gal
- **Icon**: 💰 mdi:currency-usd
- **Description**: Current fuel price per gallon

## Technical Details

### Authentication Flow
1. Fetches login page to extract CSRF token
2. Submits credentials with token to authenticate
3. Maintains session cookies for data requests
4. Automatically re-authenticates if session expires

### Data Extraction
- Scrapes HTML from MyFuelPortal website (no REST API available)
- Parses tank level from progress bar `aria-valuenow` attribute
- Extracts gallons from "Approximately X gallons in tank" text
- Extracts tank capacity and fuel type from text like "125 Gal Propane" or "125 gal. | PROPANE"
- Extracts last delivery date from text patterns on the Tank page
- Extracts tank reading date from text patterns on the Tank page
- Extracts current fuel price from price-related text on the Tank page
- Uses BeautifulSoup for HTML parsing

### Update Frequency
- **Default**: Every 5 minutes (300 seconds)
- Helps avoid excessive requests to the portal

## Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.11 or newer
- Active MyFuelPortal account

## Dependencies

- `aiohttp` - Async HTTP client (provided by Home Assistant Core)
- `beautifulsoup4==4.12.2` - HTML parsing

## Support

- **Issues**: [GitHub Issues](https://github.com/turbo5000c/myfuelportal_intigration/issues)
- **Documentation**: This README

## Known Limitations

- Only supports single tank monitoring
- Requires web scraping (no official API available)
- HTML structure changes could break parsing

## Future Enhancements

- [ ] Support for multiple tanks
- [ ] Additional sensors (price, delivery dates)
- [ ] Service for manual refresh

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This integration is provided as-is for use with Home Assistant.

## Disclaimer

This is an unofficial integration and is not affiliated with MyFuelPortal. Use at your own risk.