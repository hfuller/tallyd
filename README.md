# tallyd

tallyd is a daemon for keeping track of and distributing tally information.

## Install

In a Python 3 (virtual) environment:

```
~ $ git clone https://github.com/hfuller/tallyd.git
...
~ $ cd tallyd
~/tallyd $ pip3 install -e .
...
~/tallyd $ tallyd --help
Usage: tallyd [OPTIONS] COMMAND [ARGS]...
...
```

## Run

Copy `config.json.example` to a file named however you like, and edit the
config defaults appropriately.

Note the following:

- There must be at least one, but no more than eight, kinds of tally.
- "cameras" is a minimum. If you try to set tally for a camera that is beyond
  the "cameras" configuration value, it will succeed. The resulting tally update
  sent to tally clients, and future tally updates, will include this camera, as
  well as all cameras between it and the previous maximum camera.
- The "ports" do not have to be consecutive.

In the same Python environment as above:

```
~ $ tallyd start /path/to/config.json
```

## Updating tally

Connect to the defined "control" port using netcat/telnet/whatever. Then you can
send lines like the following:

* `{"cmd": "set", "camera": 2, "kind": "live"}` sets tally for the camera with
  the given ID to the given "kind". The kind must be specified in the config
  file.
* `{"cmd": "get", "camera": 2}` gets tally for the camera with the given ID.
* `{"cmd": "subscribe"}` activates update notifications on this connection.
* `{"cmd": "quit"}` cleanly closes your connection.
