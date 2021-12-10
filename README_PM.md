# PM (Parity market) REST API:

The REST API runs on `localhost:1317` as default, the configuration can be changed in `conf/*.json` configuration files. 
Basically local POST requests are used to run transactions on the sidechain, while with GETs it is possible to perform queries
to read data.

In the following a simple sidechain constituted by 4 nodes is considered as reference. The nodes play the related 
roles in the PM application:

* the DSO, called `severus`
* the AGG, called `albus`
* the prosumers, called `harry` and `hermione` 

In the real cases the names have to be pseudonymized in order to preserve the privacy and be GDPR-compliant.

## Elements manageable by PM REST API:

* **_Account_**: Account information (e.g. name and address of the node).
* **_DSO_**: Single element representing the node responsible for the maintenance of the `player` map.  
* **_AGG_**: Single element representing the node responsible for the management of `lem`, `sla` and `kpi` maps.
* **_Player_** map: The list of the prosumers allowed to be included by `AGG` in a LEM (i.e. the prosumers on the same LV trafo)
* **_lem_** map: Container of the LEMs (Local Energy Markets)
* **_lemDataset_** map: Container of the power time series related to the LEMs
* **_SLA_** map: Container of the SLA definition
* **_KPI_** map: Container of the KPI definition, each of them is linked to a SLA
* **_kpiMeasure_** map: Container of the time series related to a KPI
  
## **_Account_** element:

<pre>
curl -X GET "http://localhost:9119/account" 
{"name": "severus", "type": "local", "address": "cosmos123snape", "pubkey": "{\"@type\":\"/cosmos.crypto.secp256k1.PubKey\",\"key\":\"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\"}" 
</pre>

N.B.
The output of the query above is returned only running the command on the DSO node. 

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

`AGG` must be created by `DSO` node.

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

`Player` map must be edited by `DSO` node.

### Elements creation (DSO, AGG and prosumers):

<pre>
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"severus", "address":"cosmos123snape", "role": "dso"}' 
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"albus", "address":"cosmos123dumbledore", "role": "aggregator"}' 
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"hermione", "address":"cosmos123granger", "role": "prosumer"}' 
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"harry", "address":"cosmos123potter", "role": "prosumer"}' 
</pre>

Where:
* `role`: Role of the player in the LEMs (`dso | aggregator | prosumer`)

### Data retrieving of the entire map:

<pre>
curl -X GET "http://localhost:9119/player" 
{
  "player": [
    {
      "index": "harry",
      "idx": "harry",
      "address": "cosmos123potter",
      "role": "prosumer",
      "creator": "cosmos123snape"
    },
    {
      "index": "albus",
      "idx": "albus",
      "address": "cosmos123dumbledore",
      "role": "aggregator",
      "creator": "cosmos123snape"
    },
    {
      "index": "hermione",
      "idx": "hermione",
      "address": "cosmos123granger",
      "role": "prosumer",
      "creator": "cosmos123snape"
    },
    {
      "index": "severus",
      "idx": "severus",
      "address": "cosmos123snape",
      "role": "dso",
      "creator": "cosmos123snape"
    }
  ],
  "pagination": {
    "next_key": null,
    "total": "4"
  }
}
</pre>

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/player/hermione" 
{
  "player": {
    "index": "hermione",
    "idx": "hermione",
    "address": "cosmos123granger",
    "role": "prosumer",
    "creator": "cosmos123snape"
  }
}
</pre>

## **_lem_** map:

`lem` map must be edited by `AGG` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createLem -H 'Content-Type: application/json' \
            -d '{"start":1608897600, "end":1608898500, "aggregator": "albus", "case": "green", "marketParameters": [0.2, 0.065, 0.14, 0.08, 0], "players": ["harry", "hermione"]}'
curl -X POST http://localhost:9119/createLem -H 'Content-Type: application/json' \
            -d '{"start":1608984000, "end":1608984900, "aggregator": "albus", "case": "yellow", "marketParameters": [0.24, 0.045, 0.14, 0.08, 0.025], "players": ["harry", "hermione"]}'
</pre>

Where:
* `start`: LEM starting timestamp
* `end`: LEM ending timestamp
* `aggregator:` Aggregator identifier
* `case:` Traffic light signal (`green | yellow | red`)
* `marketParameters:` Parameters of the LEM (`[price_buy(BAU), price_sell(BAU), price_buy(P2P), price_sell(P2P), beta]`)
* `players:` Prosumers constituting the LEM

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
        "green",
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
        "green",
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

### Data retrieving of a single element

<pre>
curl -X GET "http://localhost:9119/lem/1608984000-1608984900-albus" 
{
  "index": "1608984000-1608984900-albus",
  "start": 1608984000,
  "end": 1608984900,
  "params": [
    "green",
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

<pre>
curl -X POST http://localhost:9119/createLemDataset -H 'Content-Type: application/json' \ 
             -d '{"player":"hermione", "timestamp": 1608984000, "powerConsumptionMeasure": 2345.7, \ 
                  "powerProductionMeasure": 1462.3, "powerConsumptionForecast": "None", "powerProductionForecast": "None"}'
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

## **_kpi_** map:

`kpi` map must be edited by `AGG` node.

### Creation:

<pre>
curl -X POST http://localhost:9119/createKpi -H 'Content-Type: application/json' \
            -d '{"idx":"temp_too_high", "idxSla":"comfort01", "rule": "gt", "limit": 24.5, "measureUnit": "°C", "penalty": 120}'
</pre>

Where:
* `idx`: KPI identifier
* `idxSLA`: SLA identifier to which the KPI belongs
* `rule:` KPI rule (`lt | gt`)
* `limit:` Limit value
* `measureUnit:` Measure unit of the limit
* `penalty:` Tokens penalty


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

