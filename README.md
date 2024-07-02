# ShadowFinder

<a href="https://www.bellingcat.com"><img alt="Bellingcat logo: Discover Bellingcat" src="https://img.shields.io/badge/Discover%20Bellingcat-%20?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TS0UqDnZQEcxQneyiIo6likWwUNoKrTqYXPoFTRqSFBdHwbXg4Mdi1cHFWVcHV0EQ%2FABxdnBSdJES%2F5cUWsR4cNyPd%2Fced%2B8AoVllqtkTA1TNMtKJuJjLr4rBVwQwhhBEDEvM1JOZxSw8x9c9fHy9i%2FIs73N%2Fjn6lYDLAJxLHmG5YxBvEs5uWznmfOMzKkkJ8Tjxp0AWJH7kuu%2FzGueSwwDPDRjY9TxwmFktdLHcxKxsq8QxxRFE1yhdyLiuctzir1Tpr35O%2FMFTQVjJcpzmKBJaQRIo6klFHBVVYiNKqkWIiTftxD%2F%2BI40%2BRSyZXBYwcC6hBheT4wf%2Fgd7dmcXrKTQrFgcCLbX%2BMA8FdoNWw7e9j226dAP5n4Err%2BGtNYO6T9EZHixwBA9vAxXVHk%2FeAyx1g6EmXDMmR%2FDSFYhF4P6NvygODt0Dfmttbex%2BnD0CWulq%2BAQ4OgYkSZa97vLu3u7d%2Fz7T7%2BwHEU3LHAa%2FQ6gAAAAZiS0dEAAAAAAAA%2BUO7fwAAAAlwSFlzAAAuIwAALiMBeKU%2FdgAAAAd0SU1FB%2BgFHwwiMH4odB4AAAAZdEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAAA50lEQVQ4y82SvWpCQRCFz25ERSJiCNqlUiS1b5AuEEiZIq1NOsGXCKms0wXSp9T6dskDiFikyiPc%2FrMZyf3FXSGQ0%2BzuzPl2ZoeVKgQ0gQ2wBVpVHlcDkjM5V%2FJ5nag6sJ%2FZX%2Bh%2FC7gEhqeAFKf7p1M9aB3b5oN1OomB7g1axUBPBr3GQHODHmOgqUF3MZAzKI2d4LWBV4H%2BMXDuJd1a7Cew1k7SwksaHC4LqNaw7aeX9GWHXkC1G1sTAS17Y3Kk2lnp4wNLiz0DrgLq8qt2MfmSSabAO%2FBBXp26dtrADPjOmN%2BAUdG7B3cE61l5hOZiAAAAAElFTkSuQmCC&logoColor=%23fff&color=%23000"></a><!--
--><a href="https://discord.gg/bellingcat"><img alt="Discord logo: Join our community" src="https://img.shields.io/badge/Join%20our%20community-%20?style=for-the-badge&logo=discord&logoColor=%23fff&color=%235865F2"></a><!--
--><a href="https://colab.research.google.com/github/Bellingcat/ShadowFinder/blob/main/ShadowFinderColab.ipynb"><img alt="Colab icon: Try it on Colab" src="https://img.shields.io/badge/Try%20it%20on%20Colab-%20?style=for-the-badge&logo=googlecolab&logoColor=fff&logoSize=auto&color=e8710a"></a>

A lightweight tool and Google Colab notebook for estimating the points on the Earth's surface where a shadow of a particular length could occur, for geolocation purposes.

Using an object's height, the length of its shadow, the date and the time, ShadowFinder estimates the possible locations where that shadow could occur. These possible locations are shown as a bright band on a map of the Earth:

![ExampleShadowFinderOutput](https://github.com/bellingcat/ShadowFinder/assets/54807169/391c9b54-d5b4-463f-9c09-94ff1fec6ee4)


## Usage - Google Colab Notebook 🚀
No installation necessary, just try it out using the [Google Colab notebook here](https://colab.research.google.com/github/Bellingcat/ShadowFinder/blob/main/ShadowFinderColab.ipynb)!

## Installation :magic_wand:
[![PyPI - Version](https://img.shields.io/pypi/v/ShadowFinder)](https://pypi.org/project/ShadowFinder/)

ShadowFinder is built with the interactive notebook in mind, which can be downloaded and used in a local Jupyter environment, the package also provides a Python API and a command-line interface.

ShadowFinder is published on [PyPi](https://pypi.org/project/ShadowFinder/) so can be installed via `pip` with:

```shell
pip install shadowfinder
```
## Usage - Python Library 🐍

If you want to use ShadowFinder directly from Python, the usage is as follows.

```python
from shadowfinder import ShadowFinder

finder = ShadowFinder()

# Use a pre-generated timezone grid to save time
# Attempt to load a timezone grid and on a failure generate the grid and save to file
try:
    finder.load_timezone_grid()
except FileNotFoundError:
    finder.generate_timezone_grid()
    finder.save_timezone_grid() # timezone_grid.json

# Set up the scenario
# Provide either object_height and shadow_length OR sun_altitude_angle
finder.set_details(
    date_time=date_time, # datetime object with no timezone awareness
    object_height=object_height, # object height in arbitrary units
    shadow_length=shadow_length, # shadow length in arbitrary units
    time_format=time_type, # string, either 'local' or 'utc'
    sun_altitude_angle=sun_altitude_angle, # altitude angle of the sun, in degrees above the horizon
)

# Run the finder
finder.find_shadows()

# Access the resulting figure
fig = finder.plot_shadows()
```

## Usage - Command Line Interface 🐌
>[!IMPORTANT]
> Using the CLI is not the recommended way of using ShadowFinder as it is quite slow (there is currently not a caching strategy for the timezone_grid, so this is generated every run which is resource intesive)

```shell
shadowfinder find 10 5 2024-02-29 13:59:59 --time_format=utc
```
Where the arguments are `OBJECT_HEIGHT`, `SHADOW_LENGTH`, `DATE`, and `TIME` respectively.

You can also use the angle to the sun directly (above the horizon, in degrees):

```shell
shadowfinder find_sun 50 2024-02-29 13:59:59 --time_format=utc
```
Where the arguments are `SUN_ALTITUDE_ANGLE`, `DATE`, and `TIME` respectively.

More complete help information can be found by running:

```shell
shadowfinder find --help
shadowfinder find_sun --help
```

## Development :octocat:

<details>
<summary>Expand to view information for developers</summary>

This section describes how to install the project to run it from source, for example if you want to build new features.

```bash
# Clone the repository
git clone https://github.com/bellingcat/ShadowFinder.git

# Change directory to the project folder
cd ShadowFinder
```

This project uses [Poetry](https://python-poetry.org/docs) for dependency management and packaging.

```bash
# Install poetry if you haven't already
pip install poetry

# Install dependencies
poetry install

# Setup pre-commit hooks
poetry run pre-commit install

# Run the tool
poetry run shadowfinder --help

# Run tests against your current Python interpreter
poetry run pytest

# Or, run pytest against all shadowfinder supported Python versions
poetry run tox p  # p=run in parallel
```
</details>
