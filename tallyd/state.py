from dataclasses import dataclass
import collections


TallyState = collections.namedtuple(
    "TallyState", ["is_on", "kind"], defaults=(False, ""))


class TallyStateManager():
    """
    >>> t = TallyStateManager()
    >>> t.set_tally(1, "preview")
    >>> t.set_tally(2, "live")
    >>> t.get_all_numeric_tally()
    (2, 1)
    >>> t.set_tally(2, "off")
    >>> t.get_all_numeric_tally()
    (2, 0)
    >>> t.set_tally(3, "off")
    >>> t.get_all_numeric_tally()
    (2, 0, 0)
    >>> t.set_tally(8, "live")
    >>> t.get_all_numeric_tally()
    (2, 0, 0, 0, 0, 0, 0, 1)
    >>> t.set_max_camera(10)
    >>> t.get_all_numeric_tally()
    (2, 0, 0, 0, 0, 0, 0, 1, 0, 0)
    """

    def __init__(self, tally_kinds=("live", "preview"), explicit_cameras=0):

        # A list of allowed tally kinds, as in TallydConfig.tally_kinds.
        # For example, ("live", "preview").
        self.tally_kinds = tally_kinds

        assert "off" not in self.tally_kinds
        assert 1 <= len(self.tally_kinds) <= 8

        # Map of int (camera number) to tally state.
        # Camera numbering starts at 1.
        self.tally = collections.defaultdict(TallyState)

        # List of functions that we call after set_tally changes a tally
        # state. This is how clients hook in. Observers have a function
        # signature (camera, old_state, new_state) -> None.
        self.observers = []

    def register_observer(self, func):
        assert func not in self.observers

        self.observers.append(func)

    def set_max_camera(self, camera: int):
        # Explicitly sets the max camera ID. This only matters if the max ID
        # of cameras that have had tally set is less than the camera ID passed
        # to this function.
        #
        # For example, if cameras 1, 3, 5 have had tally set, then
        # get_all_numeric_tally will return a 5-element tuple. If this function
        # is called with camera=9, then calling get_all_numeric_tally will
        # return a 9-element tuple. However, if this function is called with
        # camera=4, get_all_numeric_tally will still return 5 elements.

        if camera not in self.tally:
            self.tally[camera] = TallyState()

    def set_tally(self, camera: int, kind: str):
        assert camera >= 1
        assert kind == "off" or kind in self.tally_kinds

        old_state = self.tally[camera]

        if kind == "off":
            new_state = TallyState(is_on=False)
        else:
            new_state = TallyState(is_on=True, kind=kind)

        self.tally[camera] = new_state

        if old_state != new_state:

            for observer in self.observers:
                observer(camera, old_state, new_state)

    def state_to_numeric_tally(self, state):
        if not state.is_on:
            return 0

        return self.tally_kinds.index(state.kind) + 1

    def get_numeric_tally(self, camera):
        assert camera >= 1

        state = self.tally[camera]
        return self.state_to_numeric_tally(state)

    def get_all_numeric_tally(self):
        max_camera = max(self.tally.keys())

        return tuple(self.get_numeric_tally(camera)
                     for camera in range(1, max_camera + 1))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
