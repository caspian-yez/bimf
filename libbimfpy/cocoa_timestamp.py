#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import datetime
import zoneinfo

COCOA_TIMESTAMP_UNIX_TIMESTAMP_DIFF_SECONDS = 978307200


def auto_dec_seconds_or_nanoseconds(cocoa_timestamp: int) -> str:
    """
    this function is limited
    won't work after 2032-09-09
    """
    if 0 == cocoa_timestamp:
        return "ns"
    if datetime.datetime.now().year > 2030:
        return "unknow"
    if cocoa_timestamp / 1000000000 > 1:
        return "ns"
    else:
        return "s"


def get_datetime_from_cocoa_timestamp(cocoa_timestamp: int) -> datetime.datetime:
    match (auto_dec_seconds_or_nanoseconds(cocoa_timestamp)):
        case "s":
            local_datetime = datetime.datetime.fromtimestamp(
                cocoa_timestamp + COCOA_TIMESTAMP_UNIX_TIMESTAMP_DIFF_SECONDS,
                zoneinfo.ZoneInfo("UTC"),
            )
        case "ns":
            local_datetime = datetime.datetime.fromtimestamp(
                cocoa_timestamp / 1000000000
                + COCOA_TIMESTAMP_UNIX_TIMESTAMP_DIFF_SECONDS,
                zoneinfo.ZoneInfo("UTC"),
            )
        case _:
            print(
                "ERROR: cannot determin date timestamp unit of value".format(
                    cocoa_timestamp
                )
            )
            return None
    return local_datetime
