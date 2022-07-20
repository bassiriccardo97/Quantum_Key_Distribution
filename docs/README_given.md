# QSN-d-1 - Manuale di utilizzo

Il presente manuale fornisce le istruzioni operative che consentono l'utilizzo del QSN-d-1 product.

Per una documentazione più dettagliata su tutti i messaggi TCP scambiati tra trasmettitore e ricevitore o le API esposte
a client esterni, fare riferimento al seguente [file](transmitter/data/API_documentation.md).

- [QSN-d-1 - Manuale di utilizzo](#qsn-d-1---manuale-di-utilizzo)
    - [Requisiti](#requisiti)
    - [Collegamenti hardware](#collegamenti-hardware)
        - [Trasmettitore](#trasmettitore)
        - [Ricevitore](#ricevitore)
    - [Programmi disponibili](#programmi-disponibili)
    - [Application manager](#application-manager)
        - [Funzioni di autostart](#funzioni-di-autostart)
    - [Programmi per calibrazione](#programmi-per-calibrazione)
        - [Settings](#settings)
        - [Find delay](#find-delay)
        - [Novoptel calibration](#novoptel-calibration)
        - [Manual alignment](#manual-alignment)
        - [Conclusione](#conclusione)
    - [Programmi Main](#programmi-main)
        - [Esecuzione e parametri](#esecuzione-e-parametri)
        - [Utilizzo](#utilizzo)
            - [Settings](#settings-1)
        - [Logging](#logging)
        - [Files di configurazione](#files-di-configurazione)
            - [Settings.xml](#settingsxml)
            - [config.json](#configjson)
            - [SPAD Settings.xml](#spad-settingsxml)
            - [VOA Settings.json](#voa-settingsjson)
    - [Key Management System](#key-management-system)
        - [Introduzione](#introduzione)
        - [Attivazione della macchina virtuale](#attivazione-della-macchina-virtuale)
        - [Configurazione dell'host](#configurazione-dellhost)
        - [Configurazione del Key Manager](#configurazione-del-key-manager)
        - [Dialogo Applicazione-Key Manager](#dialogo-applicazione-key-manager)
        - [Trace logs](#trace-logs)

![loghi_poli_cohaerentia](img/poli_coh.png)

## Requisiti

LabVIEW 2020 32bit Runtime: <https://www.ni.com/it-it/support/downloads/software-products/download.labview.html#353197>.
Inoltre è necessario installare i driver DAQmx per la stessa versione di
LabVIEW: <https://www.ni.com/it-it/support/downloads/drivers/download.ni-daqmx.html#348669>
e la runtime del toolkit Multicore Analysis and Sparse Matrix
Toolkit: <https://www.ni.com/gate/gb/GB_EVALTLKTLVMULTICORE/US>

Driver FTDI D2xx: <https://ftdichip.com/drivers/d2xx-drivers/> ma nel dubbio installare il kit dello SPAD.

Unico sistema operativo sul quale i programmi sono stati testati: Windows 10 Professional 64-bit.

## Collegamenti hardware

### Trasmettitore

![Frontale-Trasmettitore](img/Frontale-Transmitter.PNG)

Oltra all'alimentazione 220V da collegarsi sul retro della scatola trasmettitore, è sufficiente collegare una fibra con
connettore FC/APC alla porta `Fiber Out` del frontale.

Infine, è necessario collegare un cavo ethernet al frontale. Sono presenti porte USB per collegamento di mouse e
tastiera e una porta HDMI per il segnale video.

Non è fornita la bretelle di fibra ottica per collegare il trasmettitore alla rete in fibra ottica.

### Ricevitore

Il ricevitore è composto da:

- Scatola rack 3RU. Alimentata da 220V attraverso porta posteriore
- Ricevitore SPAD e suo alimentatore esterno
- Fotodido e suo alimentatore esterno
- Filtro WDM

Sono inoltre forniti i seguenti cavi:

- 1 cavo USB
- 3 cavi SMA
- Una bretella fibra ottica FC/APC - FC/APC, da frontale a fotodiodo
- 1 cavo di alimentazione per il fotodiodo esterno

Non è fornita la bretelle di fibra ottica per collegare il ricevitore alla rete in fibra ottica.

![Frontale-Ricevitore](img/Frontale-Receiver.PNG)

La fibra ottica della tratta deve essere collegata al filtro WDM. L'uscita del filtro WDM alla porta `Fiber In` sul
frontale della scatola rack.

Due cavi SMA devono essere collegati tra scatola rack e SPAD, utilizzando i due cavi SMA forniti:

- `Trigger In` dello SPAD a porta `Trigger Out` della scatola rack
- `TTL AUX Output` dello SPAD a porta `TTL AUX IN`

Un cavo UBS deve essere collegato tra SPAD e frontale, utilizzando la porta USB `SPAD USB`. Una bretella ottica con
connettori FC/APC deve essere collegata tra ingresso ottico dello SPAD e `Fiber Out` della sezione SPAD.

Il fotodiodo deve essere alimentato utilizzando cavo fornito e etichettato. Inoltre una fibra ottica con connettore
FC/APC collegata a porta `Fiber out` del frontale e connettore FC/APC all'ingresso ottico del fotodiodo. Infine un cavo
SMA deve essere collegato tra la porta SMA del fotodiodo e la porta `RF IN` del frontale.

Infine, è necessario collegare un cavo ethernet al frontale. Sono presenti porte USB per collegamento di mouse e
tastiera e una porta HDMI per il segnale video.

## Programmi disponibili

Sia per trasmettitore che ricevitore esistono tre distinti eseguibili:

1. Application manager.
2. Calibration.
3. Main. Presenti nelle cartelle `receiver` e `transmitter`.

In aggiunta, è disponibile `Config file manager` per la modifica, attraverso una interfaccia grafica, dei
files `config.json` presenti nelle sottocartelle `Data` di tutti gli eseguibili elencati sopra.

Tutti i programmi, per funzionare correttamente, necessitano di conoscere l'indirizzo IP dell'altro elemento del nodo e
le porte sulle quali sono aperti i vari TCP Server necessari per il loro corretto funzionamento.

Per questo, il primo passo per una corretta configurazione è individuare gli IP di trasmettitore e ricevitore e
utilizzare l'eseguibile in `Config file manager`. Oltre agli IP, in questo momento sarà possibile configurare le porte
utilizzate, scegliendo due porte che saranno configurate in modo da essere raggiungibili dall'esterno.

Dopo aver indicato i valori desiderati, premere `Save`. Questa operazione deve essere effettuata sia sul device
trasmettitore che su quello ricevitore.

Oltre alle due indicate, un ulteriore TCP server sulla porta 6666 verrà aperto lato trasmettitore.

## Application manager

L'application manager del trasmettitore è configurato in modo da avviarsi automaticamente. L'application manager del
ricevitore può essere configurato in modo da poter avviarsi automaticamente. Una scorciatoia al rispettivo application
manager è presente sul desktop dei devices.

La funzione di questi due eseguibili è quella di poter facilmente avviare gli altri eseguibili Calibrazione e Main,
senza permetterne l'esecuzione contemporanea e, in particolare, permettere l'apertura anche dei programmi lato
trasmettitore avendo accesso al pc del solo ricevitore.

![GUI Application Manager di trasmettitore e ricevitore](img/AppManager.png)

All'avvio della versione ricevitore, verrà tentata la connessione con il ricevitore, utilizzando l'indirizzo IP indicato
nel file `config.json`. In caso di insuccesso è possibile indicare un differente IP e ritentare. Quando la connessione
andrà a buon fine l'indicatore diventerà verde.

A questo punto è possibile lanciare l'applicazione per la calibrazione o l'applicazione per il programma principale. La
stessa applicazione verrà automaticamente avviata anche al trasmettitore.

Se una delle applicazione dovesse essere ancora in esecuzione, non sarà possibile lanciare nessuna nuova applicazione.

### Funzioni di autostart

Entrambi gli application manager possono essere configurati per avviarsi automaticamente al boot del sistema operativo.
Questo è ottenuto attraverso il singolo controllo `Autostart` per il trasmettitore e attraverso `Autostart Manager` al
ricevitore.

Inoltre, al ricevitore, è possibile impostare l'autostart dell'applicativo principale, attraverso
controllo `Autostart Main`. Una volta verificata la connessione tra partner allora la generazione della chiave inizierà
automaticamente.

## Programmi per calibrazione

Questi programmi guidano la configurazione e calibrazione del sistema, al fine di massimizzarne le prestazioni e la
sicurezza.

Il programma lato trasmettitore riceve istruzioni da quello del ricevitore, quindi è ancora sufficiente avere accesso
diretto al solo nodo del ricevitore. Da ora in poi si farà riferimento solo a quest'ultima.

Sono presenti quattro differenti schede, con l'intento di guidare passo passo durante la configurazione e calibrazione.

### Settings

In questa scheda è possibile indicare i device name di trasmettitore e ricevitore, le COM dei due laser presenti,
insieme a molti altri parametri della coppia trasmettitore e ricevitore. In generale, tutti questi valori sono da
considerarsi già ottimizzati per cui se ne sconsiglia la modifica se non da parte di persone qualificate.

![Calibration settings](img/Calibration-Settings.PNG)

### Find delay

Questa attività può essere utilizzata per individuare il miglior ritardo tra segnale di clock e momento in cui abilitare
il gate del ricevitore SPAD. Grazie alla presenza nel trasmettitore del recovery clock da Novoptel, questo valore non
dipende più dalla lunghezza di propagazione in fibra. Anche in questo caso quindi il valore indicato è da considerasi
già ottimizzato e raramente sarà necessaria una modifica.

![Calibration delay](img/Calibration-Delay.PNG)

Nella immagine viene riportato un esempio di misura completa e si indica, con freccia rossa, il valore dell'asse x da
indicare nel controllo `Delay(s)` in `Receiver settings` nella prima tab.

### Novoptel calibration

Procedura necessaria ad allineare gli assi di polarizzazione del dispositivo Novoptel presente nel ricevitore. La
procedura è automatizzata in quasi tutti gli step, con l'eccezione dello step 6, che è anche l'ultimo.

![Calibration Novoptel](img/Calibration-Novoptel.PNG)

Dopo aver premuto `Start` la procedurà inzia con lo Step 2 (lo step 1 dura così poco che non sarà possibile notarlo);
per passare al passo successivo premere il tasto `Next`. Ad ogni step la descrizione verrà aggiornata e verrà indicato
il valore `Feedback` che deve tendere ad assumere prima di poter passare allo step successivo.

> Se durante lo step 5 il segnale non dovesse raggiungere i 28000 previsti, interrompere la procedura, tornare alla schermata settings e incrementare il valore `AUX bias (mA)` di 5 mA. Tornare alla schermata `Novoptel calibration` e ricominciare con la procedura.

Lo step 6 potrebbe richiedere la regolazione manuale di una delle tre lamine per il controllo di polarizzazione,
presenti all'interno del ricevitorem in particolare quella indicata da riquadro azzurro nella seguente immagine.

![botola](img/botola.png)

Si dovrà regolarla in modo da minimizzare il valore di `Feedback`; valori inferiori a 1000 sono da considerarsi
sufficienti e si potrà quindi concludere questa fase di calibrazione, premendo `Stop`.

### Manual alignment

Quest'ultimo step richiederà l'allineamento manuale della polarizzazione al ricevitore e, per farlo, sarà necessario
utilizzare i due controllori di polarizzazione neri all'interno della scatola ricevitore. In particolare, i due
controllori da utilizzare sono quelli indicati dal riquadro arancione della precedente immagine.

Una volta premuto `Start` si vedranno due impulsi nel grafico. A questo punto sarà necessario alternare tra 90° e 135°
mentre si cerca di minimizzare l'ampiezza dei due impulsi:

Quando è selezionato 90° si deve cercare di muovere i due controllori di polarizzazione in modo da minimizzare
l'ampiezza del primo impulso.

![Calibration manual - 90 degrees](img/Calibration-Manual-90.PNG)

Quando è selezionato 135° si deve cercare di minimizzare l'ampiezza del secondo

![Calibration manual - 135 degrees](img/Calibration-Manual-135.PNG)

Attenzione che dopo aver minimizzato l'ampiezza del primo impulso e poi del secondo, sarà necessario tornare a 90° per
verificare che l'ampiezza del primo sia ancora vicino a zero. Sarà necessario passare parecchie volte a 90° e 135° fino
a quando non si sarà trovato un punto per il quale entrambi gli impulsi sono minimizzati se osservati al corretto
angolo.

### Conclusione

Completati i passi appena descritti si deve tornare alla schermata iniziale `Settings`, attraverso la quale sarà
possibile salvare i parametri trovati, in modo che i programmi principali ne facciano uso quando verranno avviate. In
automatico i programmi di calibrazione aggiorneranno i file di settings presenti nelle sottocartelle `Data` delle
rispettive main applications.

## Programmi Main

Presenti nelle cartelle `receiver` e `transmitter`. Sono i due eseguibili che permettono la effettiva creazione di
chiavi.

![GUI Main Transmitter](img/Transmitter_Main.png)
![GUI Main Transmitter](img/Receiver_Main.png)

### Esecuzione e parametri

Per lanciare in modalità simulazione è sufficiente eseguire il file `run simulazione.bat`, che esegue i due programmi
principali (trasmettitore e ricevitore) in modalità simulazione, con cascade abilitato, e i due client (lkms e etsi) che
emulano quanto realizzato da UPM.

Per eseguire nella normale modalità con hardware vero collegato è sufficiente eseguire il file `run hardware.bat`.

Sono disponibili vari parametri per l'esecuzione degli eseguibili del trasmettitore e ricevitore. Sono elencati nella
seguente tabella:

| Parametro | Valori | Target | Descrizione |
|----|----|----|----|
| **mode** |  "", "daq", "hw", "ni", Default | Entrambi | Se l'hw è collegato e composto da schede NI.|
||  "s", "sim", "simulate" || Se si vuole utilizzare in modalità simulazione, nella quale il conteggio fotoni è simulato da generazione casuale.|
| **
cascade** |  "", "true", "y", "yes", Default | Entrambi | Viene abilitata la parte di analisi relativa a Cascade e Privacy Amplification.|
||  "f", "false", "n", "no" || Non si effettuano cascade e privacy amplification, fermandosi alla Sifted Key. Le chiavi non saranno error free ma potrebbe essere utile in fase di debug.|
| **
spad** |  "hardware", "hw", "mpd", "real" | Ricevitore | Lo spad della MDP è controllato direttamente dal software LabVIEW.|
||  "ext", "external", "sim", Default  || Si suppone che lo SPAD venga controllato attraverso software esterno di terze parti. |
| **
ttl** | t, true, y, yes, Default | Transmettitore | Viene abilitato il controllo del tempo di vita delle chiavi conservate nei database locali. |
|| f, false, n, no || Il controllo è disabilitato, garantendo vita infinita alla chiavi nei database |

Alcuni esempi per lanciare una specifica versione:

```bash
Transmitter.exe
Transmitter.exe --mode:daq
Transmitter.exe --mode:sim --cascade:true --ttl:false
Receiver.exe --mode:ni --cascade:true --spad:mpd
```

E' possibile creare un collegamento ad ognuna delle versioni. Una volta creato un collegamento a `Transmitter.exe`,
rinominarlo a piacere e poi, tra le proprietà modificare la voce "Destinazione", aggiungendo i parametri come
desiderato.

### Utilizzo

Dopo aver avviato i due eseguibili `Transmitter.exe` e `Receiver.exe`, è necessario collegare attraverso il canale
pubblico TCP i due partner: è sufficiente premere il tast `Connect` presente in entrambe le UI dei programmi.Se la
connessione andrà a buon fine, il led di fianco a questo pulsante diventerà verde, su entrambe le UI.

![Connect](img/Connection_Success.PNG)

Se anche uno solo di questi led dovesse rimanere rosso allora la connessione non è andata a buon fine; chiudere quindi i
programmi e verificare se gli indirizzi IP indicati in `config.json` sono corretti.

Nella UI del ricevitore sono presenti gli indicatori di stato dello SPAD. Si consiglia di iniziare il processo di
generazione di chiavi solo quando tutti gli indicatori sono verdi. Di fianco a questi indicatori è inoltre presente un
tasto per visualizzare e modificare le impostazioni dello SPAD. Tuttavia si sconsiglia di modificare questi valori, in
quando già ottimizzati durante la fase di test.

Se la connessione viene instaurata con successo allora è possibile iniziare la procedura di generazione della chiave
premendo `Start`, presente in entrambe le UI. Per interrompere, in qualunque momento, premere `Stop`, anche questo
presente in entrambe le UI.

> **Attenzione**: la procedura si fermerà all'istante senza completare la procedura di trasmissione/ricezione della chiave in corso e scartando quindi le informazioni raccolte fino a quel momento e che non sono già state utilizzate per la creazione di una chiave.

Durante la generazione delle chiavi, le due barre di progresso presenti nelle due UI vengono aggiornate e rappresentano
una stima del tempo rimanente alla creazione della nuova chiave. La barra di progresso nel Trasmettitore viene
aggiornata molto meno frequentemente di quella presente nel Ricevitore, per evitare di scambiare troppi messaggi su
canale pubblico.

Sono inoltre indicati:

- **target # photons**: indica il numero di fotoni che devono essere acquisiti prima di poter creare una chiave della
  dimensione richiesta (attraverso parametro `block size` in Settings.)
- **total # photons**: numero di fotoni attualmente ricevuti, da confrontarsi con quelli target da ricevere.
- **QBER**: stima del QBER ottenuto durante la creazione dell'ultima chiave. Se il QBER misurato risulta maggiore di
  0.11 allora i dati vengono scartati poiché non può essere garantito il corretto recupero degli errori e quindi non può
  essere garantita l'uguaglianza delle chiavi elaborate al trasmettitore e al ricevitore.
- **Valid QBITs**: numero di QBit validi misurati durante ultimo processo, ovvero numero di gates duranti i quali è
  stato conteggiato un fotone e la base al trasmettitore è uguale a quella al ricevitore.
- Dopo la procedura di recupero dell'errore, le due chiavi vengono confrontate tramite CRC e se il check non dovesse
  essere superato la chiave viene scartata.
- **Key length**:Lunghezza (in bits) della chiave dopo l'intera procedura di generazione.

Nelle UI dei programmi è presente indicatore `# of keys available` che indica il numero di blocchi di chiave disponibili
in quel momento e che sono conservate all'interno dei database locali, uno per partner.

In un qualunque momento, anche a generazione in corso, è possibile premere `Flush keys` e scartare tutte le chiavi
create e memorizzare all'interno dei due database. Tuttavia, si sconsiglia di farlo se è connesso un client esterno che
potrebbe chiedere una nuova chiave ai partner.

#### Settings

Tramite tasto Settings è possibile modificare alcuni dei parametri di funzionamento; il tasto è presente in entrambe le
UI di Trasmettitore e Ricevitore ed è disabilitato se la trasmissione è in corso; per poterlo abilitare è necessario
fermare la trasmissione. La modifica dei Settings di uno dei due partner viene automaticamente propagata all'altro
partner attraverso messaggio TCP su canale pubblico.

![Settings Main Application](img/Settings.png)

In particolare, i parametri a disposizione sono:

- Block size: indica la lunghezza (in bit) che dovrà avere la sifted key prima di essere elaborata dalla parte di codice
  del cascade per l'error recovery. Questo numero deve essere una potenza di 2.
- Samples: la trasmissione/acquisizione continuerà fino a quando non si sarà raggiunto un numero di fotoni letti tale da
  garantire la block size richiesta. Una singola trasmissione/ricezione consiste però di "Samples" qbits trasmessi alla
  volta. Quando i programmi sono in modalità simulazione è consigliato un valore pari a 3000; quando in modalità
  hardware, si consiglia di lavorare con blocchi di 102000 qbit.
- Delta attenuazione (dB). Il sistema è dimensionato in modo da avere una potenza ottica in uscita dal trasmettitore
  tale da avere 0.1 fotoni per gate. E' tuttavia possibile andare a modificare questo valore di potenza variando
  l'attenuazione introdotta dall'attenuatore ottico variabile presente nel trasmettitore. Aumentando questo valore, la
  potenza ottica trasmessa diminuirà di conseguenza e il tempo necessario a produrre una chiave aumenterà.
- BER size: la percentuale di bits della sifted key usati per la stima del QBER durante la trasmissione. Questi bits
  devono poi essere scartati perché trasmessi su canale pubblico quindi si sconsiglia di aumentare questa percentuale,
  nonostante questo porti ad una stima più precisa.
- Logging: si può decidere cosa salvare (niente, solo la chiave, modalità di debug) e indicare una cartella e un nome
  comune. Al nome verrà appeso il timestamp e altre tag per identificare trasmettitore, ricevitore, sifted key e
  cascade.
- Time to live (s): una chiave presente nel database locale viene eliminata se creata da più di "time to live" secondi.

Inoltre è stato aggiunto un parametro per artificiosamente rallentare la generazione delle chiavi in modalità simulata.
Questo parametro è impostabile solo attraverso una modifica diretta dei files di settings, cambiando il numero alla riga
114 di questi files.

```xml
<Name>SimPause_ms</Name>
<Val>5000</Val>
```

La pausa è espressa in millisecondi e deve essere un numero intero positivo (uint32). Ricordarsi di modificare il numero
in entrambi i files di settings, sia per trasmettitore che per ricevitore. Il numero verrà letto solo in fase di avvio
degli eseguibili quindi, per modificarlo, è necessario riavviare gli eseguibili.

### Logging

E' possibile abilitare il logging su file di testo delle chiavi generate. Per farlo è sufficiente selezionare la
voce `Key` in `What to log` nel pannello di Settings. In questo caso vengono generati due files al Trasmettitore e due
al ricevitore:

- \<timestamp\>_\<filename\>_Cascade_Transmitter_Key.json
- \<timestamp\>_\<filename\>_Sifted_Transmitter_Key.json
- \<timestamp\>_\<filename\>_Cascade_Receiver_Key.json
- \<timestamp\>_\<filename\>_Sifted_Receiver_Key.json

```json
{
    "time":U64 from epoch,
    "id":UUID string,
    "Role":"transmitter"/"receiver",
    "Key":[array of bytes]
}
```

Un'altra opzione è selezionare `Debug` in `What to log`. Questa scelta produce i seguenti files:

- \<timestamp\>_\<filename\>_Cascade_Transmitter_Debug.json
- \<timestamp\>_\<filename\>_Sifted_Transmitter_Debug
- \<timestamp\>_\<filename\>_Cascade_Receiver_Debug.json
- \<timestamp\>_\<filename\>_Sifted_Receiver_Debug.json

con molte più informazioni, rendendo i files parecchio più grandi, in particolare quelli `Sifted`. Si sconsiglia di
selezionare questa opzione durante il normale utilizzo.

Cartella di destinazione e filename sono impostabili nel pannello `Settings` con il controllo `Log Relative File Path`.
Il percorso che si va ad indicare è relativo e la cartella di partenza dove è `"\<user>\Documents\QKD_log"`. Per
esempio, se viene scritto `Folder1\subfolder\prova.json` allora il path completo di uno dei file di log sarà:

```batch
\<user>\Documents\Folder1\subfolder\<timestamp\>_prova_Sifted_Transmitter_Key.json
```

Infine, nelle cartella `Data` di entrambi gli eseguibili, sono presenti `Log Transmitter.txt` e `Log Receiver.txt` dove
vengono registrati tutti gli eventi dei rispettivi eseguibili, compresi eventuali errori.

### Files di configurazione

Sono presenti diversi files di configurazione che vengono letti dagli eseguibili in fase di avvio. Sono tutti nella
cartella `data` del rispettivo eseguibile.

Il trasmettitore ha i seguenti files:

- Settings.xml
- VOA Settings.xml
- config.json

Per quanto riguarda il ricevitore:

- Settings.xml
- SPAD Settings.xml
- config.json

#### Settings.xml

Questo file contiene tutte le impostazioni delle schede di acquisizione e dei segnali elettrici di controllo e i device
names della scheda di acquisizione presente nel trasmettiore e nel ricevitore. Generalmente si sconsiglia di modificare
questi valori, in quanto già ottimizzati in fase di test.

Sono presenti inoltre altri parametri che l'utente può generalmente modificare attraverso interfaccia degli eseguibili.

#### config.json

Questo file contiene indirizzi IP e porte a cui contattare il web server del partner e le porte dei propri web servers
ai quali possono collegarsi partner e client terzi (come LKMS e ETSI).

```json
{
    "servers": {
        "main": {
            "port": 6342
        },
        "lkms": {
            "port": 6352
        }
    },
    "partner": {
        "address": "1.2.3.4",
        "port": 6341
    }
}
```

In questo esempio, il server per partner e ETSI risponde alla porta 6342; il server per il client LKMS alla porta 6352.
Invece il partner può essere contattato all'indirizzo `1.2.3.4:6341`.

In fase di configurazione è quindi necessario individuare gli indirizzi IP a cui risultano raggiungibili sia il
trasmettitore che il ricevitore e modificare opportunamente i files `config.json` presenti nella cartella `data` di
entrambi gli eseguibili.

#### SPAD Settings.xml

Contiene le impostazioni che verranno utilizzate in fase di inizializzazione dello SPAD. Si sconsiglia la modifica di
questi valori in quanto ottimizzati in fase di test.

#### VOA Settings.json

Contiene la curva di calibrazione dell'attenuatore ottico variabile presente nel trasmettitore e viene utilizzata per
identificare il corretto valore di tensione da fornire al dispositivo data una certa attenuazione desiderata. Si
sconsiglia la modifica di questi valori in quanto ottimizzati in fase di test.

## Key Management System

![logo_italtel](img/italtel.png)

QKD System e Key Management System devono essere attivati seguendo i passi descritti nel seguito.

### Introduzione

L'implementazione del Key Manager realizza quanto previsto dai documenti di riferimento (specifiche ETSI, documenti
funzionali) e in particolare:

- effettua l'integrazione con il QKD device corrispondente
- definisce le politiche di gestione delle chiavi simmetriche fornite dal QKD device
- effettua l'integrazione delle applicazioni attraverso una specifica interfaccia applicativa

In questa realizzazione del QSN-d-1 product la funzione del Key Manager pur essendone logicamente distinta risulta
essere integrata nel QKD device.

KMS si compone di un'immagine di una macchina virtuale (`KM-QKD`) composta nel modo seguente:

- sistema operativo Ubuntu 20.04.1 LTS
- software della funzionalità Key Manager
- script per la configurazione dell'host e dell'inserimento in rete
- script per la configurazione del Key Manager.

L'immagine della macchina virtuale deve essere configurata nella modalità multi-host, ovvero due macchine virtuali
distinte per i nodi tx (Alice) e rx (Bob)

### Attivazione della macchina virtuale

L'attivazione della macchina virtuale relativa all'immagine `KM-QKD` comporta l'utilizzo di Oracle VM VirtualBox. Al
completamento dell'avvio della macchina virtuale si può accedere tramite console con le seguenti credenziali:

```bash
qkdkm login:    qkd
Password:       quantum2020
```

### Configurazione dell'host

La configurazione dell'host comporta:

- indicazione dell'hostname
- configurazione dell'interfaccia di rete (enp0s3). E' possibile scegliere fra le seguenti due alternative

    - abilitare il DHCP
    - disabilitare il DHCP, dichiarare l'indirizzo IP con la notazione CIDR (es. 192.168.1.101/24), indicare il
      gateway (es. 192.168.1.1)

E' necessario accedere con le credenziali di root ed eseguire lo script "cfg_net.sh". Al termine il sistema verrà
restartato per attualizzare le scelte effettuate.

```bash
qkd@qkdkm:~$ sudo ./cfg_net.sh
[sudo] password for qkd: quantum2020
```

### Configurazione del Key Manager

La configurazione del QKD Management Layer comporta la configurazione di due QKD node (Alice e Bob) mediante la
ripetizione della medesima procedura sulle due machine virtuali (modalità multi-host).

> La procedura va eseguita prima per il QKD node 'X' (Alice) e successivamente per il QKD node 'Y' (Bob).**

La procedura comporta:

- indicazione del tipo di nodo (X, Y)
- azione che si vuole compiere

    - configuration
    - start-up
    - shutdown

Per l'azione di Node configuration occorre indicare:

- Node IP address (Alice/Bob)
    - indirizzo dell'host
- Remote node IP address (Bob/Alice)
    - indirizzo dell'host remoto
- configurazione del QKD device; occorre scegliere l'integrazione del QKD device rispetto all'emulazione del dialogo con
  il QKD device medesimo. Più in dettaglio occorre indicare le informazioni utilizzate nella procedura relativa alla
  configurazione del "QKD System"

    - indirizzo del QKD device
    - porta LKMS del QKD device
    - porta SDN del QKD device

E' necessario accedere con le credenziali di utente (qkd) ed eseguire lo script "cfg_node.sh".

```bash
qkd@hostname:~$ ./cfg_node.sh
```

L'output dell'esecuzione del QKD node viene memorizzato in `/home/qkd/sw_impl/qkd_itl` nei files

- contr.log, node_x.log per il nodo X (Alice)
- node_y_log per il nodo Y (Bob)

### Dialogo Applicazione-Key Manager

In questo paragrafo si riportano i dati di configurazione che devono essere utilizzati dalle applicazioni per dialogare
con il KMS.

Il dialogo tra applicazione e QKD Management Layer utilizza la API specificata nel documento "Application-Italtel QKD
itf v01.00".

Il dialogo si svolge con uno schema client-server,nel quale il KMS svolge il ruolo server.

**Numero di porta.**

- Nel nodo X (Alice), l'applicazione deve utilizzare la porta 24030.
- Nel nodo Y (Bob), l'applicazione deve utilizzare la porta 24031.

**Node_id**

- QKD node X (Alice): "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
- QKD node Y (Bob): "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

### Trace logs

L'output dell'esecuzione del QKD node viene memorizzato in `/home/qkd/sw_impl/qkd_itl` nei file:

- contr.log: controller nel nodo X (Alice)
- node_x.log: Key Manager nel nodo X (Alice)
- node_y.log: Key Manager nel nodo Y (Bob)

Elementi informativi rilevanti scritti nei log:

- **node_id** dei QKD node (contr.log, node_x.log, node_y.log) a cui devono essere associate le Applicazioni con i loro
  identificativi

    - QKD node x (Alice) "node_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    - QKD node y (Bob) "node_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

- **key package** cioè le chiavi simmetriche messe a disposizione dai QKD node (node_x.log, node_y.log)
- **ksid generated** (contr.log) ovvero il "key_stream_id" richiesto dai due lati della stessa applicazione
  all'esecuzione delle relative "OPEN_CONNECT" e passato come parametro delle altre funzioni.
