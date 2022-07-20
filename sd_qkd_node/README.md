# Software-Defined QKD Node

The module is mainly composed by the [FastAPI](https://fastapi.tiangolo.com/) app which 
exposes some RESTApi on two sides ([routers](routers) module):
- One side for the SAEs that want to connect with a secure channel with other SAEs
- One side for the control plane of the SDN Controller

There is also a [database](database) module which is again divided in two parts:

- The local database, which stores the keys provided by the `qcs`
- The shared database, shared between all nodes and which stores information about the keys provided to the SAEs

## Execution

If you want to start the SD-QKD node you must first execute the SDN Controller.\
Once the Controller is started, open a terminal inside `qkd` folder and then type:

```bash
python -m sd_qkd_node
```

Use the `--config node_name` (ex. *alice*, that is the default configuration)
flag to select the desired configuration in the [config file](configs/config.ini).

This will start a server (in the [channel](channel) module) listening for the related `qcs`
and then the [FastAPI](https://fastapi.tiangolo.com/) app that connects to the Controller.

## API

The [routers](routers) module is divided in two submodules:
* The *Key Manager Entity* ([kme](routers/kme)) module which handles the SAEs requests
* The *SDN Agent* ([sdn_agent](routers/sdn_agent)) module which manages the control messages 
 exchanged with the *SDN Controller*

### KME

The Kme module exposes towards the SAEs these APIs: 
* [*enc_keys*](routers/kme/enc_keys.py) called by the master SAE to make the kme reserve a number of keys with a specified length
* [*dec_keys*](routers/kme/dec_keys.py) called by the slave SAE to get the keys reserved by the kme upon the request of the master SAE
* [*key_relay*](routers/kme/key_relay.py) called by other KMEs to relay a key when the connection is multi-hop
* [*status*](routers/kme/status.py) to get the status of the connection

### SDN Agent

The SDN Agent exposes these APIs:
* [*link_confirmed*](routers/sdn_agent/link_confirmed.py) called by the SDN Controller to confirm a new QC passing information about
the companion KME on the QC
* [*open_key_session*](routers/sdn_agent/open_key_session.py) called by a SAE who wants to start a connection with another one
* [*register_app*](routers/sdn_agent/register_app.py) called by the Controller to assign a Ksid to a connection,
when also the second SAE has been registered
* [*close_connection*](routers/sdn_agent/close_connection.py) called by a SAE who wants to close a connection