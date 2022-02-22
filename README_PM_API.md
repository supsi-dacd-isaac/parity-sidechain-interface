# PM (Parity market) REST API:

The REST API runs on `localhost:9119` as default, the configuration can be changed in `conf/*.json` configuration files. 
Basically local POST requests are used to run transactions on the sidechain, while with GETs it is possible to perform queries
to read data.

In the following a simple sidechain constituted by 4 nodes is considered as reference. The nodes play the related 
roles in the PM application:

* the DSO, called `severus`
* the AGG, called `albus`
* the prosumers, called `harry` and `hermione` 

In the real cases the names have to be pseudonymized in order to preserve the privacy and be GDPR-compliant.

## Elements manageable by PM REST API:

* **_account_**: Account information (e.g. name and address of the node).
* **_balances_**: Balances information (e.g. token owned by an account).
* **_dso_**: Single element representing the node responsible for the maintenance of `player` and `gridState` maps.  
* **_aggregator_**: Single element representing the node responsible for the management of `lem`, `sla` and `kpi` maps.
* **_marketOperator_**: Single element representing the node responsible for the management of `defaultLemPars` maps.
* **_player_** map: The list of the prosumers allowed to be included by `AGG` in a LEM (i.e. the prosumers on the same LV trafo)
* **_defaultLemPars_** map: Container of the default LEM parameters 
* **_lem_** map: Container of the LEMs (Local Energy Markets)
* **_lemDataset_** map: Container of the power time series related to the LEMs
* **_sla_** map: Container of the SLA definition
* **_kpiFeatures_** map: Container of the KPIs, each of them is linked to a SLA
* **_kpiMeasure_** map: Container of the time series related to a KPI
* **_gridState_** map: Container of the grid states
  
## **_account_** element:

<pre>
curl -X GET "http://localhost:9119/account" 
{"name": "severus", "type": "local", "address": "cosmos123snape", "pubkey": "{\"@type\":\"/cosmos.crypto.secp256k1.PubKey\",\"key\":\"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\"}" 
</pre>

N.B.
The output of the query is related to the node account. 

## **_balances_** element:

<pre>
curl -X GET "http://localhost:9119/balances/cosmos123granger" 
{
  "balances": [
    {
      "denom": "ect",
      "amount": "1000000"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "1"
  }
} 
</pre>

## **_dso_** element:

### Creation:

<pre>
curl -X POST http://localhost:9119/createDso -H 'Content-Type: application/json' -d '{"idx":"severus", "address":"cosmos123snape"}' 
</pre>

### Data retrieving:

<pre>
curl -X GET "http://localhost:9119/dso" 
{
  "Dso": {
    "idx": "severus",
    "address": "cosmos123snape",
    "creator": "cosmos123snape"
  }
}
</pre>

## **_aggregator_** element:

### Creation:

`aggregator` must be created by `DSO` node.

<pre>
curl -X POST http://localhost:9119/createAggregator -H 'Content-Type: application/json' -d '{"idx":"albus", "address":"cosmos123dumbledore"}' 
</pre>

### Data retrieving:

<pre>
curl -X GET "http://localhost:9119/aggregator" 
{
  "Dso": {
    "idx": "albus",
    "address": "cosmos123dumbledore",
    "creator": "cosmos123snape"
  }
}
</pre>

## **_player_** map:

`player` map must be edited by `DSO` node.

### Elements creation (DSO, AGG and prosumers):

<pre>
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"severus", "address":"cosmos123snape", "role": "dso"}' 
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"albus", "address":"cosmos123dumbledore", "role": "aggregator"}' 
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"hermione", "address":"cosmos123granger", "role": "prosumer"}' 
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"harry", "address":"cosmos123potter", "role": "prosumer"}' 
</pre>

Where:
* `role`: Role of the player in the LEMs (`dso | aggregator | prosumer`)

## **_marketOperator_** element:

