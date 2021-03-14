import json
import re
import struct
from base64 import b64decode
from io import BytesIO
from urllib.parse import quote

from cogs.music import song_management


# Reads a json file in the /utils/ directory and returns a dictionary
def read_json(file_name):
    with open(f'utils/{file_name}.json', 'r') as file:
        data = json.load(file)
    return data


# Reads a dictionary to a json file with a given name in the /utils/ directory
def write_json(file_name, data):
    with open(f'utils/{file_name}.json', 'w') as file:
        json.dump(data, file, indent=4)


#  checks if a guild has a defined dj role.
def has_dj_role(guild):
    try:
        read_json('djroles')[str(guild.id)]
    except KeyError:
        return False
    else:
        return True


# returns the value given the key of an item in the config.json file
def config_entry(entry):
    return read_json('config')[entry]


# returns the prefix of the bot in a given guild (provided within the message object).
def get_prefix(bot, message):
    prefixes = read_json('prefixes')
    return prefixes[str(message.guild.id)]


def track_from_utf(track_utf):  # Reads data from the Websocket connection in UTF and converts it to a dictionary that
    # will fit in a Song Object.
    reader = BytesIO(b64decode(track_utf))

    def utf_read():
        res, = struct.unpack('>H', reader.read(2))
        return reader.read(res)

    def bool_read():
        res, = struct.unpack('B', reader.read(1))
        return res != 0

    def read_long():
        res, = struct.unpack('>Q', reader.read(8))
        return res

    title = utf_read().decode(errors='ignore')
    author = utf_read().decode()
    length = read_long()
    identifier = utf_read().decode()
    is_stream = bool_read()
    url = None
    if bool_read():
        url = utf_read().decode()

    track = {
        'track': track_utf,
        'info': {
            'title': title,
            'author': author,
            'length': length,
            'identifier': identifier,
            'isStream': is_stream,
            'uri': url,
            'isSeekable': not is_stream
        }
    }
    return song_management.Song(title, author, url, length, track)


async def query_to_song(query: str, player, query_site='yt'):  # Converts a query (Search or URL) to a Song object.
    playlist = False
    song = False
    url_rx = re.compile(r'https?://(?:www\.)?.+')  # regex object to check if a string is a URL

    if re.match(url_rx, query):
        query_type = 'url'
    else:
        query_type = 'search'

    if query_type == 'search':  # if the string is not a url, consider it a search query; defaults to YouTube
        if query_site == 'yt':
            query = f'ytsearch:{query}'

    hit = f'http://{player.node.host}:{player.node.port}/loadtracks?identifier={quote(query)}'  # Send query to lavalink
    headers = {
        "Authorization": player.node.password
    }

    async def get_song_info(to_hit, packet_headers):  # Receive response from Lavalink and make sense of it
        async with player.node.session.get(to_hit, headers=packet_headers) as res:
            if res.status == 200:
                return await res.json()

            if res.status == 401 or res.status == 403:
                raise PermissionError

            return []

    player_info = await get_song_info(hit, headers)  # converts response object into a dictionary

    if player_info[
        "loadType"] != "PLAYLIST_LOADED":  # if the type of response is a Track, output a single song as appt.
        song = True
        track = player_info['tracks'][0]
        song_name = track['info']['title']
        song_artist = track['info']['author']
        URL = track['info']['uri']
        length = track['info']['length']

    else:  # if it's a playlist, edit boolean and output a list of Songs
        playlist = True

    if playlist:
        songs = []
        for temp_track in player_info['info']['tracks']:
            temp_track_name = temp_track['info']['title']
            temp_track_artist = temp_track['info']['author']
            temp_track_URL = temp_track['info']['uri']
            temp_track_length = temp_track['info']['length']
            songs.append(
                song_management.Song(temp_track_name, temp_track_artist, temp_track_URL, temp_track_length, temp_track))

        return songs
    elif song:
        return song_management.Song(song_name, song_artist, URL, length, track)
