# Quantum Key Distribution

This project implements the prototypes of Software-Defined QKD node and SDN Controller for a QKD network.
Indeed, the prototypes are used to simulate the network of the PoliQI project.\
The repository contains the following modules:

- a [Quantum Channel Simulator (QCS)](qcs/README.md)
- a [Secure Application Entity (SAE)](sae/README.md)
- a [Software-Defined QKD Node (SD-QKD node)](sd_qkd_node/README.md)
- an [SDN Controller](sdn_controller/README.md)

In summary, SD-QKD node receives requests from a SAE that want to use
quantum-generated secret keys to communicate with another SAE. 
QCS is a simulator of a quantum channel that produces the raw material that will be used to generate the keys.
The SDN Controller is in charge of managing the new connections and the network optimizations.

## Installation

1. (Optional) This project **requires Python 3.10 or higher.** If you don't
   have Python 3.10 installed system-wide, you may want to install it
   through [pyenv](https://realpython.com/intro-to-pyenv/).
2. Install [PostgreSQL](https://www.postgresql.org/download/).
3. Install [Poetry](https://python-poetry.org/docs/master/#installation).
4. In a terminal window, inside folder "qkd", install project dependencies:

```bash
poetry install
```

## Configuration setup

You have to set all the parameters needed for the correct execution of each module.

### qcs

The parameters needed to correctly set qcs can be provided with the execution command, which will be explained 
in the next section.

### sae

This module is for automated testing only. The only parameter needed to run the simulation is "average_duration", which can be set in the 
[configuration file](sae/configs/config.ini).

### sd_qkd_node

The parameters that can be modified for the SD-QKD node in the [configuration file](sd_qkd_node/configs/config.ini) are:
* "TTL", the time-to-live of received blocks.
* "SDN_CONTROLLER_IP" and "SDN_CONTROLLER_PORT", to make the node correctly connect to the Controller.
* "KEYS_AHEAD", the number of keys generated ahead in the "qkp" execution mode (see next section).

### sdn_controller

The parameters of the SDN Controller are similar to the ones of the SD-QKD node and can be found in its 
[configuration file](sdn_controller/configs/config.ini).
The only additional parameter is "n_kme", which indicates how many nodes there are in the network topology specified.

## Execution

First, an instance of PostgreSQL must run, with a database called "prod_db" with password "secret" 
(these can be different, but you must modify the configuration of [node](sd_qkd_node/configs/configs.py) and 
[Controller](sdn_controller/configs/configs.py)).

All the following commands must be executed in a terminal positioned inside
folder `qkd`.

First start the SDN Controller through the command:
```bash
poetry run python -m sdn_controller
```

Then to start the SD-QKD nodes:

```bash
poetry run python -m sd_qkd_node
```

Add the flag `-h` to see more details about additional parameters (required to correctly setup the network).
Then for each pair of `sd_qkd_nodes` you have to start a `qcs` with the command:

```bash
poetry run python -m qcs
```

Also here use the `-h` flag to see more about other parameters.
Finally start the SAEs needed:

```bash
poetry run python -m sae
```

Again, use the `-h` to know more about other parameters.

## Simulation

In this repository there is also a [script](simulator.py) to run automated simulations.
It is designed to start all the components needed to simulate the network desired.\
Since it starts every component in different processes, the parameters for those processes must be set directly in the file.\
The generic parameters for the network can be set in the configuration [file](simulation.ini).\
In particular the topology must be defined with the number of nodes, their port numbers, the qcs and the number of SAEs.
Then the other parameters to set are:
* "key_length", the length in bits (for example 128); it can have multiple values, like "64,128,256" and the max should be 8192
* "request_interval", the interval between two key requests by a SAE (integer, in the format "max,min")
* "n_connections", the number of connections desired (in the format "min,max")
* "new_connection_interval", an integer that is the mean interval time between two new connection requests.

To start the entire simulation run:

```bash
poetry run python simulator.py
```


## Sources

- https://www.etsi.org/committee/1430-qkd

## People

- [Riccardo Bassi](mailto:riccardo4.bassi@mail.polimi.it), graduate student
- [Giacomo Verticale](mailto:giacomo.verticale@polimi.it), project contact person
