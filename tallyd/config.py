from dataclasses import dataclass
import json


@dataclass
class TallydConfig():
    tally_kinds: tuple = ("live", "preview")
    initial_cameras: int = 0

    control_port: int = 5762
    client_port: int = 5763


def load_config(obj):
    return TallydConfig(
        tuple(obj["tally"]),
        obj["cameras"],
        obj["ports"]["control"],
        obj["ports"]["client"]
    )
