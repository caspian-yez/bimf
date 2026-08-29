#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import sqlite3
import argparse
from libbimfpy.cocoa_timestamp import auto_dec_seconds_or_nanoseconds


def sms_db_process(
    path_target_backup_sms_db: str, path_target_backup: str, default_phone_number: str
):
    if os.path.exists(path_target_backup_sms_db):
        print(path_target_backup_sms_db)
    else:
        print("Cannot fild {}".format(path_target_backup_sms_db))
        return

    print(path_target_backup)

    # CREATE TABLE message (
    # ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    # guid TEXT UNIQUE NOT NULL,
    # text TEXT,
    # replace INTEGER DEFAULT 0,
    # service_center TEXT,
    # handle_id INTEGER DEFAULT 0,
    # subject TEXT,
    # country TEXT,
    # attributedBody BLOB,
    # version INTEGER DEFAULT 0,
    # type INTEGER DEFAULT 0,
    # service TEXT,
    # account TEXT,
    # account_guid TEXT,
    # error INTEGER DEFAULT 0,
    # date INTEGER,
    # date_read INTEGER,
    # date_delivered INTEGER,
    # is_delivered INTEGER DEFAULT 0,
    # is_finished INTEGER DEFAULT 0,
    # is_emote INTEGER DEFAULT 0,
    # is_from_me INTEGER DEFAULT 0,
    # is_empty INTEGER DEFAULT 0,
    # is_delayed INTEGER DEFAULT 0,
    # is_auto_reply INTEGER DEFAULT 0,
    # is_prepared INTEGER DEFAULT 0,
    # is_read INTEGER DEFAULT 0,
    # is_system_message INTEGER DEFAULT 0,
    # is_sent INTEGER DEFAULT 0,
    # has_dd_results INTEGER DEFAULT 0,
    # is_service_message INTEGER DEFAULT 0,
    # is_forward INTEGER DEFAULT 0,
    # was_downgraded INTEGER DEFAULT 0,
    # is_archive INTEGER DEFAULT 0,
    # cache_has_attachments INTEGER DEFAULT 0,
    # cache_roomnames TEXT,
    # was_data_detected INTEGER DEFAULT 0,
    # was_deduplicated INTEGER DEFAULT 0,
    # is_audio_message INTEGER DEFAULT 0,
    # is_played INTEGER DEFAULT 0,
    # date_played INTEGER,
    # item_type INTEGER DEFAULT 0,
    # other_handle INTEGER DEFAULT 0,
    # group_title TEXT,
    # group_action_type INTEGER DEFAULT 0,
    # share_status INTEGER DEFAULT 0,
    # share_direction INTEGER DEFAULT 0,
    # is_expirable INTEGER DEFAULT 0,
    # expire_state INTEGER DEFAULT 0,
    # message_action_type INTEGER DEFAULT 0,
    # message_source INTEGER DEFAULT 0,
    # associated_message_guid TEXT,
    # associated_message_type INTEGER DEFAULT 0,
    # balloon_bundle_id TEXT,
    # payload_data BLOB,
    # expressive_send_style_id TEXT,
    # associated_message_range_location INTEGER DEFAULT 0,
    # associated_message_range_length INTEGER DEFAULT 0,
    # time_expressive_send_played INTEGER,
    # message_summary_info BLOB,
    # ck_sync_state INTEGER DEFAULT 0,
    # ck_record_id TEXT DEFAULT NULL,
    # ck_record_change_tag TEXT DEFAULT NULL,
    # destination_caller_id TEXT DEFAULT NULL,
    # sr_ck_sync_state INTEGER DEFAULT 0,
    # sr_ck_record_id TEXT DEFAULT NULL,
    # sr_ck_record_change_tag TEXT DEFAULT NULL,
    # is_corrupt INTEGER DEFAULT 0,
    # reply_to_guid TEXT DEFAULT NULL,
    # sort_id INTEGER DEFAULT 0,
    # is_spam INTEGER DEFAULT 0,
    # has_unseen_mention INTEGER DEFAULT 0,
    # thread_originator_guid TEXT DEFAULT NULL,
    # thread_originator_part TEXT DEFAULT NULL,
    # syndication_ranges TEXT DEFAULT NULL,
    # was_delivered_quietly INTEGER DEFAULT 0,
    # did_notify_recipient INTEGER DEFAULT 0,
    # synced_syndication_ranges TEXT DEFAULT NULL,
    # date_retracted INTEGER DEFAULT 0,
    # date_edited INTEGER DEFAULT 0,
    # was_detonated INTEGER DEFAULT 0,
    # part_count INTEGER,
    # is_stewie INTEGER DEFAULT 0,
    # is_kt_verified INTEGER DEFAULT 0,
    # is_sos INTEGER DEFAULT 0,
    # is_critical INTEGER DEFAULT 0,
    # bia_reference_id TEXT DEFAULT NULL,
    # fallback_hash TEXT DEFAULT NULL,
    # associated_message_emoji TEXT DEFAULT NULL,
    # is_pending_satellite_send INTEGER DEFAULT 0,
    # needs_relay INTEGER DEFAULT 0,
    # schedule_type INTEGER DEFAULT 0,
    # schedule_state INTEGER DEFAULT 0,
    # sent_or_received_off_grid INTEGER DEFAULT 0,
    # date_recovered INTEGER DEFAULT 0,
    # is_time_sensitive INTEGER DEFAULT 0,
    # ck_chat_id TEXT
    # )
    db_conn_target_backup_sms = sqlite3.connect(path_target_backup_sms_db)
    db_conn_target_backup_sms.row_factory = sqlite3.Row

    db_cursor_target_backup_sms = db_conn_target_backup_sms.cursor()

    # check cocoa timestamp for nanoseconds and destination_caller_id
    db_cursor_target_backup_sms.execute("SELECT * FROM message;")
    db_rows = db_cursor_target_backup_sms.fetchall()
    for row in db_rows:
        key_value: dict = {}

        # date INTEGER,
        # date_read INTEGER,
        # date_delivered INTEGER,
        # destination_caller_id
        match auto_dec_seconds_or_nanoseconds(row["date"]):
            case "ns":
                pass
            case "s":
                key_value["date"] = row["date"] * 1000000000
            case _:
                print(
                    "failed to detect rowid {}, guid: {} timestamp unit".format(
                        row["ROWID"], row["guid"]
                    )
                )
                continue

        match auto_dec_seconds_or_nanoseconds(row["date_read"]):
            case "ns":
                pass
            case "s":
                key_value["date_read"] = row["date_read"] * 1000000000
            case _:
                print(
                    "failed to detect rowid {}, guid: {} timestamp unit".format(
                        row["ROWID"], row["guid"]
                    )
                )
                continue

        match auto_dec_seconds_or_nanoseconds(row["date_delivered"]):
            case "ns":
                pass
            case "s":
                key_value["date_delivered"] = row["date_delivered"] * 1000000000
            case _:
                print(
                    "failed to detect rowid {}, guid: {} timestamp unit".format(
                        row["ROWID"], row["guid"]
                    )
                )
                continue

        if row["destination_caller_id"] is None:
            key_value["destination_caller_id"] = default_phone_number

        set_string: str = ""
        count = len(key_value.keys())
        for key in key_value.keys():
            match key:
                case "date" | "date_read" | "date_delivered":
                    set_string += " {} = {}".format(key, key_value[key])
                case "destination_caller_id":
                    set_string += " {} = '{}'".format(key, key_value[key])
            count -= 1
            if 0 != count:
                set_string += ","

        if 0 != len(key_value.keys()):
            query = "UPDATE message SET {} WHERE ROWID={};".format(
                set_string, row["ROWID"]
            )
            print(query)
            db_cursor_target_backup_sms.execute(query)
            db_cursor_target_backup_sms.execute("COMMIT;")

    db_conn_target_backup_sms.close()


