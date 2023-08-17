from lib.external.umqttsimple import MQTTClient
from constants.secrets import MQTT
from constants.constants import get_debug, VERSION, AC_VOLTS
from machine import unique_id
from ubinascii import hexlify

serial = hexlify(unique_id()).decode()
d_print = get_debug("MQTT")


# Get HA device string
def __get_discovery_device(mac):
    suggested_area = "Utility"
    name = "Current Sensors"
    manufacturer = "SPZ Software"
    model = "n16 Current"
    return '{' + f'"connections":[["mac","{mac}"]],"identifiers":"{serial}","suggested_area":"{suggested_area}","name":"{name}","manufacturer":"{manufacturer}","model":"{model}","sw":"{VERSION}"' + '}'

# Get HA discovery string for a current entity
def __get_discovery_current_entity(device, pin, mac):
    # Prettiest JSON I've ever seen
    ha_device = __get_discovery_device(mac)
    name = f'Power Sensor #{device+1}-{pin}'
    unique_id = f'{MQTT["topic"]}_{device}_{pin}'
    state_topic = f'homeassistant/sensor/{unique_id}/state'
    return '{' + f'"name":"{name}","device_class":"power","state_topic":"{state_topic}","unique_id":"{unique_id}","unit_of_measurement":"W","device":{ha_device}' +'}'

# Get HA discovery string for the logging entity
def __get_discovery_log_entity(mac):
    ha_device = __get_discovery_device(mac)
    name = f'Current Sensor Logs'
    unique_id = f'{MQTT["topic"]}_logs'
    state_topic = f'homeassistant/sensor/{unique_id}/state'
    return '{' + f'"name":"{name}","device_class":"power","state_topic":"{state_topic}","unique_id":"{unique_id}","device":{ha_device}' +'}'


class PicoMQTTClient:
    last_message = 0
    message_interval = 5
    counter = 0

    # Initilize
    def __init__(self, mac_address):
        d_print("Initializing MQTT")
        self.mac_address = mac_address
        self.client = MQTTClient(MQTT["client_id"], MQTT["server_ip"], user=MQTT["username"], password=MQTT["password"], keepalive=30)

    # Connect to MQTT
    def connect(self):
        self.client.connect(True)
        d_print(f"Connected to {MQTT['server_ip']} MQTT Broker as {MQTT['username']}")

    # Disconnect from MQTT
    def disconnect(self):
        self.client.disconnect()
        d_print(f"Disconnected from {MQTT['server_ip']}")
        
    # Send discovery payloads to MQTT Broker
    def discover(self, device):
        # Register Current Entities
        for x in range(16):
            self.publish(f"homeassistant/sensor/{MQTT['topic']}_{device}_{x}/config", __get_discovery_current_entity(device, x, self.mac_address))

        # Register Logging Entity
        self.publish(f"homeassistant/sensor/{MQTT['topic']}_logs/config", __get_discovery_log_entity(self.mac_address))

    # Publish Log message
    def publish_log(self, data):
        topic = f"homeassistant/sensor/{MQTT['topic']}_logs/state"
        self.publish(topic, data)

    # Publish Measured Current to MQTT
    def publish_current(self, device, pin, data):
        topic = f"homeassistant/sensor/{MQTT['topic']}_{device}_{pin}/state"
        self.publish(topic, data * AC_VOLTS)

    # Raw publish
    def publish(self, topic, payload):
        try:
            self.client.publish(topic, msg=str(payload))
            d_print(f"Published '{str(payload)}' to '{topic}'")
        except Exception as e:
            d_print(f"Failed to publish: '{e}', attempting to reconnect")
            self.disconnect()
            self.connect()