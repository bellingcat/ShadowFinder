from datetime import datetime

from shadowfinder import ShadowFinder


def _validate_args(
    object_height: float,
    shadow_length: float,
    date_time: datetime,
) -> None:
    """
    Validate the text search CLI arguments, raises an error if the arguments are invalid.
    """
    if not object_height:
        raise ValueError("Object height cannot be empty")
    if not shadow_length:
        raise ValueError("Shadow length cannot be empty")
    if not date_time:
        raise ValueError("Date time cannot be empty")


def _validate_args_sun(
    sun_altitude_angle: float,
    date_time: datetime,
) -> None:
    """
    Validate the text search CLI arguments, raises an error if the arguments are invalid.
    """
    if not sun_altitude_angle:
        raise ValueError("Sun altitude angle cannot be empty")
    if not date_time:
        raise ValueError("Date time cannot be empty")


class ShadowFinderCli:

    @staticmethod
    def find(
        object_height: float,
        shadow_length: float,
        date: str,
        time: str,
        time_format: str = "utc",
    ) -> None:
        """
        Find the shadow length of an object given its height and the date and time.
        :param object_height: Height of the object in arbitrary units
        :param shadow_length: Length of the shadow in arbitrary units
        :param date: Date in the format YYYY-MM-DD
        :param time: UTC Time in the format HH:MM:SS
        """

        try:
            date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            raise ValueError(f"Invalid argument type or format: {e}")
        _validate_args(object_height, shadow_length, date_time)

        shadow_finder = ShadowFinder(
            object_height, shadow_length, date_time, time_format
        )
        shadow_finder.quick_find()

    @staticmethod
    def find_sun(
        sun_altitude_angle: float,
        date: str,
        time: str,
        time_format: str = "utc",
    ) -> None:
        """
        Locate a shadow based on the solar altitude angle and the date and time.
        :param sun_altitude_angle: Sun altitude angle in degrees
        :param date: Date in the format YYYY-MM-DD
        :param time: UTC Time in the format HH:MM:SS
        """

        try:
            date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            raise ValueError(f"Invalid argument type or format: {e}")
        _validate_args_sun(sun_altitude_angle, date_time)

        shadow_finder = ShadowFinder(
            date_time=date_time,
            time_format=time_format,
            sun_altitude_angle=sun_altitude_angle,
        )
        shadow_finder.quick_find()
