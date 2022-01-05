"""Adopt environment section in pytest configuration files."""

import os
import pytest


def pytest_addoption(parser):
    """Add section to configuration files."""
    help_msg = (
        "a line separated list of environment variables "
        "of the form NAME=VALUE."
        )

    parser.addini(
        "env",
        type="linelist",
        help=help_msg,
        default=[]
        )


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(args, early_config, parser):
    """Load environment variables from configuration files."""
    for e in early_config.getini("env"):
        part = e.partition("=")
        key = part[0].strip()
        value = part[2].strip()

        # Replace environment variables in value. for instance:
        # TEST_DIR={USER}/repo_test_dir.
        value = value.format(**os.environ)

        # use D: as a way to designate a default value
        # that will only override env variables if they
        # do not exist already
        dkey = key.split("D:")
        default_val = False

        if len(dkey) == 2:
            key = dkey[1]
            default_val = True

        if not default_val or key not in os.environ:
            os.environ[key] = value
