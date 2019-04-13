import homeassistant.loader as loader

# The domain of your component. Should be equal to the name of your component.
DOMAIN = 'hello_mqtt'

# List of component names (string) your component depends upon.
DEPENDENCIES = ['mqtt']


CONF_TOPIC = 'topic'
DEFAULT_TOPIC = 'home-assistant/hello_mqtt'


def setup(hass, config):
    """Set up the Hello MQTT component."""
    mqtt = hass.components.mqtt
    topic = config[DOMAIN].get(CONF_TOPIC, DEFAULT_TOPIC)
    entity_id = 'hello_mqtt.last_message'

    # Listener to be called when we receive a message.
    # The msg parameter is a Message object with the following members:
    # - topic, payload, qos, retain
    def message_received(msg):
        """Handle new MQTT messages."""
        hass.states.set(entity_id, msg.payload)

    # Subscribe our listener to a topic.
    mqtt.subscribe(topic, message_received)

    # Set the initial state.
    hass.states.set(entity_id, 'No messages')

    # Service to publish a message on MQTT.
    def set_state_service(call):
        """Service to send a message."""
        mqtt.publish(topic, call.data.get('new_state'))

    # Register our service with Home Assistant.
    hass.services.register(DOMAIN, 'set_state', set_state_service)

    # Return boolean to indicate that initialization was successfully.
    return True
