# WorthingBinDayScraper
Scrapes next bin day info from the Adur &amp; Worthing website and serves an API endpoint which can be read by the HASS rest integration.

To use add this repo (https://github.com/MikeGrimwade/WorthingBinDayScraper) to the Home Assistant add-on store repositories list. Then refresh the page and you should see the add-on appear in the add-on store list. 

Install the Add-On then configure your UPRN value in the config page. Once you've done that you can start the add-on.

To determine the UPRN for your address visit the Adur &amp; Worthing website (https://www.adur-worthing.gov.uk/bin-day/) and view your upcoming bin days by entering postcode and selecting your address. You will find your UPRN value in the url looking something like brlu-selected-address=1234567890

While the add-on is running, GET calls to http://[HASS-IP]:5000/bin-dates will return JSON values.

{
  "black_bin_next": "2025-05-27",
  "black_bin_next2": "2025-06-10",
  "blue_bin_next": "2025-05-19",
  "blue_bin_next2": "2025-06-03",
  "garden_bin_next": "2025-05-19",
  "garden_bin_next2": "2025-05-27"
}



