# hass-google_keep
Custom component for [Home Assistant](https://home-assistant.io/) to enable adding to and updating lists on [Google Keep](https://keep.google.com/).

## Installation
Add the `google_keep` folder and its contents to the `custom_components` folder in your Home Assistant configuration directory, and add the `google_keep` component to your `configuration.yaml` file.

### Example configuration.yaml entry
```yaml
google_keep:
  username: "this_is_my_username@gmail.com"
  password: "this_is_my_Google_App_password"
  list_name: "Grocery"
```
`list_name` is an optional configuration key that sets a default name for the Keep list to update.

### Dependencies
This component relies on [gkeepapi](https://github.com/kiwiz/gkeepapi), an unofficial client for the Google Keep API.

## Usage
The original intended use of this component was to restore the capability of Google Assistant to add items to Google Keep lists.
I accomplish this with a combination of this custom component running on Home Assistant and [IFTTT](https://ifttt.com/).

### Home Assistant service
With this custom component loaded, a new service named `google_keep.add_to_list` is available.
This service call has two data inputs: `title` and `items`, where `title` is the title of the Google Keep list to update, and `items` is a either a list or string of items to add to the list.
A string input for `items` is parsed for multiple items separated by 'and' and/or commas.

Here is an example of using the service in an automation to add batteries for smart home devices to a list titled "Home Supplies":
```yaml
automation:
  - alias: Low Battery Notification
    trigger:
      - platform: numeric_state
        entity_id:
        - sensor.front_door_battery
        - sensor.hallway_smoke_co_alarm_battery
        - sensor.bedroom_sensor_battery
        below: 20
    action:
      service: google_keep.add_to_list
      data_template:
        title: 'Home Supplies'
        items: 'Batteries for {{ trigger.to_state.name }}.'
```

### IFTTT Template
A combination of the [Google Assistant](https://ifttt.com/google_assistant) trigger and the [Webhooks](https://ifttt.com/maker_webhooks) action is used to call the new Home Assistant service via Google Assistant.
One IFTTT applet must be made per Google Keep list of interest, with the list name (e.g., 'Grocery' in the example below) hardcoded into the applet.

**IF**: Google Assistant/Say a phrase with a text ingredient  
*What do you want to say?*: Add $ to the grocery list  
*What do you want the Assistant to say in response?*: Okay, adding $ to your grocery list

**THEN**: Webhooks/Make a web request  
*URL*: https://thisismyhassurl.org/api/services/google_keep/add_to_list?api_password=this_is_my_hass_api_password  
*Method*: POST  
*Content Type*: application/json  
*Body*: { "title":"Grocery", "items":"{{TextField}}" }
