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

## Bonus - Add Dates to Google Calendar
To allow HASS to add the bin dates to your google calendar, you first need to find the calendar ID. From within the Google Calendar web app find the cog icon and select settings. From the settings page pick which calendar you wish to use under the "Settings for my calendars" heading. Then scroll down to the "Integrate calendar" section. The ID for that calendar will be just below the section header.  

Now head over to the google scripts page (https://script.google.com/home). Create a new project, give it a title and paste the below script into the code pane (remembering to also update your calendar ID in the script).

```
function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  var calendar = CalendarApp.getCalendarById('yourcalendarIDgoesHere'); 
  var title = data.title;
  var date = new Date(data.date);
  var existing = calendar.getEventsForDay(date);

  for (var i = 0; i < existing.length; i++) {
    if (existing[i].getTitle() === title) {
      return ContentService.createTextOutput("Event already exists");
    }
  }

  // Create the all-day event
  var event = calendar.createAllDayEvent(title, date);

  // Set event color (see list below for colorId values)
  event.setColor(CalendarApp.EventColor.GRAY); // or use a specific colorId like '7' for gray

  // Add notification for the day before at 8 PM
  var notificationTime = new Date(date);
  notificationTime.setDate(notificationTime.getDate() - 1);
  notificationTime.setHours(20, 0, 0, 0); // 8 PM
  event.addPopupReminder((date - notificationTime) / 60000); // minutes before

  return ContentService.createTextOutput("Event created");
}
```

You may also want to tweak other details like EventColor or Notification setup.  

Once you're happy you need to deploy the script as a web app, leave "Execute as" at default and allow anyone to access (less than ideal but the url is so complex that nobody is likely to bruteforce it).  
After hitting deploy, you'll have to jump through some authorisation loops and at the end take note of the deployment url.  

Back in HASS you can now add Rest Commands to your configuration.yaml to call this script (update url and sensor names to match yours)
```
rest_command:
  add_black_bin_day_to_calendar:
    url: "https://script.google.com/macros/s/sjhakjfhalkfjhldskfhlksdjhlkjhalfhasdlkfjhldkjshf/exec"
    method: POST
    headers:
      Content-Type: application/json
    payload: >
      {
        "title": "Black Bin Collection",
        "date": "{{ states('sensor.next_bin_date_black') }}"
      }
  add_blue_bin_day_to_calendar:
    url: "https://script.google.com/macros/s/sjhakjfhalkfjhldskfhlksdjhlkjhalfhasdlkfjhldkjshf/exec"
    method: POST
    headers:
      Content-Type: application/json
    payload: >
      {
        "title": "Blue Bin Collection",
        "date": "{{ states('sensor.next_bin_date_blue') }}"
      }
```
Finally create automation that triggers on Next Black Bin sensor change that Performs action RESTful Command: add_black_bin_day_to_calendar  

Something like
```
alias: Add Black Bin Collection Day to Calendar
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.next_bin_date_black
conditions: []
actions:
  - action: rest_command.add_black_bin_day_to_calendar
    data: {}
    response_variable: Response
mode: single
```
When I get time I will look at closing down the anonymous access issue in there.