`marketOperator` must be created by `DSO` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createMarketOperator -H 'Content-Type: application/json' -d '{"idx":"rubeus", "address":"cosmos123hagrid"}' 
</pre>

### Data retrieving:

<pre>
curl -X GET "http://localhost:9119/marketOperator" 
{
  "Dso": {
    "idx": "rubeus",
    "address": "cosmos123hagrid",
    "creator": "cosmos123snape"
  }
}
</pre>

## **_defaultLemPars_** map:

`defaultLemPars` map must be edited by `DSO` node.

### Elements creation:

<pre>
curl -X POST http://localhost:9119/createDefaultLemPars -H 'Content-Type: application/json' -d '{"lemCase":"GREEN", "pbBAU":"20.0", "psBAU":"5.0", "pbP2P":"15.0", "psP2P":"7.0", "beta":"0.2"}'  
</pre>


### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/defaultLemPars"
{
  "defaultLemPars": [
    {
      "index": "GREEN",
      "pbBAU": "20.0",
      "psBAU": "5.0",
      "pbP2P": "15.0",
      "psP2P": "7.0",
      "beta": "0.2",
      "creator": "cosmos123snape"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "1"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/defaultLemPars/GREEN"
{
  "defaultLemPars": [
    {
      "index": "GREEN",
      "pbBAU": "20.0",
      "psBAU": "5.0",
      "pbP2P": "15.0",
      "psP2P": "7.0",
      "beta": "0.2",
      "creator": "cosmos123snape"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "1"
  }
}
</pre>

## **_lem_** map:

`lem` map must be edited by `AGG` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createLem -H 'Content-Type: application/json' \
            -d '{"start":1608897600, "end":1608898500, "aggregator": "albus", "state": "ACTIVE", "marketParameters": [0.2, 0.065, 0.14, 0.08, 0], "players": ["harry", "hermione"]}'
curl -X POST http://localhost:9119/createLem -H 'Content-Type: application/json' \
            -d '{"start":1608984000, "end":1608984900, "aggregator": "albus", "state": "ACTIVE", "marketParameters": [0.24, 0.045, 0.14, 0.08, 0.025], "players": ["harry", "hermione"]}'
</pre>

Where:
* `start`: LEM starting timestamp
* `end`: LEM ending timestamp
* `aggregator`: Aggregator identifier
* `state`: LEM state (`ACTIVE | CLOSED`)
* `marketParameters`: Parameters of the LEM (`[price_buy(BAU), price_sell(BAU), price_buy(P2P), price_sell(P2P), beta]`)
* `players`: Prosumers constituting the LEM

### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/lem"
{
  "lem": [
    {
      "index": "1608897600-1608898500-albus",
      "start": 1608897600,
      "end": 1608898500,
      "params": [
        "ACTIVE",
        "0.2",
        "0.65",
        "0.14",
        "0.08",
        "0"
      ],
      "players": [
        "harry",
        "hermione"
      ],
      "creator": "cosmos123dumbledore"
    },
    {
      "index": "1608984000-1608984900-albus",
      "start": 1608984000,
      "end": 1608984900,
      "params": [
        "CLOSED",
        "0.24",
        "0.45",
        "0.14",
        "0.08",
        "0.025"
      ],
      "players": [
        "harry",
        "hermione"
      ],
      "creator": "cosmos123dumbledore"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "2"
  }
}
</pre>

N.B. If no market parameters are saved in the `params` sections when LEM is created (i.e. `params=["ACTIVE", 0, 0, 0, 0, 0]`)
then the settings defined in `defaultLemPars` will be taken into account during the LEM solving. Consequently,
the only information that `AGG` must know and set on the sidechain to have a valid LEM is the players list.

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/lem/1608984000-1608984900-albus" 
{
  "index": "1608984000-1608984900-albus",
  "start": 1608984000,
  "end": 1608984900,
  "params": [
    "CLOSED",
    "0.24",
    "0.45",
    "0.14",
    "0.08",
    "0.025"
  ],
  "players": [
    "harry",
    "hermione"
  ],
  "creator": "cosmos123dumbledore"
}
</pre>

## **_lemDataset_** map:

`lemDataset` is edited by the prosumers belonging to `player`map.

### Creation:

* **Without forecasts saving:**

<pre>
curl -X POST http://localhost:9119/createLemDataset -H 'Content-Type: application/json' \ 
             -d '{"player":"hermione", "timestamp": 1608984000, "powerConsumptionMeasure": 2345.7, \ 
                  "powerProductionMeasure": 1462.3, "powerConsumptionForecast": "None", "powerProductionForecast": "None"}'
</pre>

* **With saving of the forecasts related to the 4 next steps:**

<pre>
curl -X POST http://localhost:9119/createLemDataset -H 'Content-Type: application/json' \ 
             -d '{"player":"hermione", "timestamp": 1608984000, \
                  "powerConsumptionMeasure": 2345.7, "powerProductionMeasure": 1462.3, \ 
                  "powerConsumptionForecast": "2250,2400,1600,1750", "powerProductionForecast": "1400,1600,1800,1800"}'
</pre>


Where:
* `player`: Prosumer saving the data
* `timestamp:` Timestamp related to the measure
* `powerConsumptionMeasure:` Measure related to the power consumption
* `powerProductionMeasure:` Measure related to the power production
* `powerConsumptionForecast:` Forecast related to the power consumption (currently not used by the sidechain)
* `powerProductionForecast:` Forecast related to the power production (currently not used by the sidechain)

### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/lemDataset"
{
  [
    {
      "index": "harry-1608984000",
      "player": "harry",
      "timestamp": 1608984000,
      "pconsMeasure": "3657.3",
      "pprodMeasure": "0.0",
      "pconsForecast": "None",
      "pprodForecast": "None",
      "creator": "cosmos123potter"
    }
    },
    {
      "index": "hermione-1608984000",
      "player": "hermione",
      "timestamp": 1608984000,
      "pconsMeasure": "2345.7",
      "pprodMeasure": "1462.3",
      "pconsForecast": "None",
      "pprodForecast": "None",
      "creator": "cosmos123granger"
    }
    }
  ],
  "pagination": {
    "next_key": "MDgwNGQxOWIyZjA0NWY1YzgyNjE5YjA5NDhmOWY1YjM4NWYxNTNlMjA0NTdhZWIxMTBhNGU2ZmUzNThiODY4Ny1QLTE2MzgyMDgwODAv",
    "total": "2"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/lemMeasure/hermione-1608984000"
{
  "lemMeasure": {
      "index": "hermione-1608984000",
      "player": "hermione",
      "timestamp": 1608984000,
      "pconsMeasure": "2345.7",
      "pprodMeasure": "1462.3",
      "pconsForecast": "None",
      "pprodForecast": "None",
      "creator": "cosmos123granger"
  }
}
</pre>

## **_sla_** map:

`sla` map must be edited by `AGG` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createSla -H 'Content-Type: application/json' -d '{"idx":"comfort01", "start":1607601600, "end":1607688000}'
</pre>

Where:
* `idx`: SLA identifier
* `start`: SLA starting timestamp
* `end`: SLA ending timestamp

### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/sla"
{
  "sla": [
    {
      "index": "comfort01",
      "start": 1607601600,
      "end": 1607688000,
      "creator": "cosmos123dumbledore"
    },
    {
      "index": "comfort02",
      "start": 1607601600,
      "end": 1607688000,
      "creator": "cosmos123dumbledore"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "2"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/sla/comfort01"
{
  "sla": {
    "index": "comfort01",
    "start": 1607601600,
    "end": 1607688000,
    "creator": "cosmos123dumbledore"
  }
}
</pre>

## **_kpiFeatures_** map:

`kpiFeatures` map must be edited by `AGG` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createKpi -H 'Content-Type: application/json' \
            -d '{"idx":"temp_too_high", "idxSla":"comfort01", "rule": "gt", "limit": 24.5, "measureUnit": "°C", "penalty": 120, "players": ["harry", "hermione"]}'
</pre>

Where:
* `idx`: KPI identifier
* `idxSLA`: SLA identifier to which the KPI belongs
* `rule`: KPI rule (`lt | gt`)
* `limit`: Limit value
* `measureUnit`: Measure unit of the limit
* `penalty`: Tokens penalty
* `players`: Players/prosumers that have to comply the KPI 


### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/kpi"
{
  "kpi": [
    {
      "index": "temp_too_high",
      "sla": "comfort01",
      "rule": "gt",
      "limit": "24.5",
      "mu": "°C",
      "penalty": 120,
      "players": [
        "harry",
        "hermione"
      ],
      "creator": "cosmos123dumbledore"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "1"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/kpi/temp_too_high"
{
  "kpi": {
    "index": "temp_too_high",
    "sla": "comfort01",
    "rule": "gt",
    "limit": "24.5",
    "mu": "°C",
    "penalty": 120,
    "players": [ 
      "harry",
      "hermione"
    ],
    "creator": "cosmos123dumbledore"
  }
}
</pre>


## **_kpiMeasure_** map:

`kpiMeasure` is edited by the prosumers belonging to `player`map.

### Creation:

<pre>
curl -X POST http://localhost:9119/createKpiMeasure -H 'Content-Type: application/json' 
            -d '{"player":"hermione", "kpi":"temp_too_high", "timestamp": 1607601600, "value": 23.9, "measureUnit": "°C"}'
curl -X POST http://localhost:9119/createKpiMeasure -H 'Content-Type: application/json' 
            -d '{"player":"harry", "kpi":"temp_too_high", "timestamp": 1607601600, "value": 24.7, "measureUnit": "°C"}'
</pre>

### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/kpiMeasure"
{
  "kpiMeasure": [
    {
      "index": "hermione-temp_too_high-1607601600",
      "player": "hermione",
      "kpi": "temp_too_high",
      "timestamp": 1607601600,
      "value": "23.9",
      "mu": "°C",
      "creator": "cosmos123granger"
    },
    {
      "index": "harry-temp_too_high-1607601600",
      "player": "harry",
      "kpi": "temp_too_high",
      "timestamp": 1607601600,
      "value": "24.7",
      "mu": "°C",
      "creator": "cosmos123potter"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "2"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/kpiMeasure/hermione-temp_too_high-1607601600"
{
  "kpiMeasure": {
    "index": "hermione-temp_too_high-1607601600",
    "player": "hermione",
    "kpi": "temp_too_high",
    "timestamp": 1607601600,
    "value": "23.9",
    "mu": "°C",
    "creator": "cosmos123granger"
  }
}
</pre>

## **_gridState_** map:

`kpiMeasure` must be edited by `DSO` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createGridState -H 'Content-Type: application/json' -d '{"grid":"hogwarts", "timestamp": 1607601600, "state": "GREEN"}'
</pre>

N.B. Available states: `GREEN`, `YELLOW `, `RED`

### Data retrieving of the entire map:

<pre>
curl -X GET http://localhost:9119/gridState
{
  "gridState": [
    {
      "index": "1607601600-hogwarts",
      "grid": "hogwarts",
      "timestamp": 1607601600,
      "state": "GREEN",
      "creator": "cosmos123snape"
    },
    {
      "index": "1641830160-hogwarts",
      "grid": "hogwarts",
      "timestamp": 1641830160,
      "state": "YELLOW",
      "creator": "cosmos123snape"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "2"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -XGET http://localhost:9119/gridState/1607601600-hogwarts
{
  "gridState": {
    "index": "1607601600-hogwarts",
    "grid": "hogwarts",
    "timestamp": 1607601600,
    "state": "GREEN",
    "creator": "cosmos123snape"
  }
}
</pre>
