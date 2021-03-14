import sys

from cogs.events import EndOfQueue, TrackEnded
from music_master.Web.WebSocket import Node
from music_master.song_management import SongQueue, Song


# Player class, each server has it's own player in order to manage simultaneous playing in multiple servers
class Player:
    def __init__(self, guild_id):
        self.guild_id = guild_id  # the ID of the server the Player belongs to.
        self.queue = SongQueue(sys.maxsize)  # Initializes a SongQueue with an arbitrarily large size
        self.channel_id = None  # Initializes the ID of the channel the bot is connected to in the respective server
        self.current = None  # The current song being played
        self.repeat = False  # Boolean whether the player should loop the song
        self.paused = False  # Boolean whether the player is paused
        self.volume = 100  # Volume value
        self.node = Node(host='localhost', port=8888, password="Lcm44eWXJ4CQPGGa",
                         player=self)  # Initializes the Node connection
        # with Lavalink

    @property
    def is_connected(self):  # property to check whether the player is connected to a channel
        return self.channel_id is not None

    @property
    def is_playing(self):  # property that returns a boolean that represents if the player is actively playing
        return self.current and self.is_connected

    async def stop(self):  # Stops the player; clears the queue and sends an instruction to Lavalink.
        self.queue.clear_queue()
        self.current = None
        await self.node.send(op='stop', guildId=str(self.guild_id))

    async def connect_to(self, guild_id: int, channel_id: str, bot):  # method to connect the player to a channel
        ws = bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        self.channel_id = channel_id

    def add_song(self, song: Song):  # method to add a song to the queue
        self.queue.add_song(song)

    async def play(self, song: Song = None, start_time: int = 0):  # method to play a song
        # checks if the player loop is on; if it is it will simply add the current song to the queue to be repeated
        if self.repeat and self.current:
            self.queue.enqueue(self.current)
        self.paused = False

        if not song:  # checks if a song is provided
            if self.queue.is_empty():  # if a song is not provided and the queue is empty the player is stopped
                print(self.queue.show())
                await self.stop()
                await self.node.invoke_event(EndOfQueue(self))
                return

            # if a song is not provided and the queue is not empty the player will play the next song in the queue
            song = self.queue.dequeue()

        options = {}

        # if a start time was provided, the input start time is validated and inserted in to the options dictionary
        if start_time:
            if 0 > start_time > song.length:
                raise ValueError('Invalid start time')
            options['startTime'] = start_time

        self.current = song  # Currently playing song variable is updated
        # An instruction is sent to Lavalink with the command "play", the current guild id, the track to play and any
        # other options specified by the user
        await self.node.send(op='play', guildId=str(self.guild_id), track=str(song.track), **options)

    async def handle_event(self, event):
        if isinstance(event, TrackEnded) and event.reason == 'FINISHED':
            await self.play()


class PlayerManager:  # The player manager; stores all players by guild id in a dictionary
    def __init__(self):
        self.players = {}

    def add_player(self, player: Player):  # method to add an existing player to the player manager
        self.players[str(player.guild_id)] = player
        return self.players[str(player.guild_id)]

    def new_player(self, guild_id):  # method to create a new player in the player manager
        self.players[str(guild_id)] = Player(guild_id)
        return self.players[str(guild_id)]

    def get_player(self, guild_id):  # method to retrieve a player from the player manager
        return self.players[str(guild_id)]
