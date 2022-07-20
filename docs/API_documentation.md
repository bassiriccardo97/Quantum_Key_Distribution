---
front_matter_title: QKD LabVIEW - Documentazione API author: Marco Brunero & Alberto Gatto language: it-IT
tags: [qkd, api, socket, client, LabVIEW, Python]
---

# QKD LabVIEW - Documentazione API

In questo documento vengono descritti i comandi API disponibili per il trasmettitore e ricevitore del prototipo QKD
sviluppato da Politecnico di Milano all'interno del progetto **EIT Quantum Secure Net**, in collaborazione con Italtel,
CNR, UPM, Telefonica, Cefriel.

- [QKD LabVIEW - Documentazione API](#qkd-labview---documentazione-api)
    - [Descrizione architettura](#descrizione-architettura)
        - [Controllo Hardware](#controllo-hardware)
        - [QKD Analyze](#qkd-analyze)
            - [Integrazione codice CNR](#integrazione-codice-cnr)
        - [QKD Manager](#qkd-manager)
        - [TCP Socket](#tcp-socket)
    - [API](#api)
        - [ETSI client messages](#etsi-client-messages)
            - [Get Attribute](#get-attribute)
            - [Set Attribute](#set-attribute)
        - [LKMS client messages](#lkms-client-messages)
            - [get_key](#get_key)
            - [Get key by ID](#get-key-by-id)
            - [Get keys](#get-keys)
            - [Flush keys](#flush-keys)
            - [Delete by IDs](#delete-by-ids)
        - [HW Layer messages](#hw-layer-messages)
        - [Sifted Key reconstruction messages](#sifted-key-reconstruction-messages)
            - [Start](#start)
            - [Confronto basi](#confronto-basi)
            - [Sifted key](#sifted-key)
            - [Calc BER](#calc-ber)
            - [Valid Key](#valid-key)
            - [Discard Key](#discard-key)
        - [Cascade process messages](#cascade-process-messages)

## Descrizione architettura

Il prototipo è basato su due programmi LabVIEW indipendenti, uno per il trasmettitore (Alice) e uno per il ricevitore (
Bob).

![QKD Structure](QKD_structure.png)

Entrambi i programmi sono caratterizzati dai seguenti blocchi funzionali:

- Controllo del rispettivo Hardware
- QKD Analyze. Riceve da Hardware i qbit generati o qbit usati in ricezione e il conteggio fotoni. Si occupa poi di
  comunicare con il partner durante le fasi di creazione della chiave.
- QKD Manager. Riceve da QKD Analyze la chiave prodotta e la salva in keys.db, salvato localmente. Risponde inoltre ad
  eventuali richieste di chiavi da parte di client esterni.
- Logger. Salva localmente su file di testo la chiave e, eventualmente, anche le fasi intermedie, per debug.
- Un TCP Socket server. Può prendere in carico multiple connessioni di client esterni. Smista richieste TCP ricevute
  verso i moduli in grado di prendere in carico la richiesta.
- TCP Client che si connetterà al TCP server del partner e verrà utilizzato per comunicare su canale pubblico durante la
  costruzione della chiave.

Per quanto possibile, si è cercato di avere questi componenti uguali nei due programmi. Tuttavia, il modulo Hardware e
il modulo QKD Analyze sono diversi.

### Controllo Hardware

Al momento, la generazione e acquisizione sono solamente simulate.

E' possibile iniziare la procedura di trasmissione premendo il tasto <kbd>Start</kbd> su uno dei due programmi. In
generale la procedura è

1. (Start comandato da Bob. Viene trasmesso ad Alice il comando Start)
2. Alice trasmette a Bob il comando di Start.
3. Bob prepara il proprio hardware. Quando è pronto, notifica Alice.
4. Alice inizia la trasmissione su canale Quantum.

Il punto 3 deve essere ancora implementato.

In questo momento, con generazione e ricezione simulate, si rende necessario trasmettere a Bob anche i qbit che Alice ha
deciso di utilizzare nell'intera sequenza. Questa informazione viene trasmessa durante il punto 2. Bob utilizza
l'informazione per generare una sua sequenza di qbit con un determinato tasso di falsi positivi e negativi. In ogni
caso, i qbit di Alice non sono noti al processo QKD Analyze di Bob.

Quando non sarà più una simulazione, durante il punto 2 verrà solo trasmesso l'ID che verrà assegnato alla chiave, da
entrambi i partner.

- [ ] Implementare classi per il controllo di tutto l'hardware:
    - [ ] Laser (sono tre?)
    - [ ] Attenuatore variabile
    - [ ] General Photonics Polarization State Generator
    - [ ] Rotatori di polarizzazione
    - [ ] Recupero polarizzazione
    - [ ] SPAD
    - [ ] NI DAQ per generazione segnali
- [ ] Implementare procedura di calibrazione potenza e recupero polarizzazione.

### QKD Analyze

Questo processo recupera quando prodotto dal processo di generazione o ricezione, alla fine di una misura. In
particolare:

- Trasmettitore: ID, vettore U8 rappresentante i qbit (valori: 0-3)
- Ricevitore: ID, vettore U8 rappresentante i qbit (valori: 0-3) e vettore U8 rappresentante i photon counting (valori:
  0-1)

Quando il ricevitore (Bob) ottiene queste informazioni inizia la fase di costruzione della chiave, attraverso scambio di
messaggi su canale pubblico.

Qui possiamo vedere la sequenza completa, dal momento della pressione del tasto <kbd>Start</kbd> al Trasmettitore fino
alla conclusione.

![QKD Key sequence](QKD_Key.png)

La procedura si conclude con successo se il Bit Error Rate misurato è risultato inferiore a livello di soglia; in questo
caso la chiave verrà esposta al key manager.

Ogni riquadro rosso in figura rappresenta un metodo della classe `QKD Analysis.lvclass`.

Compito di questo processo è anche il logging delle chiavi su file json locale, per debug. Questo viene fatto dalla
classe `JSON Logging.lvclass`. Sia Alice che Bob salvano la loro versione file json.

#### Integrazione codice CNR

Per eseguire funzioni matlab, si può usare blocco `MathScript` di LabVIEW. Serve però aggiungere il path della cartella
con le funzioni: in un progetto, right-click in `My Computer>>Properties>>MathScript: Search Paths` e ho aggiunto la
cartella `Analyze\QKD analyze\matlab_functions`. Questo funziona per trovare le funzioni ma la working directory dello
script è comunque diversa e il `load` via path relativo non funziona se prima non si cambia cartella con `cd`.

In realtà per riuscire ad usare codice Matlab con matrici sparse è necessario utilizzare il `Matlab script node`, non il
generico MathScript. Per questo pare non funzionare l'aggiunta del path, si deve proprio cambiare la working directory a
quella che contiene funzioni e dati.

Alla fine è stato tutto tradotto in LabVIEW nativo, senza utilizzare nessuna funzione Matlab.

- [ ] Trasmissioni su canale pubblico criptate?

### QKD Manager

Questo processo riceve da QKD Analysis la chiave e la salva in un database SQLite locale, `key.db`.

**Table:** keys | Field | Type | Not NULL | Primary Key | Example | | ----- | ---- | ---- | ---- | ---- | | time |
BIGINT | No | Yes | 1234567891011 | | id | char(36)   | Yes | No | fd7a80b4-b98e-43cb-b860-53d44b4e296b | | key | char(
2048) | Yes | No | [bit chiavi espressi in bytes] |

Query usata per la creazione della tabella:

```sql
CREATE TABLE 'keys'
(
    'time'
    BIGINT
    PRIMARY
    KEY,
    'id'
    CHAR
(
    36
),
    'key' CHAR
(
    2048
) NOT NULL
    );
```

In ogni caso, alla connessione con il database, il codice LabVIEW verifica se il database contiene la tabella `keys` e,
in caso contrario, la crea.

Nel database la chiave, che è un array di 0 e 1 viene convertita in array di U8 (con larghezza pari a un ottavo quindi)e
poi convertita a stringa con la funzione nativa LabVIEW. La classe `QKD Manager SQLite.lvclass` si occupa della
conversione in scrittura nel database e anche della ricorversione quando viene letta una chiave dal database.

I metodi disponibili nella classe `QKD Manager SQLite.lvclass` sono:

- Open connection
- Add key. Aggiunge una riga alla tabella `keys`
- Get key by ID. Restituisce la chiave con ID richiesto, dove ID è parametro in ingresso di tipo stringa (36 char).
- Get keys. Restituisce N chiavi, dove N è parametro in ingresso di tipo U32.
- Flush keys. Cancella dalla tabella `keys` tutte le righe. Vengono anche fornite come output.
- Check time to live of keys. Viene verificata l'età delle chiavi presenti nel database e, quando maggiore del
  consentito, vengono eliminate.
- Delete key by ID. Elimina dal database una chiave specifica, indicata dal suo ID.
- Close connection.

In questo processo è implementato controllo in modo che, se non dovessero esserci sufficienti chiavi per soddisfare la
richiesta del client, allora le nuove chiavi appena ottenute vengono automaticamente trasmesse al client, appena queste
diventano disponibili. (*funzione attualmente disabilitata quando si chiede una singola chiave attraverso il
comando `get_key` delle API.*)

Il database e la libreria LabVIEW usata per accederci sono di tipo server-less. Non mi è quindi immediato implementare
forme di protezione dell'accesso ai dati in esso contenuti.

- [ ] Se chiave con ID non trovata deve essere mandato avviso al client che l'ha chiesta.
- [ ] Verificare comportamento quando client chiede altro blocco di chiavi mentre sto ancora aspettando di ottenere il
  numero di chiavi chiesto alla chiamata precedente.
- [ ] Se non vengono trovate abbastanza chiavi deve partire la misura vera e propria. E quando ho raggiunto il numero di
  chiavi richieste allora interrompere la misura.

### TCP Socket

Ogni partner contiene due client TCP Socket Server e un TCP Client. Uno dei server è usato per comunicazioni tra
partners e tra partner e ETSI client; il secondo è dedicato alle comunicazioni tra partner e LKMS, su richiesta di UPM.
I messaggi diretti verso l'altro partner vengono mandati tramite il proprio client verso il server del partner.

Il server è in grado di gestire multipli client contemporaneamente e a gestirne le richieste, in modo da rispondere al
client corretto.

![TCP Socket diagram](QKD_TCP_base_logic.png)

All'avvio della applicazione di un partner vengono automaticamente avviati i TCP servers; ogni server attende l'arrivo
di clients su porta indicata nella configurazione. Per esempio, Server_A ascolta sulla porta 6341.

Quando viene premuto il tasto <kbd>Connect</kbd> di un partner, il suo client prova a collegarsi al server dell'altro
partner, mettendono d'accordo su che porta utilizzare per le future comunicazione (porta diversa da quella usata dal
server per le nuove connessioni, la 6341 nel nostro esempio). In automatico il partner 2 attiva la connessione del
proprio client verso il server del primo partner.

*Nota:* in fase di sviluppo su stessa macchina i due attori sono entrambi su localhost e a differenziarli è il numero
della porta sulla quale i server ascoltano per nuovi client. Quando le macchine saranno diverse la porta sarà uguale e a
differenziare gli attori sarà l'IP.

Ogni volta che un client si collega ad un server viene memorizzata una reference a questa connessione. Periodicamente il
server controlla che uno dei client abbia mandato un messaggio; se il server trova un messaggio ed il messaggio richiede
il passaggio attraverso il processo Main (per esempio per il messaggio `Get Parameter`) allora il server confeziona un
cluster con:

- reference al client che ha fatto la richiesta
- stringa di testo JSON con il comando.

che viene mandato al processo Main. Il processo Main nota che nella coda c'è un nuovo elemento, lo scoda e interpreta il
messaggio stringa; quindi raccoglie il valore del parametro necessario, lo formatta in stringa e costruisce un cluster:

- reference al client che ha fatto la richiesta e che deve ricevere la risposta
- stringa di testo JSON con il valore del parametro (per esempio).

e viene mandato indietro al processo TCP, in modo che venga trasmesso al client indicato nel cluster.

- [ ] Gestione errori quando connessione tra partner cade.
- [ ] verificare come dimenticarsi di un client che si scollega, in modo da evitare di controllare continuamente se ha
  mandato un messaggio.

## API

Descrizione dei comandi che possono essere interpretati dai TCP Server dei partner.

Tutti i messaggi in ingresso sono di tipo json con seguente struttura:

```json
{
  "command": "set_parameter",
  "attribute": "lambda",
  "value": "1550"
}
```

eventualmente possono essere lasciati vuoti `attribute` o `value`, se non utilizzati (vedere i campi indicati come *
ignored* nella sezione API).

Esistono due categorie di richieste accettate. La prima è quella con i comandi che possono arrivare da client esterni.
La seconda è quella con i comandi tra partner.

Tutti i messaggi sono preceduti da una communicazione il cui contenuto è la lunghezza (4 bytes) del messaggio che verrà
trasmesso.

Per farlo è stato necessario modificare il codice Python inviato dagli spagnoli di UPM. In particolare
in `socketsSupport.py` la funzione `send_data_to_address` è diventata:

```python
def send_data_to_address(data_to_send, server_address, servertype="python"):
    try:
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.connect(server_address)
        main_socket.settimeout(1)

        if servertype == "labview":
            main_socket.sendall(struct.pack('>I', len(data_to_send)))
        main_socket.sendall(str(data_to_send).encode())

        if servertype == "python":
            buf = 512
        elif servertype == "labview":
            bufpack = main_socket.recv(4)
            buf = struct.unpack('>I', bufpack)[0]

        data = main_socket.recv(buf)
        data_deserialized = data.decode('utf8').replace("'", '"')
        received_data_from_device = json.loads(data_deserialized)
        print("[{}]".format(received_data_from_device))

        main_socket.close()
    except Exception as e:
        print("[ERROR WITH ADDRESS:\n{}]".format(e))
```

> **WARNING** va capito come proteggere questi comandi. Se è vero che quelli da client esterno sono solo tra entità in localhost e quindi, FORSE, da considerarsi sicure, invece non saranno sicure quelle tra partner.
>
> Al momento non ho modo di capire se è il partner o un malintenzionato a mandarmi messaggi.
>
> Inoltre, al momento, a livello LabVIEW non c'è nessuna reale differenza tra i due gruppi di comandi, per cui anche un partner potrebbe chiedere chiavi o eliminare tutte le chiavi. E quindi anche un malintenzionato potrebbe fare lo stesso!

**List of Attributes**

| Attribute | Get Attribute | Set Attribute | Type | Example | Description |
| ---- | ---- | ---- | ---- | ---- | ---- |
| wavelength    | :heavy_check_mark: | :heavy_multiplication_x:  | string `([1-9][0-9]{0,3})` | 20 | A WDM channel number |
| QBER          | :heavy_check_mark: | :heavy_multiplication_x: | double | |
| channel_att   | :heavy_check_mark: | :heavy_check_mark: | UINT8 | | Expected attenuation on the quantum channel (dB)|
| ttl           | :heavy_check_mark: | :heavy_check_mark: | UINT32 | | maximum time that a key could be kept in the key store |
| samples       | :heavy_check_mark: | :heavy_check_mark: | UINT16 | | Number of bits for each Sifted QKEY |

### ETSI client messages

#### Get Attribute

Sent by the client to get the actual value of a specific attribute.

| Field | Value |
| ---- | ---- |
| command | `get_attribute` |
| attribute | see table |
| value | *ignored* |

*Reply:* `{"status":"Successful","value":"1234"}` | `{"status": "ERROR", "message":"Invalid name"}`

*Recipient:* Transmitter | Receiver

*Note:* A list of valid attributes and respective values will be provided. I parametri per cui è possibile chiedere il
valore non sono tutti quelli presenti nel cluster `Settings.ctl` ma solo quelli che si deciderà di mettere all'interno
della functional global variable `FGV Settings for clients.vi`.

#### Set Attribute

Sent by a client to set the value of a specific attribute of the recipient. The new value will be automatically sent to
the other recipient.

| Field | Value |
| ---- | ---- |
| command | `set_attribute` |
| attribute | see table |
| value | see table |

*Reply:* `{"status": "Successful"} | {"status": "ERROR", "message":"Invalid name or value"}`

*Recipient:* Transmitter | Receiver

*Note:* A list of valid attributes and respective values will be provided. I parametri per cui è possibile impostare il
valore non sono tutti quelli presenti nel cluster `Settings.ctl` ma solo quelli che si deciderà di mettere all'interno
della functional global variable `FGV Settings for clients.vi`.

### LKMS client messages

#### get_key

Sent by a client to obtain a key segment.

| Field | Value |
| ---- | ---- |
| command | `get_key` |
| attribute | *ignored* |
| value | *ignored* |

*Reply:* If a key with the required ID is found, the reply is a json:

```json
    {
  "time": 1234567891011,
  "ID": "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
  "Key": [
    36,
    39,
    75,
    136,
    254,
    145,
    133,
    ...,
    234,
    25,
    193,
    42,
    172
  ]
}
```

If a key is not found, the reply will be an empty json with the same structure.

#### Get key by ID

Sent by a client to obtain a specific key, identified by the `ID` field. `ID` must be a string rapresentation of an U64
number.

| Field | Value |
| ---- | ---- |
| command | `Get key by ID` |
| attribute | *ignored* |
| value | `fd7a80b4-b98e-43cb-b860-53d44b4e296b` |

*Reply:* If a key with the required ID is found, the reply is a json with array of keys (the size of the array will be
one), keeping the same json structure of the `Get keys` reply.

```json
{
[
  {
    "time": 1234567891011,
    "ID": "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
    "Key": [
      36,
      39,
      75,
      136,
      254,
      145,
      133,
      ...,
      234,
      25,
      193,
      42,
      172
    ]
  }
]
}
```

If a key with that ID is not found, an error message is returned (TO BE IMPLEMENTED).

*Recipient:* Transmitter | Receiver

#### Get keys

Sent by a client to obtain `N` keys. The desired number `N` can be specified in the `value` field; `value` must be a
string rapresentation of an U32 number.

| Field | Value |
| ---- | ---- |
| command | `Get keys` |
| attribute | *ignored* |
| value | "N" |

*Reply:* The reply will be a json string with the array of keys.

```json
{
[
  {
    "time": 1234567891011,
    "ID": "fd7a80b4-b98e-43cb-b860-53d44b4e296b",
    "Key": [
      36,
      39,
      75,
      136,
      254,
      145,
      133,
      ...,
      234,
      25,
      193,
      42,
      172
    ]
  },
  {
    "time": 1234567891525,
    "ID": "1ac7b85a-4cc9-4fe7-a119-188e0af8cdfc",
    "Key": [
      36,
      39,
      75,
      136,
      254,
      145,
      133,
      ...,
      234,
      25,
      193,
      42,
      172
    ]
  }
]
}
```

*Recipient:* Transmitter | Receiver

*Note:* If the available key in the database are fewer than the required `N`, the first reply will contains all the
available; future keys will be sent automatically when available until the number `N` is reached.

#### Flush keys

Delete all the available keys in the local database.

| Field | Value |
| ---- | ---- |
| command | `Flush keys` |
| attribute | *ignored* |
| value | *ignored* |

*Reply:* to be implemented. A simple PASS/FAIL or the json array with all the removed keys.

*Recipient:* Transmitter | Receiver

#### Delete by IDs

Delete keys with the specified IDs, for example the ones that are older than the `time to live`.

| Field | Value |
| ---- | ---- |
| command | `Delete by IDs` |
| attribute | *ignored* |
| value | array of IDs (string) |

*Reply:*  `{"command":"Keys deleted", "parameter": "", "value": "Done"}`

*Recipient:* Receiver

### HW Layer messages

todo

### Sifted Key reconstruction messages

#### Start

Usato da Trasmettitore per indicare al Ricevitore l'inizio di una trasmissione. Contiene l'ID della chiave che verrà
generata.

| Field | Value |
| ---- | ---- |
| command | `start` |
| attribute | *ignored* |
| value | {"ID": ID} |

*Destinatario:* Ricevitore

*Note:* In fase di sviluppo, quando l'hardware è simulato, viene trasmesso anche l'array con i qbit selezionati dal
trasmettitore.

#### Confronto basi

Trasmesso da Ricevitore, contiene quanto serve per selezionare la parte valida.

| Field | Value |
| ---- | ---- |
| command | `Confronto basi` |
| attribute | *ignored* |
| value | {"ID": ID, "index": [i32], "basi": [0 3 2 0 1 .. 3]} |

*Destinatario:* Trasmettitore

#### Sifted key

| Field | Value |
| ---- | ---- |
| command | `Sifted key` |
| attribute | *ignored* |
| value | {"ID": ID, "confronto": [0 0 1 0 1 .. 1]} |

*Destinatario:* Ricevitore

#### Calc BER

Contiene un subset dell'array, da utilizzare per il calcolo del BER. Questo subset viene rimosso in modo che non venga
utilizzato per la costruzione della chiave.

| Field | Value |
| ---- | ---- |
| command | `Sifted key` |
| attribute | *ignored* |
| value | {"ID": ID, "index": [i32], "value": [0 1 1 0 1 .. 0]} |

*Destinatario:* Trasmettitore

#### Valid Key

Se il BER risulta inferiore a valore di soglia allora la chiave è considerata valida.

| Field | Value |
| ---- | ---- |
| command | `Valid key` |
| attribute | *ignored* |
| value | {"ID": ID, "BER": dbl} |

*Destinatario:* Ricevitore

#### Discard Key

Se il BER risulta superiore a valore di soglia allora la chiave è scartata.

| Field | Value |
| ---- | ---- |
| command | `Discard key` |
| attribute | *ignored* |
| value | {"ID": ID, "BER": dbl} |

*Destinatario:* Ricevitore

### Cascade process messages

todo
