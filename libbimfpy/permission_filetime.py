#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import stat
import datetime


def update_creation_modify_time(timestamp: datetime.datetime, filepath: str):
    amtime = timestamp.timestamp(), timestamp.timestamp()
    os.utime(filepath, times=amtime)


def update_permissions(filepath: str):
    os.chmod(
        filepath,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
    )
