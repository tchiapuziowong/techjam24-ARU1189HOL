from pyaoscx.session import Session
from pyaoscx.device import Device
import urllib3
import json
from urllib.parse import quote_plus
import jinja2
import yaml
from requests.exceptions import Timeout

urllib3.disable_warnings()


def generate_from_template(template_path, yaml_data, output_path):
    # Load device's Jinja2 template
    with open(template_path, "r") as template_file:
        template_content = template_file.read()
    template = jinja2.Template(template_content)
    # Load YAML device specific data
    with open(yaml_data, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    # Render full config using template with YAML data
    result = template.render(data)
    # Write the config to the output file
    with open(output_path, "w") as output_file:
        output_file.write(result)


def tftp_configuration(switch_ip, switch_dict, tftp_server):
    version = "10.09"
    sw = Session(switch_ip, version)
    config_name = switch_dict["hostname"] + ".txt"
    remote_file = "tftp://" + tftp_server + "/" + config_name

    print("Connecting to new switch...")

    # Try block is used so that session closes even on error.
    try:
        print("Transferring config to new switch...")

        sw.open(switch_dict["login_user"], switch_dict["login_pw"])

        ztp_switch = Device(sw)
        ztp_switch.session = sw
        config = ztp_switch.configuration()

        success = config.tftp_switch_config_from_remote_location(
            config_file_location=remote_file,
            config_name="running-config",
            vrf="default",
        )

        if success:
            print("switch {0} configured successfully".format(switch_dict["hostname"]))
        else:
            print("ERROR: switch configuration failure")
            quit(-1)

    except Timeout:
        # When changing configuration on VLAN 1 on uplinks to AGG
        # DHCP IP will be removed/changed and a Timeout error
        # would occur due to lack of connectivity to initial
        # DHCP IP found through LLDP
        print("Timeout occurred during transfer - check switch")

    except Exception as error:
        print("Ran into exception: {0}. Closing session.".format(error))

    finally:
        # At the end, the session MUST be closed
        sw.close()


# Load YAML Inventory data
print("Loading inventory...")
inventory = dict()
with open("inventory.yaml", "r") as yaml_file:
    inventory = yaml.load(yaml_file, Loader=yaml.FullLoader)

switch_mac_dict = dict()

for _, data in inventory.items():
    switch_mac_dict[data["mac_address"]] = data["hostname"]

# Try block is used so that session closes even on error.
version = "10.09"
core_switch_ip = inventory["AGG1A-8325"]["mgmt_ip"]
tftp_server = inventory["AGG1A-8325"]["tftp_server"]
s = Session(core_switch_ip, version)
s.open(
    inventory["AGG1A-8325"]["login_user"],
    inventory["AGG1A-8325"]["login_pw"],
    use_proxy=False,
)

switch = Device(s)

print("Retrieving LLDP neighbors...")
try:
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
            if "chassis_id" in data.keys():
                if data["chassis_id"] in switch_mac_dict.keys():
                    device_inventory_hostname = switch_mac_dict[data["chassis_id"]]
                    ip_addr = int_dict[key]["neighbor_info"]["mgmt_ip_list"]
                    ipv4_addr = ip_addr.split(",")
                    ip_addr = ipv4_addr[0]

                    # Only provision devices whose hostname isn't matching inventory
                    if (
                        inventory[device_inventory_hostname]["template_file"] != ""
                        and data["neighbor_info"]["chassis_name"]
                        != device_inventory_hostname
                    ):
                        output_path = (
                            "C:/Users/Administrator/Desktop/tftpboot/"
                            + device_inventory_hostname
                            + ".txt"
                        )
                        temp_file = (
                            "./templates/"
                            + inventory[device_inventory_hostname]["template_file"]
                        )
                        vars_file = (
                            "./vars/"
                            + inventory[device_inventory_hostname]["variable_file"]
                        )
                        generate_from_template(
                            template_path=temp_file,
                            yaml_data=vars_file,
                            output_path=output_path,
                        )
                        tftp_configuration(
                            ip_addr,
                            inventory[switch_mac_dict[data["chassis_id"]]],
                            tftp_server,
                        )
