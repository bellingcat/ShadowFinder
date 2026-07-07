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


def _utc_finder(**kwargs):
    return ShadowFinder(
        object_height=10,
        shadow_length=5,
        date_time=datetime(2024, 1, 1, 12, 0, 0),
        time_format="utc",
        **kwargs,
    )


def test_no_uncertainty_leaves_uncertainty_none():
    """Without any uncertainty inputs, the output is unchanged and no
    consistency surface is produced."""
    # GIVEN / WHEN
    finder = _utc_finder()
    finder.find_shadows()

    # THEN
    assert finder.location_uncertainty is None


def test_measurement_uncertainty_matches_propagation():
    """Measurement uncertainties widen the consistent region by the first-order
    propagated error (1 + r) * sqrt((dh/h)^2 + (ds/s)^2), where r is the cell's
    relative difference; the consistency surface is the distance of a perfect
    match (0) beyond that band."""
    # GIVEN height 10 +/- 1 and shadow 5 +/- 0.5
    finder = _utc_finder(object_height_uncertainty=1, shadow_length_uncertainty=0.5)

    # WHEN
    finder.find_shadows()

    # THEN
    sigma = np.sqrt((1 / 10) ** 2 + (0.5 / 5) ** 2)
    assert finder.location_uncertainty is not None
    finite = ~np.isnan(finder.location_likelihoods)
    r = finder.location_likelihoods[finite]
    lower = r - (1 + r) * sigma
    upper = r + (1 + r) * sigma
    expected = np.where(lower > 0, lower, np.where(upper < 0, -upper, 0.0))
    assert np.allclose(finder.location_uncertainty[finite], expected)


def test_time_uncertainty_widens_but_excludes_terminator():
    """A time uncertainty widens the consistent region beyond the exact-match
    band, but does not flood the terminator: cells whose predicted shadow is
    always far from the observation stay strongly excluded."""
    # GIVEN only a time uncertainty of 30 minutes
    finder = _utc_finder(time_uncertainty=1800)

    # WHEN
    finder.find_shadows()

    # THEN
    assert finder.location_uncertainty is not None
    consistent = finder.location_uncertainty == 0
    exact_match = np.abs(finder.location_likelihoods) < 1e-6
    daytime = ~np.isnan(finder.location_likelihoods)

    # widens the consistent region beyond the near-exact matches ...
    assert np.count_nonzero(consistent) > np.count_nonzero(exact_match)
    # ... but nowhere near the whole daytime hemisphere (no terminator flooding)
    assert np.count_nonzero(consistent) < 0.5 * np.count_nonzero(daytime)
    # ... and some cells are strongly excluded (large distance, not collapsed to ~0)
    assert np.nanmax(finder.location_uncertainty) > 1


def test_larger_uncertainty_widens_consistent_region():
    """A larger measurement uncertainty admits at least as many consistent
    cells."""

    def consistent_count(shadow_length_uncertainty):
        finder = _utc_finder(
            object_height_uncertainty=0.1,
            shadow_length_uncertainty=shadow_length_uncertainty,
        )
        finder.find_shadows()
        return int(np.count_nonzero(finder.location_uncertainty == 0))

    assert consistent_count(1.0) >= consistent_count(0.1)
