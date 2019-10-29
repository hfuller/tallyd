import asyncio
from tallyd.state import TallyStateManager
from tallyd.server import TallydControlInterface, TallydClientInterface


async def create_servers(config):
    loop = asyncio.get_event_loop()

    state = TallyStateManager()
    state.set_max_camera(config.initial_cameras)

    control_iface = TallydControlInterface(state)
    clients_iface = TallydClientInterface(state)

    control_server = control_iface.start(config.control_port, loop)
    clients_server = clients_iface.start(config.client_port, loop)

    await asyncio.gather(control_server, clients_server)
