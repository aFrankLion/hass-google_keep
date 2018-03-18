# hass-google_keep
Custom component for Home Assistant to enable adding to and updating lists on Google Keep.

This component relies on gkeepapi, an unofficial client for the Google Keep API (https://github.com/kiwiz/gkeepapi).

Example configuration.yaml entry:
```
google_keep:
  username: 'this_is_my_username@gmail.com'
  password: 'this is my Google App password'
```

With this custom component loaded, a new service named `google_keep.add_to_list` is available.
This service data call has two inputs: `title` and `items`, where `title` is the title of the Google Keep list, and `items` is a either a list of items, or a string.
A string input for 'items' is parsed for multiple items separated by 'and' and/or commas.
