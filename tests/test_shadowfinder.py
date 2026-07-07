from datetime import datetime

import numpy as np

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


def test_timezone_masking_keeps_only_matching_timezone():
    """When a known timezone is supplied, every remaining (non-NaN) candidate
    cell must fall within that timezone; cells elsewhere are masked to NaN."""
    # GIVEN a midday-UTC winter time when the sun is up over Ukraine
    finder = ShadowFinder(
        object_height=6,
        shadow_length=3.2,
        date_time=datetime(2024, 1, 1, 12, 0, 0),
        time_format="utc",
        timezone="Europe/Kyiv",
    )

    # WHEN
    finder.find_shadows()

    # THEN
    timezone_grid = np.reshape(finder.timezones, np.shape(finder.lons), order="A")
    surviving = ~np.isnan(finder.location_likelihoods)
    assert surviving.any(), "expected some candidate cells in the timezone"
    assert np.all(timezone_grid[surviving] == "Europe/Kyiv")


def test_no_timezone_leaves_multiple_timezones():
    """Without a timezone mask, candidate cells span many timezones (baseline
    that proves the mask above is doing the filtering)."""
    # GIVEN the same setup but no timezone
    finder = ShadowFinder(
        object_height=6,
        shadow_length=3.2,
        date_time=datetime(2024, 1, 1, 12, 0, 0),
        time_format="utc",
    )

    # WHEN
    finder.find_shadows()

    # THEN
    timezone_grid = np.reshape(finder.timezones, np.shape(finder.lons), order="A")
    surviving = ~np.isnan(finder.location_likelihoods)
    assert len(np.unique(timezone_grid[surviving])) > 1


def test_set_details_preserves_timezone_on_partial_update():
    """Re-configuring only some details (e.g. the time) must not silently drop
    a previously set timezone mask, matching how the other optional inputs are
    preserved when passed as None."""
    # GIVEN a finder with a timezone mask
    finder = ShadowFinder(
        object_height=6,
        shadow_length=3.2,
        date_time=datetime(2024, 1, 1, 12, 0, 0),
        time_format="utc",
        timezone="Europe/Kyiv",
    )

    # WHEN only the date_time is updated
    finder.set_details(date_time=datetime(2024, 1, 1, 13, 0, 0))

    # THEN the timezone is retained
    assert finder.timezone == "Europe/Kyiv"


def test_empty_mask_warns(recwarn):
    """A timezone that leaves no candidate cells (misspelled, or in darkness)
    warns rather than silently returning a blank map."""
    # GIVEN a valid IANA timezone that is in night at this instant
    finder = ShadowFinder(
        object_height=6,
        shadow_length=3.2,
        date_time=datetime(2024, 1, 1, 12, 0, 0),
        time_format="utc",
        timezone="America/Anchorage",
    )

    # WHEN
    finder.find_shadows()

    # THEN the result is empty and a warning was emitted
    assert np.all(np.isnan(finder.location_likelihoods))
    assert any("No candidate locations remain" in str(w.message) for w in recwarn)
