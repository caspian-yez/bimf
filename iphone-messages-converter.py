#!/usr/bin/env python3
import sys
import os
import sqlite3
import email.message
import email.utils


def sms_db_process(db_files_cursor, db_sms_path):
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

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
    # message_summary_info BLOB
    # )
    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()
    db_sms_cursor.execute("SELECT * FROM message")
    db_sms_rows = db_sms_cursor.fetchall()

    for db_sms_row in db_sms_rows:
        if 0 != db_sms_row["cache_has_attachments"]:
            print(db_sms_row["text"])

    db_sms_conn.close()


def main():
    if 3 != len(sys.argv):
        print("need parameters: <database filepath> <phone number>")
        return

    print(sys.argv[0])  # program name
    print(sys.argv[1])  # unencrypted backup path
    print(sys.argv[2])  # reserved

    # CREATE TABLE Files (
    # fileID TEXT PRIMARY KEY,
    # domain TEXT,
    # relativePath TEXT,
    # flags INTEGER,
    # file BLOB
    # )
    db_files_path = os.path.join(sys.argv[1], "Manifest.db")
    print(db_files_path)
    db_files_conn = sqlite3.connect(db_files_path)
    db_files_conn.row_factory = sqlite3.Row

    db_files_cursor = db_files_conn.cursor()
    db_files_cursor.execute(
        'SELECT * FROM Files WHERE relativePath = "Library/SMS/sms.db"'
    )
    db_files_rows = db_files_cursor.fetchall()

    if 1 == len(db_files_rows):
        for db_files_row in db_files_rows:
            db_sms_path = os.path.join(
                sys.argv[1],
                db_files_row["fileID"][0:2],
                db_files_row["fileID"],
            )
            sms_db_process(db_files_cursor, db_sms_path)
    else:
        print('ERROR: Multiple "Library/SMS/sms.db" found')

    db_files_conn.close()


if __name__ == "__main__":
    main()
