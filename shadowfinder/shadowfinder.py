from suncalc import get_position
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap


class ShadowFinder:
    def __init__(self, object_height, shadow_length, date_time):
        self.object_height = object_height
        self.shadow_length = shadow_length
        self.date_time = date_time

        self.lats = None
        self.lons = None
        self.shadow_lengths = None

        self.fig = None

    def quick_find(self):
        self.generate_lat_lon_grid()
        self.find_shadows()
        fig = self.plot_shadows()
        fig.savefig(
            f"shadow_finder_{self.date_time.strftime('%Y%m%d-%H%M%S-%Z')}_{self.object_height}_{self.shadow_length}.png"
        )

    def generate_lat_lon_grid(self, angular_resolution=0.25):
        lats = np.arange(-90, 90, angular_resolution)
        lons = np.arange(-180, 180, angular_resolution)

        self.lons, self.lats = np.meshgrid(lons, lats)

    def find_shadows(self):
        # Evaluate the sun's length at a grid of points on the Earth's surface

        if self.lats is None or self.lons is None:
            self.generate_lat_lon_grid()

        pos_obj = get_position(self.date_time, self.lons, self.lats)
        # Calculate the shadow length
        shadow_lengths = self.object_height / np.apply_along_axis(
            np.tan, 0, sun_altitudes
        )

        # Replace points where the sun is below the horizon with nan
        shadow_lengths[sun_altitudes <= 0] = np.nan

        # Show the relative difference between the calculated shadow length and the observed shadow length
        shadow_relative_length_difference = (
            shadow_lengths - self.shadow_length
        ) / self.shadow_length

        self.shadow_lengths = shadow_relative_length_difference

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
