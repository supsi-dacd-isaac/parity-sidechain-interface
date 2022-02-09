# PM (Parity market) application:

## Sidechain example

In the following a sidechain constituted of 6 nodes is considered as reference. The nodes are called DSO, AGG, PR1, 
PR2, PR3, PR4 and their roles are reported below:

* **DSO**: node related to DSO Toolset 
* **AGG**: node related to Aggregator Toolset 
* **PRX**: node related to prosumer/oracle _X_

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

The file `"conf/accounts_addresses.txt"` contains the correspondences between the node identifiers(the pseudonyms) and 
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

<pre>
# FIRST LEM -> period: [12:00-12:14], participants: P1, P4
12:00: DSO SETS THE GRID STATE FOR THE PERIOD [12:00-12:14]
12:00: AGG SETS THE LEM COMPONENTS FOR THE PERIOD [12:00-12:14] 
12:15: PR1 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:00-12:14]
12:15: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:00-12:14]

# SECOND LEM -> period: [12:15-12:29], participants: P1, P2, P4
12:15: DSO SET THE GRID STATE FOR THE PERIOD [12:15-12:29]
12:15: AGG SET THE LEM COMPONENTS FOR THE PERIOD [12:15-12:29] 
12:30: PR1 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:15-12:29]
12:30: PR2 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:15-12:29]
12:30: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:15-12:29]

# THIRD LEM -> period: [12:30-12:44], participants: P2, P3, P4
12:30: DSO SET THE GRID STATE FOR THE PERIOD [12:30-12:44]
12:30: AGG SET THE LEM COMPONENTS FOR THE PERIOD [12:30-12:44] 
12:45: PR2 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:30-12:44]
12:45: PR3 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:30-12:44]
12:45: PR4 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:30-12:44]

# THIRD LEM -> period: [12:30-12:44], participants: P1, P2, P3, P4
12:45: DSO SET THE GRID STATE FOR THE PERIOD [12:45-12:59]
12:45: AGG SET THE LEM COMPONENTS FOR THE PERIOD [12:45-12:59] 
13:00: PR1 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:44-12:59]
13:00: PR2 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:44-12:59]
13:00: PR3 SAVES THE POWER CONSUMPTION/PRODUCTION RELATED TO [12:44-12:59]
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

### Example sequence:

* SLA duration: 2 hours
* KPIs (KPI1 and KPI2) time resolution: 1 hour
* PR1 and PR2 must be compliant to KPI1
* PR3 and PR4 must be compliant to KPI2
* Example period: 12:00-14:00

<pre>
# SLA/KPIs definition
12:00: SLA CHECKER ON AGG SETS THE SLA AND ITS KPIS (KPI1 and KPI2) FOR [12:00-14:00]

# FIRST HOUR
13:00: PR1 SAVES THE KPI1 VALUE RELATED TO [12:00-12:59]
13:00: PR2 SAVES THE KPI1 VALUE RELATED TO [12:00-12:59]
13:00: PR3 SAVES THE KPI2 VALUE RELATED TO [12:00-12:59]
13:00: PR4 SAVES THE KPI2 VALUE RELATED TO [12:00-12:59]

# SECOND HOUR
14:00: PR1 SAVES THE KPI1 VALUE RELATED TO [13:00-13:59]
14:00: PR2 SAVES THE KPI1 VALUE RELATED TO [13:00-13:59]
14:00: PR3 SAVES THE KPI2 VALUE RELATED TO [13:00-13:59]
14:00: PR4 SAVES THE KPI2 VALUE RELATED TO [13:00-13:59]

# KPIs solving
15:00: SLA PAYMENT ENGINE ON PR1 CHECKS THE KPI1 VALUES AND, IN CASE, APPLIES A PENALTY
15:00: SLA PAYMENT ENGINE ON PR2 CHECKS THE KPI1 VALUES AND, IN CASE, APPLIES A PENALTY
15:00: SLA PAYMENT ENGINE ON PR3 CHECKS THE KPI2 VALUES AND, IN CASE, APPLIES A PENALTY
15:00: SLA PAYMENT ENGINE ON PR4 CHECKS THE KPI2 VALUES AND, IN CASE, APPLIES A PENALTY

</pre>