def main(args):
    print("default phone number: {}".format(args.defaut_phone_number))
    print("target backup data path: {}".format(args.target_backup_path))
    # CREATE TABLE Files (
    # fileID TEXT PRIMARY KEY,
    # domain TEXT,
    # relativePath TEXT,
    # flags INTEGER,
    # file BLOB
    # )

    # create path from param
    path_target_backup_files_db = os.path.join(args.target_backup_path, "Manifest.db")

    # create connection to db
    db_conn_target_backup_files = sqlite3.connect(path_target_backup_files_db)
    db_conn_target_backup_files.row_factory = sqlite3.Row

    # create cursor
    db_cursor_target_backup_files = db_conn_target_backup_files.cursor()

    # find sms.db
    db_cursor_target_backup_files.execute(
        'SELECT * FROM Files WHERE relativePath = "Library/SMS/sms.db";'
    )

    # fetch to memory
    db_rows_target_backup_files = db_cursor_target_backup_files.fetchall()

    if 1 != len(db_rows_target_backup_files):
        print('ERROR: Multiple "Library/SMS/sms.db" found in backup files db')
        return 0

    for db_row in db_rows_target_backup_files:
        path_target_backup_sms_db = os.path.join(
            args.target_backup_path,
            db_row["fileID"][0:2],
            db_row["fileID"],
        )

    sms_db_process(
        path_target_backup_sms_db, args.target_backup_path, args.defaut_phone_number
    )

    db_conn_target_backup_files.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # define each option with: parser.add_argument
    parser.add_argument(
        "-p", "--defaut-phone-number", required=True, help="Default phone number"
    )
    parser.add_argument(
        "-b", "--target-backup-path", required=True, help="Path to the target backup"
    )
    args = parser.parse_args()  # automatically looks at sys.argv

    main(args)
