"""
Custom component for Home Assistant to enable adding to and updating lists on
Google Keep. This component relies on gkeepapi, an unofficial client for the
Google Keep API (https://github.com/kiwiz/gkeepapi).

Example configuration.yaml entry:

google_keep:
  username: 'this_is_my_username@gmail.com'
  password: 'this_is_my_Google_App_password'

With this custom component loaded, a new service named google_keep.add_to_list
is available. This service data call has two inputs: 'title' and 'things', where
'title' is the title of the Google Keep list, and 'things' is a either a list of
things, or a string. A string input for 'things' is parsed for multiple things
separated by 'and'.
"""

import asyncio
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

# Domain and component constants and validation
DOMAIN = "google_keep"
CONF_USERNAME = 'username'    # Google account username
CONF_PASSWORD = 'password'    # Google App password, https://myaccount.google.com/apppasswords
CONF_LIST_NAME = 'list_name'  # Default Google Keep list title
DEFAULT_LIST_NAME = 'Grocery'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_LIST_NAME, default=DEFAULT_LIST_NAME): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

# Service constants and validation
SERVICE_LIST_NAME = 'title'   # Title of the Google Keep list to create or update, string
SERVICE_LIST_ITEM = 'things'  # Things(s) to add to the list

SERVICE_LIST_SCHEMA = vol.Schema({
    vol.Optional(SERVICE_LIST_NAME): cv.string,
    vol.Required(SERVICE_LIST_ITEM): cv.ensure_list_csv,
})


@asyncio.coroutine
def async_setup(hass, config):
    """Setup the google_keep component."""

    import gkeepapi

    config = config.get(DOMAIN)

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    default_list_name = config.get(CONF_LIST_NAME)

    keep = gkeepapi.Keep()

    # Attempt to login
    login_success = keep.login(username, password)
    if not login_success:
        _LOGGER.error("Google Keep login failed.")
        return False

    @callback
    def add_to_list(call):
        """Add things to a Google Keep list."""

        list_name = call.data.get(SERVICE_LIST_NAME, default_list_name)
        things = call.data.get(SERVICE_LIST_ITEM)

        # Split any things in the list separated by ' and '
        things = [x for thing in things for x in thing.split(' and ')]

        # Sync with Google servers
        keep.sync()

        # Find the target list amongst all the Keep notes/lists
        for l in keep.all():
            if l.title == list_name:
                list_to_update = l
                break
        else:
            _LOGGER.info("List with name {} not found on Keep. Creating new list.".format(list_name))
            list_to_update = keep.createList(list_name)

        _LOGGER.info("Things to add: {}".format(things))
        # For each thing,
        for thing in things:
            # ...is the thing already on the list?
            for old_thing in list_to_update.items:
                # Compare the new thing to each existing thing
                if old_thing.text.lower() == thing:
                    # Uncheck the thing if it is already on the list.
                    old_thing.checked = False
                    break
            # If the thing is not already on the list,
            else:
                # ...add the thing to the list, unchecked.
                list_to_update.add(thing, False)

        # Sync with Google servers
        keep.sync()


    # Register the service google_keep.add_to_list with Home Assistant.
    hass.services.async_register(DOMAIN, 'add_to_list', add_to_list, schema=SERVICE_LIST_SCHEMA)

    # Return boolean to indicate successful initialization.
    return True
