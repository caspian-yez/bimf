#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import datetime


def get_timestamp_filename(timestamp: datetime.datetime, id: str) -> str:
    return "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}-{}".format(
        timestamp.year,
        timestamp.month,
        timestamp.day,
        timestamp.hour,
        timestamp.minute,
        timestamp.second,
        id,
    )
