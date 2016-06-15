Tracks: Simple A/B testing of your backend
==========================================

Have you ever wanted to A/B test multiple code paths on your backend? Consider
the following: management wants you to cut down on server costs. You come to
terms with the fact that you really don't need a 128 GB memory 32 core beast
for your coconut store — but how low can you go? Let's test how a slower
coconut catalog page affects conversion! (First, without ``tracks``.)

.. code-block:: python

    response = render_coconut_catalog()
    test_value = random.random()
    if test_value < (1 / 3):
        # control group
        sleep_sec = 0
    elif test_value < (2 / 3):
        sleep_sec = 0.5
    else:
        sleep_sec = 2
    time.sleep(sleep_sec)
    cur.execute('INSERT INTO test_runs (user_id, variant) VALUES (%s, %s)', user_id, sleep_sec)
    return response

Now, this kinda works, but it's already a bit messy and can easily get out of
hand if you consider that right now:

 - The thing you test is really, really simple
 - You don't lock a user's version to make sure they always get the same test
   variant, making your data more mushy with each page load.
 - You don't exclude your most important users from testing to avoid hurting
   conversion among coconut addicts in your initial test run. (Of course you
   will need to include them later to make an informed decision.)
 - You already have a few more ideas about things you want to A/B test. Maybe
   a hundred.
 - You can add another 5 engineers to the project and they will probably each
   implement these tests slightly differently, and that's no good.

Enter ``tracks``. First we define our variants:

.. code-block:: python

    class DelayTracks(tracks.TrackSet):

        @staticmethod
        def short_track():
            time.sleep(0.5)

        @staticmethod
        def long_track():
            time.sleep(2)

And to use it:

.. code-block:: python

    response = render_coconut_catalog()
    with DelayTracks() as track:
        track()
        cur.execute('INSERT INTO test_runs (user_id, variant) VALUES (%s, %s)', user_id, track.name)
    return response

Already a bit nicer, but look what happens if we go through the list of
problems above one by one. Firstly, we can easily make the tests more complex:

.. code-block:: python

    class PricingTracks(tracks.TrackSet):

        @staticmethod
        def expensive_track(response):
            for coconut in response['coconuts']:
                coconut['price'] += 1

        @staticmethod
        def cheap_track(response):
            for coconut in response['coconuts']:
                coconut['price'] -= 1

Didn't get that much worse, now did it? Let's take it even further with more
variants:

.. code-block:: python

    class PricingTracks(tracks.ParamTrackSet):

        params = [{'price_delta': n} for n in range(-5, 6)]
        add_control_track = False  # {'price_delta': 0} is our control group

        @staticmethod
        def track_name(price_delta):
            return 'price_adjusted_by_{0}'.format(price_delta)

        @staticmethod
        def track(response, price_delta):
            for coconut in response['coconuts']:
                coconut['price'] += price_delta

Tons of tests! Let's move on to the second bullet point. How do we lock the
variant served to users? Just change your usage to pass a user key to tracks:


.. code-block:: python

    response = render_coconut_catalog()
    with DelayTracks(key=user_id) as track:
        track()
        cur.execute('INSERT INTO test_runs (user_id, variant) VALUES (%s, %s)', user_id, track.name)
    return response

The key will be serialized to a string and the variant to use will be derived
from that string. The key of course can be anything; in most cases it might be
the user ID, but you could use a combination of the user's country and the
article ID for instance. (Not sure why you would want this specific example,
but you get the point.)

So, with that solved, list item #3, here we come! What if we're worried about
our top customers being mad at us for testing things on them? Easy peasy.

.. code-block:: python

    class DelayTracks(tracks.TrackSet):

        @property
        def is_eligible(self):
            return not self.context['user']['is_vip']

        # code of variants trimmed

    response = render_coconut_catalog()
    with DelayTracks(context={'user': user_dict}) as track:
        track()  # will always be control for VIPs (even with `add_control_group = False`)
        if track.is_eligible:
            cur.execute('INSERT INTO test_runs (user_id, variant) VALUES (%s, %s)', (user_id, track.name))
    return response

And finally, let's try running the delay and pricing tests at the same time!

.. code-block:: python

    tracksets = [DelayTracks, PricingTracks]

    response = render_coconut_catalog()
    with tracks.MultiTrackSet(tracksets, key=user_id) as multitrack:
        multitrack()
        cur.execute(
            'INSERT INTO test_runs (user_id, test, variant) VALUES (%s, %s)',
            (user_id, multitrack.trackset.name, multitrack.track.name),
        )
    return response

So, with this, ``tracks`` will gather all tests the user is eligible for, and
choose one of them based on the given key. We could also set
``DelayTracks.weight`` to 1000 to make that one ten times as likely to be used
as the pricing one (the default weight is 100.)

We got pretty far with just a few lines of code, didn't we?
