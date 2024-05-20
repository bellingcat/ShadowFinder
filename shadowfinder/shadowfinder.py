import datetime
from pytz import timezone
import pandas as pd
from suncalc import get_position
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from timezonefinder import TimezoneFinder
import json


class ShadowFinder:
    def __init__(
        self, object_height=None, shadow_length=None, date_time=None, time_format="utc"
    ):

        self.set_details(object_height, shadow_length, date_time, time_format)

        self.lats = None
        self.lons = None
        self.shadow_lengths = None

        self.timezones = None
        self.tf = TimezoneFinder(in_memory=True)

        self.fig = None

        self.angular_resolution=0.5
        self.min_lat=-60
        self.max_lat=85
        self.min_lon=-180
        self.max_lon=180

    def set_details(self, object_height, shadow_length, date_time, time_format=None):
        self.object_height = object_height
        self.shadow_length = shadow_length
        self.date_time = date_time

        if time_format is not None:
            assert time_format in [
                "utc",
                "local",
            ], "time_format must be 'utc' or 'local'"
            self.time_format = time_format

    def quick_find(self):
        self.generate_timezone_grid()
        self.find_shadows()
        fig = self.plot_shadows()
        fig.savefig(
            f"shadow_finder_{self.date_time.strftime('%Y%m%d-%H%M%S')}-{self.time_format.title()}_{self.object_height}_{self.shadow_length}.png"
        )

    def generate_timezone_grid(self):
        lats = np.arange(self.min_lat, self.max_lat, self.angular_resolution)
        lons = np.arange(self.min_lon, self.max_lon, self.angular_resolution)

        self.lons, self.lats = np.meshgrid(lons, lats)

        # Create a pandas series of datetimes adjusted for each timezone
        self.timezones = np.array(
            [
                self.tf.timezone_at(lng=lon, lat=lat)
                for lat, lon in zip(self.lats.flatten(), self.lons.flatten())
            ]
        )

    def save_timezone_grid(self, filename="timezone_grid.json"):
        data = {
            "min_lat": self.min_lat,
            "max_lat": self.max_lat,
            "min_lon": self.min_lon,
            "max_lon": self.max_lon,
            "angular_resolution": self.angular_resolution,
            "timezones": self.timezones.tolist(),
        }

        json.dump(data, open(filename, "w"))

    def load_timezone_grid(self, filename="timezone_grid.json"):
        data = json.load(open(filename, "r"))
        
        self.min_lat = data["min_lat"]
        self.max_lat = data["max_lat"]
        self.min_lon = data["min_lon"]
        self.max_lon = data["max_lon"]
        self.angular_resolution = data["angular_resolution"]

        lats = np.arange(self.min_lat, self.max_lat, self.angular_resolution)
        lons = np.arange(self.min_lon, self.max_lon, self.angular_resolution)

        self.lons, self.lats = np.meshgrid(lons, lats)
        self.timezones = np.array(data["timezones"])

    def find_shadows(self):
        # Evaluate the sun's length at a grid of points on the Earth's surface

        if self.lats is None or self.lons is None or self.timezones is None:
            self.generate_timezone_grid()

        if self.time_format == "utc":
            valid_datetimes = self.date_time
            valid_lats = self.lats.flatten()
            valid_lons = self.lons.flatten()
        elif self.time_format == "local":
            datetimes = np.array(
                [
                    (
                        None
                        if tz is None
                        else self.date_time.replace(tzinfo=timezone(tz))
                        .astimezone(datetime.timezone.utc)
                        .timestamp()
                    )
                    for tz in self.timezones
                ]
            )

            # Create mask for invalid datetimes
            mask = np.array([dt is not None for dt in datetimes])

            # Only process the valid datetimes
            valid_datetimes = np.extract(mask, datetimes)
            valid_lons = np.extract(mask, self.lons.flatten())
            valid_lats = np.extract(mask, self.lats.flatten())

            # Convert the datetimes to pandas series of timestamps
            valid_datetimes = pd.to_datetime(valid_datetimes, unit="s", utc=True)

        pos_obj = get_position(valid_datetimes, valid_lons, valid_lats)

        valid_sun_altitudes = pos_obj["altitude"]  # in radians

        # Calculate the shadow length
        shadow_lengths = self.object_height / np.apply_along_axis(
            np.tan, 0, valid_sun_altitudes
        )

        # Replace points where the sun is below the horizon with nan
        shadow_lengths[valid_sun_altitudes <= 0] = np.nan

        # Show the relative difference between the calculated shadow length and the observed shadow length
        shadow_relative_length_difference = (
            shadow_lengths - self.shadow_length
        ) / self.shadow_length

        shadow_lengths = shadow_relative_length_difference

        if self.time_format == "utc":
            self.shadow_lengths = shadow_lengths
        elif self.time_format == "local":
            self.shadow_lengths = np.full(np.shape(mask), np.nan)
            np.place(self.shadow_lengths, mask, shadow_lengths)
        self.shadow_lengths = np.reshape(
            self.shadow_lengths, np.shape(self.lons), order="A"
        )

    def plot_shadows(
        self,
        figure_args={"figsize": (12, 6)},
        basemap_args={"projection": "cyl", "resolution": "c"},
    ):

        fig = plt.figure(**figure_args)

        # Add a simple map of the Earth
        m = Basemap(**basemap_args)
        m.drawcoastlines()
        m.drawcountries()

        # Deal with the map projection
        x, y = m(self.lons, self.lats)

        # Set the a color scale and only show the values between 0 and 0.2
        cmap = plt.cm.get_cmap("inferno_r")
        norm = colors.BoundaryNorm(np.arange(0, 0.2, 0.02), cmap.N)

        # Plot the data
        m.pcolormesh(x, y, np.abs(self.shadow_lengths), cmap=cmap, norm=norm, alpha=0.7)

        # plt.colorbar(label='Relative Shadow Length Difference')
        plt.title(
            f"Possible Locations at {self.date_time.strftime('%Y-%m-%d %H:%M:%S')} {self.time_format.title()}\n(object height: {self.object_height}, shadow length: {self.shadow_length})"
        )
        self.fig = fig
        return fig
