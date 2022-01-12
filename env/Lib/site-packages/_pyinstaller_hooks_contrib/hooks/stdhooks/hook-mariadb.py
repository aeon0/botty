# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------


from PyInstaller.compat import is_py38


# The MariaDB uses a .pyd file and uses import within its __init__.py
# The decimal import seems to be hidden in Python version 3.7 and older
if not is_py38:
    hiddenimports = ['decimal']
