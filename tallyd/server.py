from dataclasses import dataclass
import asyncio
import json


@dataclass
class TallydControlClient():
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    subscribed: bool = False


@dataclass
class TallydClientClient():
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter


class TallydControlInterface():
    def __init__(self, state_manager):
        self.clients = []
        self.state_manager = state_manager

        self.event = asyncio.Event()
        self.last_change = None

        self.state_manager.register_observer(
            self._observer)

    def _observer(self, camera, old_state, new_state):
        self.last_change = {
            "camera": camera,
            "old_state": old_state,
            "new_state": new_state
        }

        self.event.set()

    async def _send_change_notifications(self):
        while True:
            await self.event.wait()

            for client in self.clients:
                if not client.subscribed:
                    continue

                old = self.last_change["old_state"]
                new = self.last_change["new_state"]

                client.writer.write(
                    json.dumps(
                        {"change": {
                            "camera": self.last_change["camera"],
                            "old": "off" if not old.is_on else old.kind,
                            "new": "off" if not new.is_on else new.kind
                        }}
                    ).encode() + b"\n"
                )

            self.event.clear()

    async def accept_client(self, reader, writer):
        client = TallydControlClient(reader, writer)
        self.clients.append(client)

        while not (writer.is_closing()):
            try:
                command = await reader.readline()
                command = json.loads(command.decode())

                assert "cmd" in command

                result = "ok"

                if command["cmd"] == "subscribe":
                    client.subscribed = True

                elif command["cmd"] == "set":
                    assert "camera" in command
                    assert "kind" in command

                    self.state_manager.set_tally(
                        command["camera"], command["kind"])

                elif command["cmd"] == "get":
                    assert "camera" in command

                    result = self.state_manager.tally[
                        command["camera"]]

                    result = "off" if not result.is_on else result.kind

                elif command["cmd"] == "quit":
                    writer.close()
                    break

            except AssertionError:
                result = "error"

            except json.decoder.JSONDecodeError:
                result = "error"

            writer.write(
                json.dumps({"result": result}).encode() +
                b"\n")

        self.clients.remove(client)

    async def start(self, port, loop):
        notify = loop.create_task(self._send_change_notifications())
        serve = asyncio.start_server(
            client_connected_cb=self.accept_client,
            loop=loop,
            port=port)

        await asyncio.gather(notify, serve)


class TallydClientInterface():
    def __init__(self, state_manager):
        self.clients = []
        self.state_manager = state_manager

        self.event = asyncio.Event()
        self.state_manager.register_observer(
            lambda *_: self.event.set())

    def _tally_bytes(self):
        tally = self.state_manager.get_all_numeric_tally()
        tally_bytes = [0x02] + [
            1 << (t - 1) if t else 0 for t in tally
        ] + [0xa]
        return bytes(tally_bytes)

    async def _send_change_notifications(self):
        while True:
            await self.event.wait()

            tally_bytes = self._tally_bytes()
            for client in self.clients:
                client.writer.write(tally_bytes)

            self.event.clear()

    async def accept_client(self, reader, writer):
        client = TallydClientClient(reader, writer)
        self.clients.append(client)

        while not (writer.is_closing()):
            await reader.readline()
            writer.write(self._tally_bytes())

        self.clients.remove(client)

    async def start(self, port, loop):
        notify = loop.create_task(self._send_change_notifications())
        serve = asyncio.start_server(
            client_connected_cb=self.accept_client,
            loop=loop,
            port=port)

        await asyncio.gather(notify, serve)
