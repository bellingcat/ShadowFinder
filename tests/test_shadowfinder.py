from datetime import datetime

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


def _gen_simple_finder_local_time():
    object_height = 6
    shadow_length = 3.2
    date_time = datetime.now()

    return ShadowFinder(
        object_height=object_height,
        shadow_length=shadow_length,
        date_time=date_time,
        time_format="local",
    )


def test_creation_with_valid_arguments_local_time_format_should_pass():
    _gen_simple_finder_local_time()


def test_find_shadows_with_local_time_format():
    finder = _gen_simple_finder_local_time()
    finder.find_shadows()
