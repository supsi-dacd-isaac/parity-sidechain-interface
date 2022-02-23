# PM (Parity market) application:

## Sidechain example

In the following a sidechain constituted of 6 nodes is considered as reference. The nodes are called DSO, AGG, PR1, 
PR2, PR3, PR4 and their roles are reported below:

* **DSO**: node related to DSO Toolset, it is the unique validator in the chain 
* **AGG**: node related to Aggregator Toolset 
* **PRX**: node related to prosumer/oracle _X_

## Sidechain running:
To have the PM sidechain and its REST API running, all the instances of `$GOPATH/bin/pmd` executables and 
`server_pm.py` must run on the nodes. The former is the Cosmos application managing all the sidechain issues 
(consensus, networking, transactions, etc.). It is a standalone executable and saves all its data in `~/.pm` folder.
The latter is a Python server that acts as a bridge between an off-chain element of the node (e.g. the DSO Toolset) and 
the sidechain. Its script needs a configuration file similar to the following to run:

<pre>
{
  "server": {
    "host": "localhost",
    "port": 9119
  },
  "cosmos": {
    "protocol": "http",
    "host": "localhost",
    "port": 1317,
    "chainName": "pm",
    "folderSignatureFiles": "/tmp",
    "requestEndpointHeader": "supsi-dacd-isaac/pm/pm",
    "goRoot": "$path_of_go_root",
    "app": "pm",
    "token": "ect"
  }
}
</pre>

The element `cosmos.goRoot` is the only dependent on the GO installation on the node. The other parameters 
reported in the example above are already correct and have not to be changed.

In the following the commands to launch the sidechain and its REST API on a node are reported

<pre>
$GOPATH/bin/pmd start --log_format json >> ~/log/pm.log
(venv) python server_pm.py -c conf/config.json
</pre>

To check if the node are running and synced the following command can be used on all the nodes:

<pre>
tail -f ~/log/pm.log | grep _valid
</pre>

## Sidechain initilization:
Before running LEMs and SLAs/KPIs the sidechain must be properly initialized. Thus, some transactions have to run 
in order to set up the main sidechain information, e.g. who is the aggregator, by whom is composed the player map, 
which are the default market parameters, etc.   

The initialization is performed running the `sidechain_initializer.py` script and the related example configuration 
file as follows:

<pre>
(venv) python script/pm/sidechain_initializer.py -c conf/conf_sidechain_initializer_example.json

(venv) cat conf/conf_sidechain_initializer_example.json 
{
  "accountsAddressesfile": "conf/accounts_addresses.txt",
  "pseudonymization": {
    "enabled": true,
    "pseudonomizerWebService": "http://pseudo.nymi.zer",
    "timeout": 5
  },
  "sidechainRestApi": "http://localhost:9119",
  "roles": {
    "prosumers": ["PR1", "PR2", "PR3", "PR4"],
    "dso": "DSO",
    "aggregator": "AGG",
    "marketOperator": "DSO"
  },
  "defaultLemParameters": [
    {
      "gridState": "GREEN",
      "pbBAU": 20.0,
      "psBAU": 6.5,
      "pbP2P": 14.0,
      "psP2P": 8.0,
      "beta": 0.0
    },
    {
      "gridState": "YELLOW",
      "pbBAU": 24.0,
      "psBAU": 6.3,
      "pbP2P": 14.0,
      "psP2P": 8.0,
      "beta": 0.025
    }
  ]
}
</pre>

N.B. In order to use the pseudonymization service the proper section in the JSON file must be set properly. 

The file `"conf/accounts_addresses.txt"` contains the correspondences between the node identifiers (the pseudonyms) and 
the Cosmos accounts.

## LEMs management:
Typically, the LEMs have the same duration (15 minutes) and a set of LEMs is periodically solved (e.g. daily) 
in order to distribute the tokens accordingly to the production/consumption.
In the following paragraphs a generic LEM named _LEM_ts_te_ is taken into account as reference. 

### Grid State setting (DSO)
Before the starting of _LEM_ts_te_, DSO has to save the grid state of to the quarter of hour related to _LEM_ts_te_. 
The dataset stored in the sidechain is basically composed by the starting timestamp and 
the value (GREEN | YELLOW | RED). 

### LEM setting (AGG)
Before the starting of _LEM_ts_te_, AGG node has to save the features of _LEM_ts_te_, basically the starting/ending 
timestamps and the identifiers of the prosumers that will participate in _LEM_ts_te_.
Additionally, AGG can decide to refine the default parameters, which depend on the grid state. 
If not, default LEM parameters saved in th sidechain will be used during the LEM solving. 

