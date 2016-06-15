"""Integration tests, taken mostly from the README examples"""
from collections import Counter
import random

import tracks


def test_pricing_tracks():
    class PricingTracks(tracks.SimpleTrackSet):
        name = 'pricing'

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

    track_names = set()
    for _ in range(1000):
        response = {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        track = PricingTracks()
        track(response)
        if track.track.name == 'cheap':
            assert set(coconut['price'] for coconut in response['coconuts']) == {49.0, 19.0}
        elif track.track.name == 'control':
            assert set(coconut['price'] for coconut in response['coconuts']) == {50.0, 20.0}
        elif track.track.name == 'expensive':
            assert set(coconut['price'] for coconut in response['coconuts']) == {51.0, 21.0}
        else:
            assert False, 'got unexpected track name {0}'.format(track.track.name)
        track_names.add(track.track.name)

    assert track_names == {'cheap', 'control', 'expensive'}


def test_pricing_param_tracks():
    class PricingTracks(tracks.ParamTrackSet):
        name = 'pricing'

        params = [{'price_delta': n} for n in range(-2, 3)]
        add_control_track = False  # {'price_delta': 0} is our control group

        @staticmethod
        def track_name(price_delta):
            return 'price_adjusted_by_{0}'.format(price_delta)

        @staticmethod
        def track(response, price_delta):
            for coconut in response['coconuts']:
                coconut['price'] += price_delta

    track_names = set()
    for _ in range(1000):
        response = {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        track = PricingTracks()
        track(response)
        if track.track.name == 'price_adjusted_by_-2':
            assert set(coconut['price'] for coconut in response['coconuts']) == {48.0, 18.0}
        elif track.track.name == 'price_adjusted_by_-1':
            assert set(coconut['price'] for coconut in response['coconuts']) == {49.0, 19.0}
        elif track.track.name == 'price_adjusted_by_0':
            assert set(coconut['price'] for coconut in response['coconuts']) == {50.0, 20.0}
        elif track.track.name == 'price_adjusted_by_1':
            assert set(coconut['price'] for coconut in response['coconuts']) == {51.0, 21.0}
        elif track.track.name == 'price_adjusted_by_2':
            assert set(coconut['price'] for coconut in response['coconuts']) == {52.0, 22.0}
        else:
            assert False, 'got unexpected track name {0}'.format(track.track.name)
        track_names.add(track.track.name)

    assert track_names == {
        'price_adjusted_by_-2',
        'price_adjusted_by_-1',
        'price_adjusted_by_0',
        'price_adjusted_by_1',
        'price_adjusted_by_2',
    }


def test_pricing_tracks_with_keys():
    class PricingTracks(tracks.SimpleTrackSet):
        name = 'pricing'

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

    user_prices = {}
    for _ in range(1000):
        response = {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        user_id = random.randint(0, 10)
        track = PricingTracks(key=user_id)
        track(response)
        if user_id not in user_prices:
            user_prices[user_id] = set(coconut['price'] for coconut in response['coconuts'])
        assert user_prices[user_id] == set(coconut['price'] for coconut in response['coconuts'])


def test_pricing_tracks_with_vips():
    class PricingTracks(tracks.SimpleTrackSet):
        name = 'pricing'

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

        @property
        def is_eligible(self):
            return not self.context['user']['is_vip']

    users = [{'name': 'Jerry', 'is_vip': False}, {'name': 'Ron', 'is_vip': True}]
    track_names = set()
    for _ in range(1000):
        response = {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        user = random.choice(users)
        track = PricingTracks(context={'user': user})
        track(response)
        if user['name'] == 'Ron':
            assert track.is_eligible is False
            assert response == {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        else:
            track_names.add(track.track.name)

    assert track_names == {'cheap', 'control', 'expensive'}


def test_multitrackset():
    class PricingTracks(tracks.SimpleTrackSet):
        name = 'pricing'

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

    class SuperNameTracks(tracks.SimpleTrackSet):
        name = 'super_name'

        @staticmethod
        def changed_name_track(response):
            for coconut in response['coconuts']:
                coconut['name'] = 'Super ' + coconut['name']

    trackset_track_names = set()
    for _ in range(1000):
        response = {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        track = tracks.MultiTrackSet([PricingTracks, SuperNameTracks])
        track(response)
        trackset_track_name = (track.trackset.name, track.track.name)
        if trackset_track_name == ('pricing', 'cheap'):
            assert set(coconut['price'] for coconut in response['coconuts']) == {49.0, 19.0}
        elif trackset_track_name == ('pricing', 'control'):
            assert set(coconut['price'] for coconut in response['coconuts']) == {50.0, 20.0}
        elif trackset_track_name == ('pricing', 'expensive'):
            assert set(coconut['price'] for coconut in response['coconuts']) == {51.0, 21.0}
        elif trackset_track_name == ('super_name', 'changed_name'):
            assert set(coconut['name'] for coconut in response['coconuts']) == {'Super Cpt. Coco', 'Super Lt. Coco'}
        elif trackset_track_name == ('super_name', 'control'):
            assert set(coconut['name'] for coconut in response['coconuts']) == {'Cpt. Coco', 'Lt. Coco'}
        trackset_track_names.add(trackset_track_name)

    assert trackset_track_names == {
        ('pricing', 'cheap'),
        ('pricing', 'control'),
        ('pricing', 'expensive'),
        ('super_name', 'changed_name'),
        ('super_name', 'control'),
    }


def test_multitrackset_weights():
    class PricingTracks(tracks.SimpleTrackSet):
        name = 'pricing'
        weight = 9

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

    class SuperNameTracks(tracks.SimpleTrackSet):
        name = 'super_name'
        weight = 1

        @staticmethod
        def changed_name_track(response):
            for coconut in response['coconuts']:
                coconut['name'] = 'Super ' + coconut['name']

    trackset_counts = Counter()
    for _ in range(1000):
        track = tracks.MultiTrackSet([PricingTracks, SuperNameTracks])
        trackset_counts[track.trackset.name] += 1

    assert 850 < trackset_counts['pricing'] < 950
    assert 50 < trackset_counts['super_name'] < 150


def test_multitrackset_with_vips():
    class PricingTracks(tracks.SimpleTrackSet):
        name = 'pricing'

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

        @property
        def is_eligible(self):
            return not self.context['user']['is_vip']

    class SuperNameTracks(tracks.SimpleTrackSet):
        name = 'super_name'

        @staticmethod
        def changed_name_track(response):
            for coconut in response['coconuts']:
                coconut['name'] = 'Super ' + coconut['name']

        @property
        def is_eligible(self):
            return not self.context['user']['is_vip']

    users = [{'name': 'Jerry', 'is_vip': False}, {'name': 'Ron', 'is_vip': True}]
    trackset_track_names = set()
    for _ in range(1000):
        response = {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        user = random.choice(users)
        track = tracks.MultiTrackSet([PricingTracks, SuperNameTracks], context={'user': user})
        track(response)
        if user['name'] == 'Ron':
            assert track.is_eligible is False
            assert response == {'coconuts': [{'name': 'Cpt. Coco', 'price': 50.0}, {'name': 'Lt. Coco', 'price': 20.0}]}
        else:
            trackset_track_names.add((track.trackset.name, track.track.name))

    assert trackset_track_names == {
        ('pricing', 'cheap'),
        ('pricing', 'control'),
        ('pricing', 'expensive'),
        ('super_name', 'changed_name'),
        ('super_name', 'control'),
    }
