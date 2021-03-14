import aiohttp

from cogs.events import NodeConnected, TrackEnded, ClosedWebSocket, LavalinkEvent
from music_master import song_management
from utils.functions import track_from_utf


class Node:
    def __init__(self, host, port, password, player):
        """Node object, represents a node connection to Lavalink."""
        self.player = player
        self.host = host
        self.port = port
        self.password = password
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30))
        self.hit = f'http://{self.host}:{self.port}/'  # resource locator for the web socket connection
        self.headers = {  # Headers to use in the packet sent
            "Authorization": self.password,
            "User-Id": '509406384106897428',
            "Num-Shards": '1'
        }

    # Method to invoke an event
    async def invoke_event(self, event: LavalinkEvent):  # Sends a Lavalink Event object to Lavalink
        async def main():
            async with aiohttp.ClientSession() as _:
                _ws = WebSocket(self, max_retries=1)  # Opens a web socket connection
                # EVENT HOOKS NEEDED HERE

        await main()

    async def send(self, **kwargs):  # sends an instruction to Lavalink
        async def main():
            async with aiohttp.ClientSession() as session:
                _ws = await session.ws_connect(self.hit, headers=self.headers)  # Opens a web socket connection
                opts = {}
                for arg in kwargs:  # Formats the options into a dictionary to send as an op instruction
                    opts[arg] = kwargs[arg]
                await _ws.send_json(opts)

        await main()


class WebSocket:
    def __init__(self, node: Node, max_retries=1):
        """Web socket object, used to communicate with the Lavalink jar."""
        self.node = node  # Takes in a node as a parameter
        self.session = node.session
        self._ws = None

        self.message_queue = song_management.Queue(10)  # Uses the Queue class already created to manage instruction
        # queues

        self.host = node.host
        self.port = node.port
        self.password = node.port
        self.max_retries = max_retries
        self.bot_id = 789490889009266720

    @property
    def connected(self):  # if the WebSocket is connected
        return self._ws and not self._ws.closed

    async def connect(self):  # asynchronous method to connect the Web Socket
        headers = {
            'Authorization': self.password,
            'User-Id': str(self.bot_id),
            'Num-Shards': '1'
        }

        try:
            # Creates a websocket connection with a 60 second heartbeat
            self._ws = await self.session.ws_connect(f'ws://{self.host}:{self.port}', headers=headers, heartbeat=60)
        except Exception as e:
            print(f'Error while establishing WebSocket connection: {e}')
        else:
            await self.node.invoke_event(NodeConnected(self.node))  # Dispatches an Event that the Node is connected

            if not self.message_queue.is_empty():
                for message in self.message_queue.queue:  # If any messages were attempted to be sent while the
                    # WebSocket wasn't connected, it will send them now.
                    await self.send(**message)

                self.message_queue.clear_queue()

    async def listen_ws(self):
        async for message in self._ws:
            print(f'Received message from WebSocket: {message.data}')

            if message.type == aiohttp.WSMsgType.ERROR:
                err = self._ws.exception()
                raise Exception(f'Error in WebSocket connection: {err}')

            elif message.type == aiohttp.WSMsgType.TEXT:
                op = message.data['op']
                if op == 'event':
                    await self.invoke_event(
                        message.data)  # Invokes events if the message received from the WebSocket is an event

    async def invoke_event(self, data):  # Dispatches an Event to the Node.

        event_type = data['type']

        if event_type == 'TrackEndEvent':
            track = track_from_utf(data['track']).track
            await self.node.invoke_event(TrackEnded(self.node.player, track, data['reason']))
        elif event_type == 'WebSocketClosedEvent':
            await self.node.invoke_event(ClosedWebSocket(self.node.player, data['code'], data['reason']))

    async def send(self, **opts):  # sends instructions to Lavalink through the WebSocket connection
        if self.connected:
            await self._ws.send_json(opts)
        else:
            self.message_queue.enqueue(opts)  # If the WebSocket isn't connected, the instruction is queued.