### LEM data saving (PR1, PR2, PR3, PR4)
After the end of _LEM_ts_te_, each prosumer belonging to A has to save its power consumption/production related to 
_LEM_ts_te_ on the sidechain.

### LEM solving (AGG, PR1, PR2, PR3, PR4)
Periodically, the last markets are solved and the token accordingly moved. For example, if the market are daily solved,
at the beginning of each day the last 96 LEMs are solved.

### LEM example sequence:

* LEM duration: 15 minutes
* LEM solving: hourly
* Example period: 12:00-13:00

The following image shows the transactions sequence needed to run the first LEM in the hour 12:00-13:00 (called 
`LEM_Q1`) and the solution of the 4 LEMs in the example period. Below the explanations of the transactions colors:

* Orange: Transaction performed by DSO
* Green: Transaction performed by AGG
* Red: Transaction performed by PR1
* Light blue: Transaction performed by PR2
* Yellow: Transaction performed by PR3
* Violet: Transaction performed by PR4


![Alt text](img/LEM_sequences.png?raw=true "LEM sequences")

### Transactions to run before the LEM starting
Transactions 1 and 2 have to be performed before the beginning of the period related to the LEM, in the example 
12:00-12:15. Transaction 1 stores on the sidechain the grid state signal and is performed by DSO. Transaction 2 saves 
main LEM features, basically the list of the prosumer that will play the LEM (i.e. will store its energy 
production/consumption).

### Transactions to run after the LEM ending
Once LEM_Q1 is finished, in the example after 12:15, transactions 3, 4, 5 and 6 are performed by the the prosumer to 
store on the sidechain their energy production/consumption. 

### Transactions to solve a set of LEMs
Periodically (in the example on a hourly basis), nodes AGG, PR1, PR2, PR3 and PR4 perform transactions to update their 
balances accordingly to the solution of the LEMs related to the just past hour (12:00-13:00. 

### Complete sequence of the transactions:

<pre>
# LEM_Q1 -> period: [12:00-12:14], participants: P1, P2, P3, P4
12:00: DSO SETS THE GRID STATE FOR THE PERIOD [12:00-12:14]
12:00: AGG SETS THE LEM COMPONENTS FOR THE PERIOD [12:00-12:14] 
12:15: PR1 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:00-12:14]
12:15: PR2 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:00-12:14]
12:15: PR3 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:00-12:14]
12:15: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:00-12:14]

# LEM_Q2 -> period: [12:15-12:29], participants: P1, P2, P4
12:15: DSO SET THE GRID STATE FOR THE PERIOD [12:15-12:29]
12:15: AGG SET THE LEM COMPONENTS FOR THE PERIOD [12:15-12:29] 
12:30: PR1 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:15-12:29]
12:30: PR2 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:15-12:29]
12:30: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:15-12:29]

# LEM_Q3 -> period: [12:30-12:44], participants: P2, P3, P4
12:30: DSO SET THE GRID STATE FOR THE PERIOD [12:30-12:44]
12:30: AGG SET THE LEM COMPONENTS FOR THE PERIOD [12:30-12:44] 
12:45: PR2 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:30-12:44]
12:45: PR3 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:30-12:44]
12:45: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:30-12:44]

# LEM_Q4 -> period: [12:30-12:44], participants: P1, P4
12:45: DSO SET THE GRID STATE FOR THE PERIOD [12:45-12:59]
12:45: AGG SET THE LEM COMPONENTS FOR THE PERIOD [12:45-12:59] 
13:00: PR1 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:44-12:59]
13:00: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:44-12:59]

# MARKET SOLVING
13:01: LEM ENGINE ON AGG SOLVES THE MARKET (PRODUCTION MANAGEMENT)
13:01: LEM ENGINE ON PR1 SOLVES THE MARKET (CONSUMPTION MANAGEMENT)
13:01: LEM ENGINE ON PR2 SOLVES THE MARKET (CONSUMPTION MANAGEMENT)
13:01: LEM ENGINE ON PR3 SOLVES THE MARKET (CONSUMPTION MANAGEMENT)
13:01: LEM ENGINE ON PR4 SOLVES THE MARKET (CONSUMPTION MANAGEMENT)
</pre>


## SLA/KPIs management:
An SLA is basically defined by an identifier, a period when it is active and a set of KPIs.  
In the following paragraphs a generic SLA named _SLA_ts_te_ is taken into account as reference.

### SLA/KPIs setting (AGG)
Before the beginning of _SLA_ts_te_, AGG saves on the sidechain ist features (basically the period when it is active) 
and its KPIs.  
Each KPI has its own features, among them a rule (_gt_ | _lt_), a limit, a signal, a penalty in terms of tokens and a 
list of the prosumers that have to be compliant with it. 


