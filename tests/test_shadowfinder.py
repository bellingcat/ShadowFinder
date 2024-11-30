import unittest
from datetime import datetime
import numpy as np
from shadowfinder import multi_shadow_find, ShadowFinder



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


def test_multi_shadow_find():
    """Test the multi_shadow_find function with multiple ShadowFinder instances."""
    # GIVEN
    dict_list = [
        {
            "object_height": 6,
            "shadow_length": 3.2,
            "date_time": datetime(2023, 10, 1, 12, 0, 0),
            "time_format": "utc"
        },
        {
            "object_height": 5,
            "shadow_length": 2.5,
            "date_time": datetime(2023, 10, 1, 12, 0, 0),
            "time_format": "utc"
        }
    ]
    num_cores = 2

    # WHEN
    normalized_output = multi_shadow_find(dict_list, num_cores)

    # THEN
    assert isinstance(normalized_output, np.ndarray)
    assert normalized_output.shape == ShadowFinder().lats.shape
    assert np.all(normalized_output >= 0)