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
            "object_height": 10,
            "shadow_length": 8,
            "date_time": datetime(2024, 2, 29, 12, 0, 0),
        },
        {
            "object_height": 10,
            "shadow_length": 9,
            "date_time": datetime(2024, 2, 29, 15, 0, 0),
        },
    ]
    num_cores = 2

    # WHEN
    normalized_output = multi_shadow_find(dict_list, num_cores)

    # THEN
    assert isinstance(normalized_output, np.ndarray)
    finder = ShadowFinder()
    finder.load_timezone_grid()
    assert normalized_output.shape == finder.lats.shape
