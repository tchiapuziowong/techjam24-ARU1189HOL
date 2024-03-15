## Welcome to Tech Jam 24!
This project contains files necessary to complete the lab activities for ARU1189HOL.

## Project Structure
```bash
├───templates/                              # Directory for Jinja2 template files
│   ├───access_6300.j2                      # Jinja2 file that is a template for generating configurations for Access switches
├───vars                                    # Directory for YAML variable files
│   ├───ACC1A-6300.yaml                     # YAML file that defines variables with specific values for 6300A
│   ├───ACC1B-6300.yaml                     # YAML file that defines variables with specific values for 6300B
├───LICENSE                                 # Project license
├───README.md                               # Document outlining project requirements
├───configure_vlans.py                      # Python script that configures a list of VLANs across Access switches
├───get_lldp_neighbors.py                   # Python script that retrieves & displays LLDP neighbors
├───inventory.yaml                          # YAML file that defines all network devices in infrastructure
├───provision_switches.py                   # Python script that discovers connected devices & provisions them  
├───requirements.txt                        # Python library requirements for project
``` 