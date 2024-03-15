from pyaoscx.session import Session
from pyaoscx.device import Device
import yaml
import urllib3

urllib3.disable_warnings()

inventory = dict()
# Load YAML Inventory data
print("Building inventory...")
with open("inventory.yaml", "r") as yaml_file:
    inventory = yaml.load(yaml_file, Loader=yaml.FullLoader)

for _, switch in inventory.items():
    if "variable_file" in switch.keys() and switch["variable_file"] != "":
        with open("vars/" + switch["variable_file"], "r") as yaml_file:
            switch_var_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
            switch.update(switch_var_dict)

version = "10.09"

# Modify this variable
vlan_list = [100]

for _, switch in inventory.items():
    if "role" in switch.keys() and switch["role"] == "access":
        print("Connecting to switch {0}".format(switch["hostname"]))
        switch_ip = switch["mgmt_int_ip"]
        sesh = Session(switch_ip, version)
        sesh.open(switch["login_user"], switch["login_pw"], use_proxy=False)

        sw = Device(sesh)
        sw.session = sesh

        for vlan in vlan_list:
            # Try block is used so that session closes even on error.
            try:
                print("Configuring VLAN {0}...".format(vlan))

                # Create VLAN obj
                tmp_vlan = sw.vlan(vlan)

                # apply() will create the VLAN or update it if existing
                try:
                    tmp_vlan.apply()
                except Exception:
                    pass

                if not tmp_vlan.materialized:
                    print("ERROR: VLAN {0} configuration failure".format(vlan))
                    quit(-1)
                else:
                    print(
                        "VLAN{0} configured successfully on {1}".format(
                            vlan, switch["hostname"]
                        )
                    )
                # Example of configuring interface with VLAN

            except Exception as error:
                print("Ran into exception: {0}. Closing session.".format(error))

            finally:
                # At the end, the session MUST be closed
                sesh.close()
