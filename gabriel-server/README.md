# Gabriel Server

The cognitive_engine module can be used to process incoming data.

The local_engine runs the websocket server within the same Python program as the
Websocket Server.

The network_engine module contains engine_server_shuttle which runs just the
Websocket Server. The engine_runner in network_engine runs just a cognitive
engine. The engine_server_shuttle and network_engine communicate with each other
using zmq.

## Installation
Requires Python >= 3.5 

Run `pip install gabriel-server`

## Publishing Changes to PyPi

Update the version number in setup.py. Then follow [these instructions](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives).
