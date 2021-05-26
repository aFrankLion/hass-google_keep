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
The original intended use of this component was to restore the capability of Google Assistant to add things to Google Keep lists.
I accomplish this with a combination of this custom component running on Home Assistant and [IFTTT](https://ifttt.com/).

### Home Assistant service
With this custom component loaded, two services named `google_keep.add_to_list` and `google_keep.sync_shopping_list` are available.

#### Add to List
This service call has two data inputs: `title` and `things`, where `title` is the title of the Google Keep list to update, and `things` is a either a list or string of things to add to the list.
A string input for `things` is parsed for multiple things separated by 'and' and/or commas.

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
      data:
        title: 'Home Supplies'
        things: 'Batteries for {{ trigger.to_state.name }}.'
```

#### Sync Shopping List
If the Home Assistant Shopping List integration is enabled, you can use this service to synchronize your google keep list into the home assistant shopping list.
This service call has just one data input: `title` that is the Google Keep list to sync.

Here is an example of using the service in an automation to sync the list after adding an items:
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
      - service: google_keep.add_to_list
        data:
          title: 'Home Supplies'
          things: 'Batteries for {{ trigger.to_state.name }}.'
      - delay:
        seconds: 10
      - service: google_keep.sync_shopping_list
        data:
          title: 'Home Supplies'
```

Another approach could be to schedule the sync once in a while:
```yaml
automation:
  - alias: Sync google keep
    trigger:
      - platform: time_pattern
        hours: "07"
        minutes: 0
        seconds: 0
    action:
      - service: google_keep.sync_shopping_list
        data:
          title: 'Home Supplies'
```

### IFTTT applet and Home Assistant automation
A combination of the [Google Assistant](https://ifttt.com/google_assistant) trigger and the [Webhooks](https://ifttt.com/maker_webhooks) action is used to trigger the new Home Assistant service via Google Assistant.
One IFTTT applet must be made per Google Keep list of interest, with the list name (e.g., 'Grocery' in the example below) hardcoded into the applet.
For example:

**IF**: Google Assistant/Say a phrase with a text ingredient  
- *What do you want to say?*: `Add $ to the grocery list`
- *What do you want the Assistant to say in response?*: `Okay, adding $ to your grocery list`

**THEN**: Webhooks/Make a web request  
- *URL*: `https://thisismyhassurl.org/api/webhook/ABCXYZ123456`
- *Method*: `POST`
- *Content Type*: `application/json`
- *Body*: `{ "action":"call_service", "service":"google_keep.add_to_list", "title":"Grocery", "things":"{{TextField}}" }`

A Home Assistant automation to receive and process Google Assistant inputs via IFTTT can have the form:

```yaml
automation:
  - alias: Google Keep list update
    trigger:
      platform: event
      event_type: ifttt_webhook_received
      event_data:
        action: call_service
    action:
      service_template: '{{ trigger.event.data.service }}'
      data_template:
        title: '{{ trigger.event.data.title }}'
        things: '{{ trigger.event.data.things }}'
```
