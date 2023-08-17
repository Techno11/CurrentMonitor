############################################################################################################
################### Rename this file to secrets.py and set the below configs accordingly ###################
############################################################################################################


################### WIFI SETTINGS ###################
SSID="my_ssid"
PASSWORD="my_password"

# Leave as None for DHCP
STATIC=None

# To Use Staic IP, uncomment this dict
# STATIC= {
#     "ip": "10.0.0.2",
#     "subnet": "255.255.255.0",
#     "gateway": "10.0.0.1",
#     "dns": "1.1.1.1"
# }

################### MQTT SETTINGS ###################
MQTT = {
    "server_ip": "10.0.100.5",
    "client_id": "spz_current_16n",
    "topic": "mux_current",
    "username": "test",
    "password": "test"
}