#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import sqlite3
import argparse
import shutil


def sms_db_process(
    db_cursor_source_backup_files: sqlite3.Cursor,
    path_source_backup_sms_db: str,
    path_source_backup: str,
    path_target_backup: str,
):
    if os.path.exists(path_source_backup_sms_db):
        print(path_source_backup_sms_db)
    else:
        print("Cannot find {}".format(path_source_backup_sms_db))
        return

    print(path_source_backup)
    print(path_target_backup)

    # CREATE TABLE attachment (
    # ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    # guid TEXT UNIQUE NOT NULL,
    # created_date INTEGER DEFAULT 0,
    # start_date INTEGER DEFAULT 0,
    # filename TEXT,
    # uti TEXT,
    # mime_type TEXT,
    # transfer_state INTEGER DEFAULT 0,
    # is_outgoing INTEGER DEFAULT 0,
    # user_info BLOB,
    # transfer_name TEXT,
    # total_bytes INTEGER DEFAULT 0,
    # is_sticker INTEGER DEFAULT 0,
    # sticker_user_info BLOB,
    # attribution_info BLOB,
    # hide_attachment INTEGER DEFAULT 0,
    # ck_sync_state INTEGER DEFAULT 0,
    # ck_server_change_token_blob BLOB DEFAULT NULL,
    # ck_record_id TEXT DEFAULT NULL,
    # original_guid TEXT,
    # sr_ck_record_id TEXT DEFAULT NULL,
    # sr_ck_sync_state INTEGER DEFAULT 0,
    # sr_ck_server_change_token_blob BLOB DEFAULT NULL,
    # is_commsafety_sensitive INTEGER DEFAULT 0,
    # emoji_image_content_identifier TEXT DEFAULT NULL,
    # emoji_image_short_description TEXT DEFAULT NULL,
    # preview_generation_state INTEGER DEFAULT 0
    # )
    db_conn_source_backup_sms = sqlite3.connect(path_source_backup_sms_db)
    db_conn_source_backup_sms.row_factory = sqlite3.Row

    db_cursor_source_backup_sms = db_conn_source_backup_sms.cursor()

    db_cursor_source_backup_sms.execute("SELECT * FROM attachment;")
    rows_source_backup_attachment = db_cursor_source_backup_sms.fetchall()

    for db_row_attachment in rows_source_backup_attachment:
        db_cursor_source_backup_files.execute(
            "SELECT * FROM Files WHERE relativePath LIKE '%{}%';".format(
                db_row_attachment["guid"]
            )
        )
        db_file_rows = db_cursor_source_backup_files.fetchall()
        if 1 == len(db_file_rows):
            for db_file_row in db_file_rows:
                path_source_backup_attachment_file = os.path.join(
                    path_source_backup,
                    db_file_row["fileID"][0:2],
                    db_file_row["fileID"],
                )
                path_target_backup_attachment_folder = os.path.join(
                    path_target_backup, db_file_row["fileID"][0:2]
                )
                path_target_backup_attachment_file = os.path.join(
                    path_target_backup,
                    db_file_row["fileID"][0:2],
                    db_file_row["fileID"],
                )

                if os.path.exists(path_source_backup_attachment_file):
                    print(
                        "Copying {} to {}".format(
                            path_source_backup_attachment_file,
                            path_target_backup_attachment_file,
                        )
                    )
                    os.makedirs(
                        name=path_target_backup_attachment_folder, exist_ok=True
                    )
                    shutil.copy2(
                        src=path_source_backup_attachment_file,
                        dst=path_target_backup_attachment_file,
                        follow_symlinks=False,
                    )
                else:
                    print(
                        "ERROR cannot find new backup attachment GUID {}, path {}".format(
                            db_row_attachment["guid"],
                            path_source_backup_attachment_file,
                        )
                    )
        else:
            print(
                "ERROR when try to find file using attachment GUID {}".format(
                    db_row_attachment["guid"]
                )
            )

    db_conn_source_backup_sms.close()


def main(args):
    print("source backup data path: {}".format(args.source_backup_path))
    print("target backup data path: {}".format(args.target_backup_path))
    # CREATE TABLE Files (
    # fileID TEXT PRIMARY KEY,
    # domain TEXT,
    # relativePath TEXT,
    # flags INTEGER,
    # file BLOB
    # )

    # create path from param
    path_source_backup_files_db = os.path.join(args.source_backup_path, "Manifest.db")

    # create connection to db
    db_conn_source_backup_files = sqlite3.connect(path_source_backup_files_db)
    db_conn_source_backup_files.row_factory = sqlite3.Row

    # create cursor
    db_cursor_source_backup_files = db_conn_source_backup_files.cursor()

    # find sms.db
    db_cursor_source_backup_files.execute(
        'SELECT * FROM Files WHERE relativePath = "Library/SMS/sms.db";'
    )

    # fetch to memory
    db_rows_source_backup_files = db_cursor_source_backup_files.fetchall()

    if 1 != len(db_rows_source_backup_files):
        print('ERROR: Multiple "Library/SMS/sms.db" found in new backup files')
        return 0

    for db_row in db_rows_source_backup_files:
        path_source_backup_sms_db = os.path.join(
            args.source_backup_path,
            db_row["fileID"][0:2],
            db_row["fileID"],
        )

    sms_db_process(
        db_cursor_source_backup_files,
        path_source_backup_sms_db,
        args.source_backup_path,
        args.target_backup_path,
    )

    db_conn_source_backup_files.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # define each option with: parser.add_argument
    parser.add_argument(
        "-s", "--source-backup-path", required=True, help="Path to the source backup"
    )
    parser.add_argument(
        "-t", "--target-backup-path", required=True, help="Path to the target backup"
    )
    args = parser.parse_args()  # automatically looks at sys.argv

    main(args)
