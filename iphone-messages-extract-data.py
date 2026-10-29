#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import sqlite3
import argparse
import shutil
from libbimfpy.apple_streamtyped import *
from libbimfpy.cocoa_timestamp import *


def get_attachment_info_from_file_db(db_file_cursor: sqlite3.Cursor, guid: str) -> dict:
    result: dict = {"result": False, "fileID": ""}
    db_file_cursor.execute(
        'SELECT * FROM "Files" WHERE "relativePath" LIKE "%{}%";'.format(guid)
    )
    db_file_rows = db_file_cursor.fetchall()
    if 1 == len(db_file_rows):
        for db_file_row in db_file_rows:
            result["result"] = True
            result["fileID"] = db_file_row["fileID"]
    else:
        print(
            "ERROR multiple or no result when try to find file using GUID {}".format(
                guid
            )
        )

    return result


def get_attachment_info(db_sms_cursor: sqlite3.Cursor, attach_id: int) -> dict:
    result: dict = {"result": False, "guid": ""}
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
    # hide_attachment INTEGER DEFAULT 0)
    db_sms_cursor.execute(
        'SELECT * FROM "attachment" WHERE "ROWID"={};'.format(attach_id)
    )
    db_attachment_rows = db_sms_cursor.fetchall()
    if 1 == len(db_attachment_rows):
        for db_attachment_row in db_attachment_rows:
            result["result"] = True
            result["guid"] = db_attachment_row["guid"]
    else:
        print("ERROR when try to find attachment using attach_id: {}".format(attach_id))

    return result


def get_attachment_name_and_path(
    db_file_cursor: sqlite3.Cursor,
    db_sms_cursor: sqlite3.Cursor,
    row_id: int,
) -> dict:
    # one attachment info:
    # "fileID": "",
    result: dict = {"result": False, "attachments_list": None}
    attachments_list: list = []
    # CREATE TABLE message_attachment_join (
    # message_id INTEGER REFERENCES message (ROWID) ON DELETE CASCADE,
    # attachment_id INTEGER REFERENCES attachment (ROWID) ON DELETE CASCADE,
    # UNIQUE(message_id, attachment_id))
    db_sms_cursor.execute(
        'SELECT * FROM "message_attachment_join" WHERE "message_id"={};'.format(row_id)
    )
    db_message_attachment_rows = db_sms_cursor.fetchall()
    for db_msg_attach_row in db_message_attachment_rows:
        attachment_info = get_attachment_info(
            db_sms_cursor, db_msg_attach_row["attachment_id"]
        )
        if attachment_info["result"]:
            attachment_info_in_file_db = get_attachment_info_from_file_db(
                db_file_cursor, attachment_info["guid"]
            )
            if attachment_info_in_file_db["result"]:
                attachments_list.append(attachment_info_in_file_db["fileID"])

    if 0 != len(attachments_list):
        result["result"] = True
        result["attachments_list"] = attachments_list
    else:
        print("ERROR cannot find attachment id using msg id {}".format(row_id))

    return result


def sms_db_process_attachments(
    db_files_cursor: sqlite3.Cursor,
    db_sms_path: str,
    base_path: str,
    output_path: str,
    year: int,
    list_attachments: list,
):
    # check SMS db file
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

    # open SMS db
    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()
    db_sms_cursor.execute('SELECT * FROM "message";')
    db_sms_rows = db_sms_cursor.fetchall()

    # iterate through SMS rows
    for db_sms_row in db_sms_rows:
        # skip empty row
        if db_sms_row["attributedBody"] is None:
            if db_sms_row["text"] is None:
                continue

        # older database cocoa timestamp is in seconds
        datetime_timestamp = get_datetime_from_cocoa_timestamp(db_sms_row["date"])

        # skip year not interested in
        if 0 != year:
            if year != datetime_timestamp.year:
                continue

        if 0 != db_sms_row["cache_has_attachments"]:
            # get text for searching
            body_text = None
            if db_sms_row["text"] is None:
                body_text = decode_streamtyped(db_sms_row["attributedBody"])
                if (body_text is None) or (0 == len(body_text)):
                    body_text = ""
            else:
                body_text = db_sms_row["text"]

            # get subject for searching
            subject_text = None
            if db_sms_row["subject"] is None:
                subject_text = ""
            else:
                subject_text = db_sms_row["subject"]

            # get attachments
            attachments = get_attachment_name_and_path(
                db_files_cursor, db_sms_cursor, db_sms_row["ROWID"]
            )
            if attachments["result"]:
                for attachment in attachments["attachments_list"]:
                    list_attachments.append(attachment)
            else:
                print(
                    'msg guid: {} cannot find attachments, datetime: "{}", subject: "{}", text: "{}"'.format(
                        db_sms_row["guid"],
                        datetime_timestamp.isoformat(),
                        subject_text,
                        body_text,
                    )
                )

    db_sms_conn.close()


