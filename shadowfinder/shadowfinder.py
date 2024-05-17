import datetime
from pytz import timezone
import pandas as pd
from suncalc import get_position
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from timezonefinder import TimezoneFinder


class ShadowFinder:
    def __init__(self, object_height=None, shadow_length=None, date_time=None):
        self.object_height = object_height
        self.shadow_length = shadow_length
        self.date_time = date_time

        self.lats = None
        self.lons = None
        self.shadow_lengths = None

        self.timezones = None
        self.tf = TimezoneFinder(in_memory=True)

        self.fig = None

        # config options
        self.process_sea = False
    def set_details(self, object_height, shadow_length, date_time, process_sea=None):
        self.object_height = object_height
        self.shadow_length = shadow_length
        self.date_time = date_time

        if process_sea is not None:
            self.process_sea = process_sea
    def quick_find(self):
        self.generate_lat_lon_grid()
        self.find_shadows()
        fig = self.plot_shadows()
        fig.savefig(
            f"shadow_finder_{self.date_time.strftime('%Y%m%d-%H%M%S-%Z')}_{self.object_height}_{self.shadow_length}.png"
        )

    def generate_lat_lon_grid(self, angular_resolution=0.25):
        lats = np.arange(-60, 85, angular_resolution)
        lons = np.arange(-180, 180, angular_resolution)

        self.lons, self.lats = np.meshgrid(lons, lats)

        evaluate_timezones = self.tf.timezone_at if self.process_sea else self.tf.timezone_at_land

        # Create a pandas series of datetimes adjusted for each timezone
        self.timezones = np.array(
            [
                evaluate_timezones(lng=lon, lat=lat)
                for lat, lon in zip(self.lats.flatten(), self.lons.flatten())
            ]
        )

    def save_timezones(self, filename="timezones.npz"):
        np.savez(filename, lats=self.lats, lons=self.lons, timezones=self.timezones)

    def load_timezones(self, filename="timezones.npz"):
        with np.load(filename, allow_pickle=True) as data:
            self.lats = data["lats"]
            self.lons = data["lons"]
            self.timezones = data["timezones"]

    def find_shadows(self):
        # Evaluate the sun's length at a grid of points on the Earth's surface

        if self.lats is None or self.lons is None or self.timezones is None:
            self.generate_lat_lon_grid()

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
            f"Possible Locations at {self.date_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n(object height: {self.object_height}, shadow length: {self.shadow_length})"
        )
        self.fig = fig
        return fig
