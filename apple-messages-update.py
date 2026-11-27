#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import sqlite3
import argparse
from libbimfpy.apple_messages_db_manifest_table_files import *
from libbimfpy.apple_messages_db_sms_table_chat_message_join import *
from libbimfpy.apple_messages_db_sms_table_message import *


def update_table_message(
    db_sms_cursor: sqlite3.Cursor, row: sqlite3.Row, default_number: str
):
    key_value_needs_update = dict()
    if 0 != row["date"] and 1000000000 > row["date"]:
        key_value_needs_update["date"] = row["date"] * 1000000000

    if 0 != row["date_read"] and 1000000000 > row["date_read"]:
        key_value_needs_update["date_read"] = row["date_read"] * 1000000000

    if 0 != row["date_delivered"] and 1000000000 > row["date_delivered"]:
        key_value_needs_update["date_delivered"] = row["date_delivered"] * 1000000000

    if row["destination_caller_id"] is None:
        key_value_needs_update["destination_caller_id"] = default_number

    if 0 != len(key_value_needs_update):
        db_sms_table_message_update_old_data_format(
            db_sms_cursor, row, key_value_needs_update
        )


def update_table_chat_message_join(db_sms_cursor: sqlite3.Cursor, row: sqlite3.Row):
    if 0 != row["message_date"] and 1000000000 > row["message_date"]:
        db_sms_table_chat_message_join_update_message_date(
            db_sms_cursor,
            row["message_date"] * 1000000000,
            row["chat_id"],
            row["message_id"],
        )


def sms_db_process(
    db_sms_path: str,
    default_number: str,
):
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()

    rows = db_sms_table_chat_message_join(db_sms_cursor)
    for row in rows:
        update_table_chat_message_join(db_sms_cursor, row)

    rows = db_sms_table_message(db_sms_cursor)
    for row in rows:
        update_table_message(db_sms_cursor, row, default_number)

    db_sms_conn.commit()
    db_sms_conn.close()


def main(args):
    print("Target backup path: {}".format(args.target_backup_path))

    db_files_path = os.path.join(args.target_backup_path, "Manifest.db")
    print(db_files_path)
    db_files_conn = sqlite3.connect(db_files_path)
    db_files_conn.row_factory = sqlite3.Row
    db_files_cursor = db_files_conn.cursor()

    db_files_rows = db_manifest_table_files_find_sms_db(db_files_cursor)
    if 1 == len(db_files_rows):
        for db_files_row in db_files_rows:
            db_sms_path = os.path.join(
                args.target_backup_path,
                db_files_row["fileID"][0:2],
                db_files_row["fileID"],
            )
            sms_db_process(
                db_sms_path,
                args.default_number,
            )
    else:
        print('ERROR: Multiple "Library/SMS/sms.db" found')

    db_files_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="update iphone's apple message backup database data format"
    )
    # define each option with: parser.add_argument
    parser.add_argument(
        "-t", "--target-backup-path", required=True, help="Path to the target backup"
    )
    parser.add_argument(
        "-n",
        "--default-number",
        required=True,
        help="in older database destination_caller_id do not exists so user have to set default number",
    )
    args = parser.parse_args()  # automatically looks at sys.argv
    main(args)
