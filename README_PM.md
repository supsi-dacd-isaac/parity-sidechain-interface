# parity-sidechain-interface

## PM (Parity market):

Main bash commands commands:

<pre>
ID_DSO=goofy
ADDRESS_DSO=cosmos123goofy

ID_AGGREGATOR=scrooge
ADDRESS_AGGREGATOR=cosmos123scrooge

ID_PROSUMER=donald
ADDRESS_PROSUMER=cosmos123donald


curl -X POST http://localhost:9119/createDso -H 'Content-Type: application/json' -d '{"idx":"$ID_DSO", "address":"$ADDRESS_DSO"}' && echo
curl -X POST http://localhost:9119/createAggregator -H 'Content-Type: application/json' -d '{"idx":"$ID_AGGREGATOR", "address":"$ADDRESS_AGGREGATOR"}' && echo

curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"$ID_DSO", "address":"$ADDRESS_DSO", "role": "dso"}' && echo
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"$ID_AGGREGATOR", "address":"$ADDRESS_AGGREGATOR", "role": "aggregator"}' && echo
curl -X POST http://localhost:9119/createPlayer -H 'Content-Type: application/json' -d '{"idx":"$ID_PROSUMER", "address":"$ADDRESS_PROSUMER", "role": "prosumer"}' && echo

curl -X POST http://localhost:9119/createLemMeasure -H 'Content-Type: application/json' -d '{"player":"$ID_PROSUMER", "signal":"P", "timestamp": 1500, "value": 230.4, "measureUnit": "W"}' && echo

</pre>