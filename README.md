# hass-google_keep
Custom component for Home Assistant to enable adding to and updating lists on Google Keep.

## Installation
Add the `google_keep.py` file to the `custom_components` folder in your Home Assistant configuration directory, and add the `google_keep` component to your `configuration.yaml` file.

### Example configuration.yaml entry
```
google_keep:
  username: "this_is_my_username@gmail.com"
  password: "this_is_my_Google_App_password"
  list_name: "Grocery"
```
`list_name` is an optional configuration key that sets a default name for the Keep List to update.

### Dependencies
This component relies on gkeepapi, an unofficial client for the Google Keep API (https://github.com/kiwiz/gkeepapi).

## Usage
The original intended use of this component was to restore the capability of Google Assistant to add items to Google Keep lists.
I accomplish this with a combination of this custom component running on Home Assistant and IFTTT.

### Home Assistant service
With this custom component loaded, a new service named `google_keep.add_to_list` is available.
This service call has two data inputs: `title` and `items`, where `title` is the title of the Google Keep list to update, and `items` is a either a list or string of items to add to the list.
A string input for `items` is parsed for multiple items separated by 'and' and/or commas.

### IFTTT Template
A combination of the Google Assistant trigger and the Webhooks action is used to call the new Home Assistant service via Google Assistant.
One IFTTT applet must be made per Google Keep list of interest, with the list name (e.g., 'Grocery' in the example below) hardcoded into the applet.

**IF**: Google Assistant/Say a phrase with a text ingredient  
*What do you want to say?*: Add $ to the grocery list  
*What do you want the Assistant to say in response?*: Okay, adding $ to your grocery list

**THEN**: Webhooks/Make a web request  
*URL*: https://thisismyhassurl.org/api/services/google_keep/add_to_list?api_password=this_is_my_hass_api_password  
*Method*: POST  
*Content Type*: application/json  
*Body*: { "title":"Grocery", "items":"{{TextField}}" }
