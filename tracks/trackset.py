"""This module contains the logic for all the different trackset types"""
from functools import partial
import hashlib
import inspect
import random
import uuid


class Track(object):

    def __init__(self, name, callable):
        self.name = name
        self.callable = callable

    def __call__(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    def __eq__(self, other):
        try:
            return self.name == other.name and self.callable == other.callable
        except AttributeError:
            return False

    @property
    def masked_name(self):
        return str(hashlib.md5(self.name.encode('utf-8')).hexdigest())[:7]


class BaseTrackSet(object):

    name = None
    weight = 100
    add_control_track = True

    def __init__(self, context=None, key=None):
        assert self.name is not None
        self.context = context
        self.key = key
        self._tracks = self._gather_tracks()

        if self.is_eligible:
            self.run_id = str(uuid.uuid4())
            self.track = self._tracks[self._track_index]
        else:
            self.run_id = self.track = None

    @property
    def _track_index(self):
        key = self.name + ':' + self.key
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % len(self._tracks)

    @staticmethod
    def noop(*args, **kwargs):
        return

    @property
    def masked_name(self):
        return str(hashlib.md5(self.name.encode('utf-8')).hexdigest())[:7]

    @property
    def key(self):
        return str(self._key if self._key is not None else random.random())

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def is_eligible(self):
        return True

    def __call__(self, *args, **kwargs):
        if self.track is not None:
            return self.track.callable(*args, **kwargs)
        else:
            return self.noop(*args, **kwargs)


class SimpleTrackSet(BaseTrackSet):

    def _gather_tracks(self):
        tracks = []

        if self.add_control_track:
            tracks.append(Track('control', self.noop))

        tracks.extend(
            Track(method_name[:-6], method)  # [:-6] cuts off '_track'
            for method_name, method in inspect.getmembers(self, predicate=inspect.isroutine)
            if method_name.endswith('_track')
        )
        return tracks


class ParamTrackSet(BaseTrackSet):

    params = []

    def _gather_tracks(self):
        tracks = []

        if self.add_control_track:
            tracks.append(Track('control', self.noop))

        for param_dict in self.params:
            tracks.append(Track(self.track_name(**param_dict), partial(self.track, **param_dict)))

        return tracks


class MultiTrackSet(object):

    tracksets = []

    class NoopTrackSet(SimpleTrackSet):
        name = 'control'

    noop_trackset = NoopTrackSet()

    def __init__(self, tracksets=None, context=None, key=None):
        self.tracksets = self.tracksets or tracksets
        self.context = context
        self.key = key

        weighted_trackset_list = []
        for trackset in self.tracksets:
            candidate = trackset(self.context, self.key)
            if candidate.is_eligible:
                weighted_trackset_list.extend([candidate] * trackset.weight)

        if weighted_trackset_list:
            self.is_eligible = True
            key = self.name + ':' + self.key
            index = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % len(weighted_trackset_list)
            self.trackset = weighted_trackset_list[index]
            self.track = self.trackset.track
            self.run_id = self.trackset.run_id
        else:
            self.is_eligible = False
            self.trackset = self.track = self.run_id = None

    @staticmethod
    def noop(*args, **kwargs):
        return

    @property
    def name(self):
        return '/'.join(trackset.name for trackset in self.tracksets)

    @property
    def key(self):
        return str(self._key if self._key is not None else random.random())

    @key.setter
    def key(self, value):
        self._key = value

    def __call__(self, *args, **kwargs):
        if self.trackset is not None:
            return self.trackset(*args, **kwargs)
        else:
            return self.noop(*args, **kwargs)
