import sys
import os
import site

import pytest


def pytest_addoption(parser):
    # py.test has an issue where the cwd is not in the PYTHONPATH. Fix it here.
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    parser.addini("python_paths", type="pathlist", help="space seperated directory paths to add to PYTHONPATH via sys.path.insert(0, path)",
                  default=[])
    parser.addini("site_dirs", type="pathlist", help="space seperated directory paths to add to PYTHONPATH via site.addsitedir(path)",
                  default=[])


@pytest.mark.tryfirst
def pytest_load_initial_conftests(args, early_config, parser):
    for path in reversed(early_config.getini("python_paths")):
        sys.path.insert(0, str(path))
    for path in early_config.getini("site_dirs"):
        site.addsitedir(str(path))
