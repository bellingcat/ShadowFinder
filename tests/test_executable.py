"""
The tests in this file test that running shadowfinder as an executable behaves
as expected.
"""

import subprocess


def test_executable_without_args():
    """Tests that running shadowfinder without any arguments returns the CLI's help string and 0 exit code."""
    # GIVEN
    expected = """
NAME
    shadowfinder

SYNOPSIS
    shadowfinder COMMAND

COMMANDS
    COMMAND is one of the following:

     find
       Find the shadow length of an object given its height and the date and time.

     find_sun
       Locate a shadow based on the solar altitude angle and the date and time.
"""

    # WHEN
    result = subprocess.run(["shadowfinder"], capture_output=True, text=True)

    # THEN
    assert result.returncode == 0
    assert result.stdout.strip() == expected.strip()
