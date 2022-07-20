# Secure Application Entity

This module is only for testing purposes.

It is composed by a [FastAPI](https://fastapi.tiangolo.com/) app in parallel to an action menu that allows the user
to select the action to execute (print the SAE's UUID, connect to another SAE or exit).

## Execution

To start the SAE you must open a terminal inside `qkd` folder and then type:

```bash
python -m sae
```

Use the `--config node_name` (ex. *alice*, that is the default configuration)
flag to select the KME the SAE will refer to.

Use the `--ip ip_address` flag to set the ip address of the SAE, if needed (default is "localhost").

Use the `--port port_number` flag to set the port number of the SAE, if needed (default is 9000).

Configurations can always be changed in the [config file](configs/config.ini).

## API

These are the exposed RESTApi ([routers](routers) module):
* [*ask_connection*](routers/ask_connection.py) to communicate to the other SAE the will to open a connection
* [*assign_ksid*](routers/assign_ksid.py) called by the KME passing the Ksid assigned by the SDN Controller
to the required connection
* [*ask_key*](routers/ask_key.py) to make the companion SAE ask for the new Key
* [*ask_close_connection*](routers/ask_close_connection.py) to communicate the other SAE the will to close the connection