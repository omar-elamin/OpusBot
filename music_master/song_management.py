# Base class for a Circular Queue
class Queue:
    def __init__(self, n):
        """Circular static queue. Size determined by input n."""
        # pointer to the front of the Queue
        self._front = 0
        # pointer to the rear of the Queue
        self._rear = -1
        # variable for the the number of items in the queue
        self._size = 0
        # constant for the maximum size of the queue
        self._max_size = n
        # list placeholder for the queue
        self.queue = []
        # current item
        self.item = None

    # returns the item at the front of the queue; if empty returns None
    def __peek__(self):
        if self.is_empty():
            self.item = None
        else:
            self.item = self.queue[self._front]
        return self.item

    # boolean returns whether or not the queue is empty.
    def is_empty(self):
        return not bool(self._size)

    # boolean returns whether or not the queue is full.
    def is_full(self):
        return self._size == self._max_size

    # Adds an item to the queue
    def enqueue(self, new_item):
        if self.is_full():  # checks if the queue is full first, and raises an error if it is
            raise Exception('Attempted to enqueue to a full queue.')
        else:  # otherwise, it will add an item to the queue and update the pointer variables
            self.queue.append(new_item)
            self._rear += 1
            self._size += 1

    # Removes an item from the queue
    def dequeue(self):
        if self.is_empty():  # checks if the queue is empty first, and raises an error if it is
            raise Exception('Attempted to dequeue from an empty queue.')
        else:  # otherwise, it will remove an item from the queue and update the pointer variables
            self.item = self.queue.pop(self._front)
            self._rear -= 1
            self._size -= 1
        return self.item

    def clear_queue(self):  # empties queue
        self.queue.clear()


# Song object; stores all important information relating to a song
class Song:
    def __init__(self, title, artist, link, length, track, album=None, main_genre=None, other_genres: list = None,
                 producers: list = None, year_released=None, timestamp=None):
        """Skeleton wrapper for all songs, track object used to communicate with lavalink."""
        self.title = title
        self.artist = artist
        self.link = link
        self.length = length
        self.track = track
        self.album = album
        self.main_genre = main_genre
        self.other_genres = other_genres
        self.producers = producers
        self.year_released = year_released
        self.timestamp = timestamp

    def __repr__(self):
        """Format of a repr is the given format; Example: "Shape of You by Ed Sheeran on Divide"""
        return f'{self.title} by {self.artist} on {self.album}'


# Song Queue objects, inherits Queue object but incorporates adding and removing songs by Object
class SongQueue(Queue):
    def __init__(self, n):
        """A subclass of Queue that has special methods for adding and removing songs from the queue."""
        super().__init__(n)

    def add_song(self, song: Song):  # adds a song to the queue in the form of a song Object
        self.enqueue(song)

    def show(self):  # returns the song queue in the from of a list of Song objects
        return self.queue

    def remove_song(self,
                    song_or_index):  # removes a song from the queue in the form of a song Object or an index position
        if isinstance(song_or_index, Song):
            for song in self.queue:
                if song == Song:
                    return self.queue.remove(Song)
        else:
            return self.queue.pop(song_or_index)
