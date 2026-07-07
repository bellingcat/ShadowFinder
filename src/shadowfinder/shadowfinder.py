from pytz import timezone, utc
import pandas as pd
from suncalc import get_position
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import DownloadWarning
from timezonefinder import TimezoneFinder
import json
from datetime import timedelta
from warnings import warn, filterwarnings
from math import radians


class ShadowFinder:
    def __init__(
        self,
        object_height=None,
        shadow_length=None,
        date_time=None,
        time_format="utc",
        sun_altitude_angle=None,
        object_height_uncertainty=None,
        shadow_length_uncertainty=None,
        sun_altitude_angle_uncertainty=None,
        time_uncertainty=None,
    ):
        self.set_details(
            date_time,
            object_height,
            shadow_length,
            time_format,
            sun_altitude_angle,
            object_height_uncertainty,
            shadow_length_uncertainty,
            sun_altitude_angle_uncertainty,
            time_uncertainty,
        )

        self.lats = None
        self.lons = None
        self.location_likelihoods = None
        self.location_uncertainty = None

        self.timezones = None
        self.tf = TimezoneFinder(in_memory=True)

        self.fig = None

        self.angular_resolution = 0.5
        self.min_lat = -60
        self.max_lat = 85
        self.min_lon = -180
        self.max_lon = 180

    def set_details(
        self,
        date_time,
        object_height=None,
        shadow_length=None,
        time_format=None,
        sun_altitude_angle=None,
        object_height_uncertainty=None,
        shadow_length_uncertainty=None,
        sun_altitude_angle_uncertainty=None,
        time_uncertainty=None,
    ):

        if date_time is not None and date_time.tzinfo is not None:
            warn(
                "date_time is expected to be timezone naive (i.e. tzinfo=None). Any timezone information will be ignored."
            )
            date_time = date_time.replace(tzinfo=None)
        self.date_time = date_time

        # Optional measurement/time uncertainties. When any are set, find_shadows
        # propagates them into a per-cell uncertainty band (self.location_sigmas)
        # instead of using the fixed default band width.
        self.object_height_uncertainty = object_height_uncertainty
        self.shadow_length_uncertainty = shadow_length_uncertainty
        self.sun_altitude_angle_uncertainty = sun_altitude_angle_uncertainty
        self.time_uncertainty = time_uncertainty

        if time_format is not None:
            assert time_format in [
                "utc",
                "local",
            ], "time_format must be 'utc' or 'local'"
            self.time_format = time_format

        # height and length must have the same None-ness
        # either height or angle must be set (but not both or neither)
        # fmt: off
        valid_input = (
            ((object_height is None) == (shadow_length is None)) and
            ((object_height is None) or (sun_altitude_angle is None))
        )
        # fmt: on
        if not valid_input:
            raise ValueError(
                "Please either set object_height and shadow_length or set sun_altitude_angle"
            )

        # If lengths are given, we clear the previous sun altitude angle
        # If sun altitude angle is given, we clear the previous lengths
        # If neither are given, we keep the previous values
        if object_height is not None:
            self.object_height = object_height
            self.shadow_length = shadow_length
            self.sun_altitude_angle = None
        elif sun_altitude_angle is not None:
            self.object_height = None
            self.shadow_length = None
            assert (
                0 < sun_altitude_angle <= 90
            ), "Sun altitude angle must be between 0 and 90 degrees"
            self.sun_altitude_angle = sun_altitude_angle
        else:
            # Lengths and angle are None and we use the same values as before
            pass

    def quick_find(self, timezone_grid="timezone_grid.json"):
        # try to load timezone grid from file, generate if not found
        try:
            self.load_timezone_grid(timezone_grid)
        except FileNotFoundError:
            self.generate_timezone_grid()

        self.find_shadows()
        fig = self.plot_shadows()

        if self.sun_altitude_angle is not None:
            file_name = f"shadow_finder_{self.date_time.strftime('%Y%m%d-%H%M%S')}-{self.time_format.title()}_{self.sun_altitude_angle}.png"
        else:
            file_name = f"shadow_finder_{self.date_time.strftime('%Y%m%d-%H%M%S')}-{self.time_format.title()}_{self.object_height}_{self.shadow_length}.png"

        fig.savefig(file_name)

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

    def _relative_difference(self, sun_altitudes):
        # Relative difference between the shadow implied by each cell's sun
        # altitude and the observed shadow (0 at a perfect match). Cells where
        # the sun is below the horizon are set to nan.
        if self.object_height is not None and self.shadow_length is not None:
            shadow_lengths = self.object_height / np.tan(sun_altitudes)
            shadow_lengths[sun_altitudes <= 0] = np.nan
            return (shadow_lengths - self.shadow_length) / self.shadow_length

        elif self.sun_altitude_angle is not None:
            differences = (sun_altitudes - radians(self.sun_altitude_angle)) / radians(
                self.sun_altitude_angle
            )
            differences[sun_altitudes <= 0] = np.nan
            return differences

        else:
            raise ValueError(
                "Either object height and shadow length or sun altitude angle needs to be set."
            )

    def _reshape_to_grid(self, values, mask):
        # Place the values computed for the valid cells back onto the full grid.
        if mask is None:
            grid = values
        else:
            grid = np.full(np.shape(mask), np.nan)
            np.place(grid, mask, values)
        return np.reshape(grid, np.shape(self.lons), order="A")

    def _measurement_relative_variance(self):
        # Combined relative variance from the measurement uncertainties, used as
        # the (location-independent) width of the acceptance band.
        variance = 0.0
        if self.object_height is not None and self.shadow_length is not None:
            if self.object_height_uncertainty:
                variance += (self.object_height_uncertainty / self.object_height) ** 2
            if self.shadow_length_uncertainty:
                variance += (self.shadow_length_uncertainty / self.shadow_length) ** 2
        elif self.sun_altitude_angle is not None:
            if self.sun_altitude_angle_uncertainty:
                # The radians conversion cancels in the ratio.
                variance += (
                    self.sun_altitude_angle_uncertainty / self.sun_altitude_angle
                ) ** 2
        return variance

    def find_shadows(self):
        # Evaluate the sun's position at a grid of points on the Earth's surface

        if self.lats is None or self.lons is None or self.timezones is None:
            self.generate_timezone_grid()

        if self.time_format == "utc":
            valid_datetimes = utc.localize(self.date_time)
            valid_lats = self.lats.flatten()
            valid_lons = self.lons.flatten()
            mask = None
        elif self.time_format == "local":
            datetimes = np.array(
                [
                    (
                        None
                        if tz is None
                        else timezone(tz)
                        .localize(self.date_time)
                        .astimezone(utc)
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

        def relative_difference_at(offset_seconds=0):
            # Relative-difference surface for the valid cells at date_time shifted
            # by offset_seconds (used to sweep the time-uncertainty band).
            datetimes = valid_datetimes
            if offset_seconds:
                datetimes = valid_datetimes + timedelta(seconds=offset_seconds)
            sun_altitudes = np.array(
                get_position(datetimes, valid_lons, valid_lats)["altitude"]
            )
            return self._relative_difference(sun_altitudes)

        location_likelihoods = relative_difference_at()

        # Propagate the measurement and/or time uncertainties into a per-cell
        # "consistency" surface: the distance from a perfect match (0) to the
        # range of relative differences the observation could plausibly take
        # given the uncertainties. A value of 0 means the cell is consistent
        # with the observation. Stays None (unchanged output) when no
        # uncertainty was supplied.
        location_uncertainty = None
        measurement_sigma = np.sqrt(self._measurement_relative_variance())

        if self.time_uncertainty:
            seconds = (
                self.time_uncertainty.total_seconds()
                if isinstance(self.time_uncertainty, timedelta)
                else float(self.time_uncertainty)
            )
            # Sweep the observation time by +/- its uncertainty. The relative
            # difference at each cell then spans a range rather than a single
            # value, evaluated with two extra global computations at t +/- dt
            # rather than re-meshing the whole globe over many moments (issue #4).
            r_minus = relative_difference_at(-seconds)
            r_plus = relative_difference_at(seconds)
            lower_difference = np.fmin(np.fmin(r_minus, location_likelihoods), r_plus)
            upper_difference = np.fmax(np.fmax(r_minus, location_likelihoods), r_plus)
        else:
            lower_difference = location_likelihoods
            upper_difference = location_likelihoods

        if self.time_uncertainty or measurement_sigma > 0:
            # Widen the plausible range by the measurement band (issue #3), then
            # measure how far a perfect match (0) sits outside that range. Cells
            # whose range spans 0 are consistent with the observation (0 here).
            lower_bound = lower_difference - measurement_sigma
            upper_bound = upper_difference + measurement_sigma
            gap = np.where(
                lower_bound > 0,
                lower_bound,
                np.where(upper_bound < 0, -upper_bound, 0.0),
            )
            # Keep cells where the sun is always below the horizon excluded.
            gap = np.where(np.isnan(lower_bound), np.nan, gap)
            location_uncertainty = self._reshape_to_grid(gap, mask)

        self.location_likelihoods = self._reshape_to_grid(location_likelihoods, mask)
        self.location_uncertainty = location_uncertainty

    def plot_shadows(
        self,
        figure_args={"figsize": (12, 6)},
        projection="PlateCarree",
        projection_args={},
    ):

        fig = plt.figure(**figure_args)

        # Set the a color scale and only show the values between 0 and 0.2

        # Create a custom LinearSegmented colormap
        cmap = colors.LinearSegmentedColormap.from_list(
            "custom_cmap",
            [
                # 0 is the peak likelihood, 1 is the low likelihood
                (0, (1, 1, 0.75, 1)),  # Light Yellow - peak likelihood
                (0.05, (1, 1, 0, 1)),  # Yellow - high likelihood
                (0.2, (1, 0.5, 0, 1)),  # Orange - low likelihood
                (1, (1, 0, 0, 0)),  # Transparent Red - no likelihood
            ],
            N=256,
        )

        # Override the edge value of the cmap
        cmap.set_over("white", alpha=0.5)  # Day time colour
        cmap.set_under("black", alpha=0.5)  # Night time colour

        if self.location_uncertainty is not None:
            # Uncertainties were provided: the surface is the distance from a
            # perfect match to the observation's plausible range, so the bright
            # region is exactly the area consistent with the observation.
            surface = self.location_uncertainty
        else:
            # Default: distance of the relative-difference surface from a match.
            surface = np.abs(self.location_likelihoods)

        norm = colors.BoundaryNorm(np.arange(0, 0.2, 0.02), cmap.N)

        # Create the map projection
        filterwarnings("ignore", category=DownloadWarning)
        ax = plt.axes(projection=getattr(ccrs, projection)(**projection_args))
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(
            cfeature.BORDERS, linestyle="-", edgecolor="black", linewidth=0.5
        )

        # replace NaN values with a specific value (e.g. -1)
        surface = np.where(np.isnan(surface), -1, surface)

        ax.pcolormesh(
            self.lons,
            self.lats,
            surface,
            cmap=cmap,
            norm=norm,
            transform=ccrs.PlateCarree(),
        )

        if self.sun_altitude_angle is not None:
            plt_title = f"Possible Locations at {self.date_time.strftime('%Y-%m-%d %H:%M:%S')} {self.time_format.title()}\n(sun altitude angle: {self.sun_altitude_angle})"
        else:
            plt_title = f"Possible Locations at {self.date_time.strftime('%Y-%m-%d %H:%M:%S')} {self.time_format.title()}\n(object height: {self.object_height}, shadow length: {self.shadow_length})"

        plt.title(plt_title)
        self.fig = fig
        return fig
