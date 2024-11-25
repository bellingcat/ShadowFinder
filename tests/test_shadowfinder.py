from datetime import datetime, timedelta


from shadowfinder import ShadowFinder


def test_creation_with_valid_arguments_should_pass():
    """Baseline test to assert that we can create an instance of ShadowFinder with only object height, shadow length,
    and a datetime object."""
    # GIVEN
    object_height = 6
    shadow_length = 3.2
    date_time = datetime.now()

    # WHEN / THEN
    ShadowFinder(
        object_height=object_height, shadow_length=shadow_length, date_time=date_time
    )

def test_find_multiple_shadows():
    """Baseline test to assert that we can create an instance of ShadowFinder with only object height, shadow length,
    and a datetime object."""
    # GIVEN
    object_heights = [6,6,6,6]
    shadow_lengths = [3.2,3.0,2.9,2.8]
    time_offsets = range(4)
    timestamps = [datetime.now()+timedelta(hours=f) for f in time_offsets]

    shadow_finder = ShadowFinder()
    # WHEN / THEN
    figure = shadow_finder.find_multiple_shadows(object_heights=object_heights, shadow_lengths=shadow_lengths, timestamps=timestamps)
