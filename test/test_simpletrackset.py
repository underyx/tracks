"""Unit tests for SimpleTrackSet"""
try:
    from itertools import zip_longest
except ImportError:  # Python 2
    from itertools import izip_longest as zip_longest

import tracks
from tracks.trackset import Track

from hypothesis import given, strategies
import pytest


@pytest.yield_fixture
def trackset_class():
    class FooBarTrackSet(tracks.SimpleTrackSet):
        name = 'foobar'

        def foo_track(self):
            pass

        def bar_track(self):
            pass

    yield FooBarTrackSet


@pytest.yield_fixture
def trackset(trackset_class):
    yield trackset_class()


def test_gather_tracks(trackset):
    expected_tracks = [
        Track('control', trackset.noop),
        Track('bar', trackset.bar_track),
        Track('foo', trackset.foo_track),
    ]
    for actual, expected in zip_longest(trackset._gather_tracks(), expected_tracks):
        assert actual == expected


def test_gather_no_control_tracks(trackset_class):
    trackset_class.add_control_track = False
    trackset = trackset_class()
    expected_tracks = [
        Track('bar', trackset.bar_track),
        Track('foo', trackset.foo_track),
    ]
    for actual, expected in zip_longest(trackset._gather_tracks(), expected_tracks):
        assert actual == expected


def test_is_eligible(trackset):
    assert trackset.is_eligible is True


def test_name(trackset):
    assert trackset.track.name in {'foo', 'bar', 'control'}


@pytest.mark.parametrize(
    'keys',
    [
        [1] * 1000,
        ['whee'] * 1000,
        [['whee']] * 1000,
        [{'thing': 'whee'}] * 1000,
    ],
    ids=lambda keys: type(keys[0]).__name__,
)
def test_same_track_index(trackset_class, keys):
    assert len({trackset_class(key=key)._track_index for key in keys}) == 1


@pytest.mark.parametrize(
    'keys', [
        [None] * 1000,
        [i for i in range(1000)],
        [str(i) for i in range(1000)],
        [[i] for i in range(1000)],
        [{'thing': i} for i in range(1000)],
    ],
    ids=lambda keys: type(keys[0]).__name__,
)
def test_different_track_index(trackset_class, keys):
    assert len({trackset_class(key=key)._track_index for key in keys}) > 1


def test_masked_name(trackset):
    assert trackset.masked_name == '3858f62'


@given(strategies.text())
def test_masked_name_deterministic(trackset_name):
    class FooTrackSet(tracks.SimpleTrackSet):
        name = trackset_name

    class BarTrackSet(tracks.SimpleTrackSet):
        name = trackset_name

    assert FooTrackSet().masked_name == BarTrackSet().masked_name
