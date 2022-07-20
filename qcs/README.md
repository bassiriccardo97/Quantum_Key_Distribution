# Quantum Channel Simulator

## Execution

If you want to start the quantum channel simulator, open a terminal inside `qkd` folder
and then type:

```bash
python -m qcs
```

Use the `--config first_node-second_node` (ex. *alice-bob*, that is the default configuration)
flag to select the desired configuration in the [config file](config.ini).

## API

The quantum channel simulator supports the following commands:

- "Get keys by IDs"
- "Get keys"
- "Flush keys"
- "Delete by IDs"

### Get keys by IDs

Example request:

```
{
    "command": "Get keys by IDs"
    "attribute": *ignored*
    "value": [
        "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
        "bc490419-7d60-487f-adc1-4ddcc177c139"
    ]
}
```

"value" field is an array of IDs of blocks. If a key with a given ID is not found, an
error message is returned ([TODO1](#TODO1)).

Example response ([TODO3](#TODO3)):

```
{
    [
        {
            "time": 1234567891011,
            "ID": "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
            "Key": [36, 39, 75, 136, 254, 145, 133]
        },
        {
            "time": 1234567891028,
            "ID": "bc490419-7d60-487f-adc1-4ddcc177c139",
            "Key": [44, 12, 222, 136, 221, 11, 101]
        }
    ]
}
```

### Get keys

Example request:

```
{
    "command": "Get keys"
    "attribute": *ignored*
    "value": 2
}
```

*N* is the number of blocks the client wants to retrieve ([TODO2](#TODO2)). If "value"
is empty, default N value is 1. If 'value' is a non-positive integer or it cannot be
interpreted as an integer, an error should be returned ([TODO1](#TODO1)).

Example response ([TODO3](#TODO3)):

```
{
    [
        {
            "time": 1234567891011,
            "ID": "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
            "Key": [36, 39, 75, 136, 254, 145, 133]
        },
        {
            "time": 1234567891028,
            "ID": "bc490419-7d60-487f-adc1-4ddcc177c139",
            "Key": [44, 12, 222, 136, 221, 11, 101]
        }
    ]
}
```

### Flush keys

Delete all the available keys in the local database. Example request:

```
{
    "command": "Flush keys"
    "attribute": *ignored*
    "value": *ignored*
}
```

Example response:
([TODO4](#TODO4))

### Delete by IDs

Delete keys with the specified IDs. Example request:

```
{
    "command": "Delete by IDs"
    "attribute": *ignored*
    "value": [
        "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
        "bc490419-7d60-487f-adc1-4ddcc177c139"
    ]
}
```

Example response:

```
{
    "command": "Keys deleted",
    "parameter": "",
    "value": "Done"
}
```

## TODOs

### TODO1

Implement error messages.

### TODO2

How can the client define a priori the number of blocks it needs, if he does not know
how many random bits it will receive within a block?

### TODO3

The given response is not valid JSON. It should be something like

```
{
    "blocks": [
        {
            "time": 1234567891011,
            "ID": "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
            "Key": [36, 39, 75, 136, 254, 145, 133]
        },
        {
            "time": 1234567891028,
            "ID": "bc490419-7d60-487f-adc1-4ddcc177c139",
            "Key": [44, 12, 222, 136, 221, 11, 101]
        }
    ]
}
```

My QC Simulator accepts the 'illegal' version if in compatibility mode, the '
legal' version otherwise.

### TODO4

Implement a response for 'Flush keys'