# parity-sidechain-interface

## Prepaid scenario:

It is highly recommended using a custom virtual environment to run the server and the tests scripts.
In the following the venv is supposed to be installed in the root folder.  

### REST API server:

The REST server (PSRS) that interacts with the prepaid-Scenario sidechain application (PSSA) has to be launched typing the following command:

<pre>
(venv) cd $ROOT
(venv) python venv/bin/python server_ps.py -c conf/server.json
</pre>

Using properly PSRS, a HTTP client can easily interact with PSSA (see the following tests).

<pre>
user -> HTTP client <-> PSRS <-> PSSA <-> SIDECHAIN
</pre>

### Server configuration example:

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
    "chainName": "encom_chain",
    "folderSignatureFiles": "/tmp",
    "goRoot": "$go_root_folder",
    "app": "ps",
    "token": "ectoken"
  }
}
</pre>

In the following a brief explanations of the main settings:
* `server.host`: host of PSRS socket (it should always be localhost) 
* `server.port`: port of PSRS socket 
* `cosmos.host`: host of PSSA socket (it must always be localhost) 
* `cosmos.port`: port of PSSA socket (it must always be 1317)
* `goRoot`: GO root folder (e.g. `/home/pi/go`)
* `cosmos.app`: application name (ps: Prepaid scenario)

### Tests scripts:

These scripts contain exhaustive tests that can be used as examples to understand how to interact with PSRS.
All the scripts (with the exception of `tests/wallet_reader.py` that do not require arguments) needs the following input:

<pre>
(venv) python $script -m $mac_address_eth0
</pre>
 
`$mac_address_eth0` is the MAC address of the node. This is needed because PSSA uses it as nodes identifiers.

As example, in Labtrial node `pi@parity.00000000b9b968bf@116.203.153.237` the MAC address is `b8:27:eb:b9:68:bf`.

**admin_management.py:**

This script updates new community administrator, and can be run only by the current one.
In the Labtrial sidechain the current administrator node is `b8:27:eb:b9:68:bf` and the scripts simply defines again the same node identifier.

*Usage on `pi@parity.00000000b9b968bf@116.203.153.237` node:*
<pre>
(venv) python tests/admin_management.py -m b8:27:eb:b9:68:bf

</pre>

**allowed_management.py:**

This script defines the meters can save data on the sidechain, currrently the four nodes constituting the LAbTrial are already inserted in the list.
Only the administrator is allowed to run this script.

*Usage on `pi@parity.00000000b9b968bf@116.203.153.237` node:*
<pre>
(venv) python tests/allowed_management.py -m b8:27:eb:b9:68:bf
</pre>

**market_parameters_management.py:**

This script saves example market parameters on the sidechain. Only the administrator is allowed to change the parameters.

*Usage on `pi@parity.00000000b9b968bf@116.203.153.237` node:*
<pre>
(venv) python tests/market_parameters_management.py -m b8:27:eb:b9:68:bf
</pre>

Here a brief explanation of the parameters:

* 'prodConvFactor' (currently set to 1): energy production conversion factor (token/Wh)
* 'consConvFactor' (currently set to 2): energy consumption conversion factor (token/Wh)
* 'consConvFactor' (currently set to 100): not used
* 'penalty' (currently set to 20): not used

The parameters can be updated changing properly `market_parameters_management.py` script.

**measure_management.py:**

Running this script a generic measure of signal `PImp` is stored on the DB. Any allowed meter can run this script. 

*Usage on `pi@parity.00000000b9b968bf@116.203.153.237` node:*
<pre>
(venv) python tests/measure_management.py -m b8:27:eb:b9:68:bf
</pre>

Changing the script code and running it periodically it is possible to save time-series on the sidechain for a generic signal.

N.B.: Saving data about `PImp`/`PExp` signals results in an additional saving of `E_cons`/`E_prod` related to energy 
consumption/production (we suppose to have 15 minutes resolution data => energy [Wh] = power [W] * 1[h]/4 ) and in an update
of the node wallet according to the configured market parameters.

**venv/bin/python tests/wallet_reader.py:**
Script to read the node wallet.

*Usage on any node:*
<pre>
(venv) python tests/wallet_reader.py
</pre>