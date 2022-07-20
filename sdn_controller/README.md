# SDN Controller

The SDN Controller is the network entity in charge of keeping the updated configuration of the network and to modify it
when needed, create the connection between two SAEs through their respective KMEs and to optimize the network and
keys consumption basing on statistics provided by the various KMEs.

To do so it makes use of the [networkx](https://networkx.org/) library in the [info](info) module for the manipulation
and visit of the network graph.

# Execution

If you want to start the SDN Controller, open a terminal inside `qkd` folder and then type:

```bash
python -m sdn_controller
```

You can also modify the settings in the [config file](configs/config.ini) depending on your needs.

This will start the [FastAPI](https://fastapi.tiangolo.com/) app, ready to register new KMEs.

# API

The SDN Controller exposes some RESTApi towards the various *SDN Agents* of KMEs:
* [*new_link*](routers/new_link.py) to add a new QC to the network, saving its information in the local database
* [*new_kme*](routers/new_kme.py) to add a new KME to the network, saving its information in the local database
* [*new_app*](routers/new_app.py) to register a new SAE which wants to open a connection towards another one, getting a KSID
* [*close_connection*](routers/close_connection.py) to close the connection between two SAEs