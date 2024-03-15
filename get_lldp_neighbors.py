from pyaoscx.session import Session
from pyaoscx.device import Device
import urllib3
import json
from urllib.parse import quote_plus
import yaml

urllib3.disable_warnings()

# Load YAML Inventory data
print("Loading inventory...")
inventory = dict()
with open("inventory.yaml", "r") as yaml_file:
    inventory = yaml.load(yaml_file, Loader=yaml.FullLoader)

switch_mac_dict = dict()

for _, data in inventory.items():
    switch_mac_dict[data["mac_address"]] = data["hostname"]

version = "10.09"
core_switch_ip = inventory["AGG1A-8325"]["mgmt_ip"]

s = Session(core_switch_ip, version)

print("Retrieving LLDP neighbors...")
# Try block is used so that session closes even on error.
try:
    s.open(
        inventory["AGG1A-8325"]["login_user"],
        inventory["AGG1A-8325"]["login_pw"],
        use_proxy=False,
    )

    switch = Device(s)
    # Gathers LLDP neighbors from ALL interfaces but a single interface can be specified
    port = "*"
    port_quote = quote_plus(port)
    request = s.request(
        "GET", "system/interfaces/" + port_quote + "/lldp_neighbors?depth=3"
    )
    lldp_dict = json.loads(request.text)

except Exception as error:
    print("Ran into exception: {0}. Closing session.".format(error))

finally:
    # At the end, the session MUST be closed
    s.close()

for interface, int_dict in lldp_dict.items():
    if int_dict:
        for key, data in int_dict.items():
            if "chassis_id" in data.keys() and "neighbor_info" in data.keys():
                print(
                    "Found neighbor: {0} - {1} on port {2}".format(
                        data["neighbor_info"]["chassis_name"],
                        data["chassis_id"],
                        data["port_id"],
                    )
                )