### KPIs data saving (Oracles)
During the activation period the prosumers/oracles that must comly with the KPIs saves the related data on the 
sidechain. 

### KPIs solving (Oracles)
Periodically, the KPIs of the SLAs not more active but not yet checked are analyzed to see if the saved data are 
compliant with the related rules and limits. 

### SLA/KPI example sequence:

* SLA duration: 1 hours
* KPI rule: `max(Tint) > 21.0` (i.e. the hourly maximum of temperature signal `Tint` must be greater than 21.0 °C) 
* Example period: 12:00-14:00
* Involved prosumers : PR1, PR2, PR3, PR4 

The following image shows the transactions sequence needed to run a SLA comprehensive of a KPI in the interval 12:00-14:00.
In the example the data related to the KPI must be saved every hour. Below the explanations of the transactions colors:

* Green: Transaction performed by AGG
* Red: Transaction performed by PR1
* Light blue: Transaction performed by PR2
* Yellow: Transaction performed by PR3
* Violet: Transaction performed by PR4

![Alt text](img/SLAKPI_sequences.png?raw=true "SLA/KPI sequences")

### Transactions to run before the SLA/KPI starting
Transactions 1 and 2 have to be performed before the beginning of the period related to the SLA, in the example 
12:00-12:59. Transaction 1 stores on the sidechain the SLA features, like the identifier and the interval. 
Transaction 2 saves data about the KPI features (e.g. threshold, token penalty, etc.).

N.B. In this simple example we have a SLA with a KPI. In a generic case with N KPIs, the amount of the transactions to 
perform will be N+1.

### Transactions to run after the SLA/KPI ending
After the SLA/KPIs ending each involved prosumers has to store on the sidechain its `max(Tint)` value (transactions 3, 4, 5, 6).

### Transactions to solve a set of SLA/KPIs
Periodically (in the example every two hours), each prosumer involved on at least one KPI of the last SLAs (in 
the example PR1, PR2, PR3 and PR4) checks if it was always compliant. If not, it performs a transaction related to the 
total tokens penalty.

N.B. As shown in the example, only two prosumers (PR1 and PR4) will have a penalty (transactions 7 and 8), but not PR2 and PR3.
This fact happens because in the example PR1 and PR4 were not compliant with all the KPIs of the past two hours. 
On the contrary, PR2 and PR3 were always compliant and so they have not penalties.

### Complete sequence of the transactions:

* SLA1 and SLA2 duration: 1 hour (SLA1 -> [12:00-12:59], SLA2 -> [13:00-13:59])
* KPIs: SLA1 -> KPI11 and KPI12; SLA2 -> KPI21 and KPI22 
* PR1 and PR2 must be compliant to KPI11 and KPI21
* PR3 and PR4 must be compliant to KPI21 and KPI22
* Example period: 12:00-14:00

<pre>
# SLA1 definition
11:59: SLA CHECKER ON AGG SETS SLA1 AND ITS KPIS (KPI11 and KPI12) FOR THE PERIOD [12:00-12:59]

# KPI11 and KPI12 related data saving 
13:00: PR1 SAVES THE KPI11 VALUE RELATED TO [12:00-12:59]
13:00: PR2 SAVES THE KPI11 VALUE RELATED TO [12:00-12:59]
13:00: PR3 SAVES THE KPI12 VALUE RELATED TO [12:00-12:59]
13:00: PR4 SAVES THE KPI12 VALUE RELATED TO [12:00-12:59]

# SLA2 definition
12:59: SLA CHECKER ON AGG SETS SLA2 AND ITS KPIS (KPI21 and KPI22) FOR THE PERIOD [13:00-13:59]

# KPI21 and KPI22 related data saving
14:00: PR1 SAVES THE KPI21 VALUE RELATED TO [13:00-13:59]
14:00: PR2 SAVES THE KPI21 VALUE RELATED TO [13:00-13:59]
14:00: PR3 SAVES THE KPI22 VALUE RELATED TO [13:00-13:59]
14:00: PR4 SAVES THE KPI22 VALUE RELATED TO [13:00-13:59]

# KPIs solving
14:01: SLA PAYMENT ENGINE ON PR1 CHECKS KPI11 AND KPI21 VALUES AND, IN CASE, APPLIES A PENALTY
14:01: SLA PAYMENT ENGINE ON PR2 CHECKS KPI11 AND KPI21 VALUES AND, IN CASE, APPLIES A PENALTY
14:01: SLA PAYMENT ENGINE ON PR3 CHECKS KPI21 AND KPI22 VALUES AND, IN CASE, APPLIES A PENALTY
14:01: SLA PAYMENT ENGINE ON PR4 CHECKS KPI21 AND KPI22 VALUES AND, IN CASE, APPLIES A PENALTY
</pre>