def sms_db_process(
    db_sms_path: str,
    year: int,
):
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()
    db_sms_cursor.execute('SELECT * FROM "message";')
    db_sms_rows = db_sms_cursor.fetchall()

    for db_sms_row in db_sms_rows:
        # older database cocoa timestamp is in seconds
        datetime_timestamp = get_datetime_from_cocoa_timestamp(db_sms_row["date"])

        if 0 != year:
            if year != datetime_timestamp.year:
                db_sms_cursor.execute(
                    'DELETE FROM "message" WHERE "ROWID"={};'.format(
                        db_sms_row["ROWID"]
                    )
                )

    db_sms_conn.commit()
    db_sms_conn.close()


def main(args):
    print("backup path: {}".format(args.path))
    print("year: {}".format(args.year))

    file_db_path = os.path.join(args.path, "Manifest.db")

    if not os.path.exists(file_db_path):
        print("ERROR: file db does not exists, path: {}".format(file_db_path))
        return

    connection = sqlite3.connect(file_db_path)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # CREATE TABLE Files (
    # fileID TEXT PRIMARY KEY,
    # domain TEXT,
    # relativePath TEXT,
    # flags INTEGER,
    # file BLOB
    # )
    cursor.execute('SELECT * FROM "Files" WHERE "relativePath"="Library/SMS/sms.db";')

    db_files_rows = cursor.fetchall()

    list_attachment_file_ids = list()

    db_sms_path = None
    if 1 == len(db_files_rows):
        for db_files_row in db_files_rows:
            db_sms_path = os.path.join(
                args.path,
                db_files_row["fileID"][0:2],
                db_files_row["fileID"],
            )
            sms_db_process_attachments(
                cursor,
                db_sms_path,
                args.path,
                args.output_path,
                args.year,
                list_attachment_file_ids,
            )

            # copy SMS DB
            new_db_sms_path = os.path.join(
                args.output_path, db_files_row["fileID"][0:2]
            )
            new_db_sms_file_path = os.path.join(
                args.output_path, db_files_row["fileID"][0:2], db_files_row["fileID"]
            )
            if os.path.exists(db_sms_path):
                os.makedirs(name=new_db_sms_path, exist_ok=True)
                shutil.copy2(db_sms_path, new_db_sms_file_path)
    else:
        print('ERROR: Multiple or no "Library/SMS/sms.db" found')

    connection.close()

    # copy attachments to output
    for item in list_attachment_file_ids:
        file_path = os.path.join(args.path, item["fileID"][0:2], item["fileID"])
        new_path = os.path.join(args.output_path, item["file_id"][0:2])
        new_file_path = os.path.join(
            args.output_path, item["fileID"][0:2], item["fileID"]
        )

        if os.path.exists(file_path):
            os.makedirs(name=new_path, exist_ok=True)
            shutil.copy2(file_path, new_file_path)

    # copy file db to output
    new_file_db_path = os.path.join(args.output_path, "Manifest.db")
    shutil.copy2(file_db_path, new_file_db_path)

    # clean up file db records not belonging to SMS
    connection = sqlite3.connect(new_file_db_path)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "Files";')

    rows = cursor.fetchall()

    for row in rows:
        if row["fileID"] not in list_attachment_file_ids:
            if "Library/SMS/sms.db" not in row["relativePath"]:
                cursor.execute(
                    'DELETE FROM "Files" WHERE "fileID" = "{}";'.format(row["fileID"])
                )

    connection.commit()
    connection.close()

    # if year filter is all then skip SMS DB clean up
    if 0 == args.year:
        return

    # clean message db rows not outside year
    connection = sqlite3.connect(new_file_db_path)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "Files" WHERE "relativePath"="Library/SMS/sms.db";')

    rows = cursor.fetchall()
    if 1 == len(db_files_rows):
        for db_files_row in db_files_rows:
            db_sms_path = os.path.join(
                args.output_path,
                db_files_row["fileID"][0:2],
                db_files_row["fileID"],
            )
            sms_db_process(db_sms_path, args.year)
    else:
        print('ERROR: Multiple "Library/SMS/sms.db" found')

    connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # define each option with: parser.add_argument
    parser.add_argument("-p", "--path", required=True, help="iPhone backup path")
    parser.add_argument(
        "-o", "--output-path", required=True, help="Extracted data output path"
    )
    parser.add_argument(
        "-y",
        "--year",
        required=False,
        type=int,
        help="Set the year for extraction, 0 is means all",
        default=0,
    )
    args = parser.parse_args()  # automatically looks at sys.argv
    main(args)
