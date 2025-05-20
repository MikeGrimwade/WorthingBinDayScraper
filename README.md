# WorthingBinDayScraper
A Home Assistant add-on to scrape upcoming bin day info from the Adur &amp; Worthing website.

## Description
This addon will access the Adur &amp; Worthing website and serve an API endpoint which can be read by the HASS rest integration.

## Installing the Add-On
To use add this repo (https://github.com/MikeGrimwade/WorthingBinDayScraper) to the Home Assistant add-on store repositories list. Then refresh the page and you should see the add-on appear in the add-on store list. 

Install the Add-On then configure your UPRN value in the config page. Once you've done that you can start the add-on.

## Configuration
To determine the UPRN for your address visit the Adur &amp; Worthing website (https://www.adur-worthing.gov.uk/bin-day/) and view your upcoming bin days by entering postcode and selecting your address. You will find your UPRN value in the url looking something like brlu-selected-address=1234567890

## Usage
While the add-on is running, GET calls to http://localhost:5000/bin-dates will return JSON values.
```
{
  "black_bin_next": "2025-05-27",
  "black_bin_next2": "2025-06-10",
  "blue_bin_next": "2025-05-19",
  "blue_bin_next2": "2025-06-03",
  "garden_bin_next": "2025-05-19",
  "garden_bin_next2": "2025-05-27"
}
```

black_bin_next = Next black bin collection date.  
black_bin_next2 = The subsequent black bin collection date if provided.  
blue_bin_next = Next blue bin collection date.  
blue_bin_next2 = The subsequent blue bin collection date if provided.  
garden_bin_next = Next garden bin collection date.  
garden_bin_next2 = The subsequent garden bin collection date if provided.  


## Adding Sensors to Home Assistant
Add a rest sensor to your configuration.yaml file.
```
rest:
    scan_interval: 43200
    resource: http://localhost:5000/bin-dates
    sensor:
      - name: "Bin Dates"
        value_template: "{{ value_json.black_bin_next }}"
        json_attributes:
          - black_bin_next
          - black_bin_next2
          - blue_bin_next
          - blue_bin_next2
          - garden_bin_next
          - garden_bin_next2
```          
This will create a sensor with 6 attributes attached containing the dates. All you need then is to create template helpers through the UI.

Name: Next Black Bin
Device Class: Date
State Template: {{ state_attr('sensor.bin_dates', 'black_bin_next') }}

Repeat for each one you want to use.
