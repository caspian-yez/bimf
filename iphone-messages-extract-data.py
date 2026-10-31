#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import sqlite3
import argparse
import shutil
from libbimfpy.apple_messages_db import *
from libbimfpy.apple_streamtyped import *
from libbimfpy.cocoa_timestamp import *


def get_attachment_name_and_path(
    db_file_cursor: sqlite3.Cursor,
    db_sms_cursor: sqlite3.Cursor,
    row_id: int,
) -> dict:
    result: dict = {"result": False, "attachments_list": None}
    attachments_list: list = []
    db_message_attachment_rows = (
        db_sms_table_message_attachment_join_match_by_message_row_id(
            db_sms_cursor, row_id
        )
    )
    for db_msg_attach_row in db_message_attachment_rows:
        attachment_info = db_sms_table_attachment_match_by_attach_row_id(
            db_sms_cursor, db_msg_attach_row["attachment_id"]
        )
        if 1 == len(attachment_info):
            attachment_info_in_file_db = (
                db_manifest_table_files_relativepath_match_by_attach_guid(
                    db_file_cursor, attachment_info[0]["guid"]
                )
            )
            if 1 == len(attachment_info_in_file_db):
                attachments_list.append(attachment_info_in_file_db[0]["fileID"])
            else:
                print(
                    "ERROR multiple or no result when try to find file using attachment GUID {}".format(
                        attachment_info[0]["guid"]
                    )
                )
        else:
            print(
                "ERROR when try to find attachment using attach_id: {}".format(
                    db_msg_attach_row["attachment_id"]
                )
            )

    if 0 != len(attachments_list):
        result["result"] = True
        result["attachments_list"] = attachments_list
    else:
        print("ERROR cannot find attachment id using msg id {}".format(row_id))

    return result


def sms_db_process_attachments(
    db_files_cursor: sqlite3.Cursor,
    db_sms_path: str,
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

    db_sms_rows = db_sms_table_message(db_sms_cursor)
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
            # check balloon_bundle_id
            if db_sms_row["balloon_bundle_id"] is not None:
                print(
                    "Warning: msg guid {}, balloon_bundle_id not NULL: {}".format(
                        db_sms_row["guid"], db_sms_row["balloon_bundle_id"]
                    )
                )

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


def delete_attachment_path(path: str):
    print("db function delete_attachment_path: path: {}".format(path))


def after_delete_message_plugin(ROWID: int, guid: str):
    print(
        "db function after_delete_message_plugin: ROWID: {}, guid: {}".format(
            ROWID, guid
        )
    )


def before_delete_attachment_path(ROWID: int, guid: str):
    print(
        "db function before_delete_attachment_path: ROWID: {}, guid: {}".format(
            ROWID, guid
        )
    )


def delete_chat_background_before_deleting_chat(guid: str, properties: bytes):
    print(
        "db function delete_chat_background_before_deleting_chat: guid: {}, properties: {}".format(
            guid, properties
        )
    )


def is_mic_enabled() -> int:
    return 0


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
    db_sms_conn.create_function("delete_attachment_path", 1, delete_attachment_path)
    db_sms_conn.create_function(
        "after_delete_message_plugin", 2, after_delete_message_plugin
    )
    db_sms_conn.create_function(
        "before_delete_attachment_path", 2, before_delete_attachment_path
    )
    db_sms_conn.create_function(
        "delete_chat_background_before_deleting_chat",
        2,
        delete_chat_background_before_deleting_chat,
    )
    db_sms_conn.create_function("is_mic_enabled", 1, is_mic_enabled)
    db_sms_cursor = db_sms_conn.cursor()

    db_sms_rows = db_sms_table_message(db_sms_cursor)
    for db_sms_row in db_sms_rows:
        # older database cocoa timestamp is in seconds
        datetime_timestamp = get_datetime_from_cocoa_timestamp(db_sms_row["date"])

        if year != datetime_timestamp.year:
            db_sms_table_message_delete_by_msg_row_id(
                db_sms_cursor, db_sms_row["ROWID"]
            )
            db_sms_table_message_attachment_join_delete_by_msg_row_id(
                db_sms_cursor, db_sms_row["ROWID"]
            )
            db_sms_table_chat_message_join_delete_by_msg_row_id(
                db_sms_cursor, db_sms_row["ROWID"]
            )

    db_sms_trigger_drop_before_delete_chat_update_sync_chat_deletes(db_sms_cursor)

    db_chat_rows = db_sms_table_chat(db_sms_cursor)
    for db_chat_row in db_chat_rows:
        db_chat_message_join_rows = db_sms_table_chat_message_join_match_by_chat_row_id(
            db_sms_cursor, db_chat_row["ROWID"]
        )
        if 0 == len(db_chat_message_join_rows):
            db_sms_table_chat_delete_by_chat_row_id(db_sms_cursor, db_chat_row["ROWID"])
            db_sms_table_chat_handle_join_delete_by_chat_row_id(
                db_sms_cursor, db_chat_row["ROWID"]
            )
            db_sms_table_chat_service_delete_by_chat_row_id(
                db_sms_cursor, db_chat_row["ROWID"]
            )
            db_sms_table_sync_chat_slice_delete_by_chat_row_id(
                db_sms_cursor, db_chat_row["ROWID"]
            )

    db_sms_table_deleted_messages_delete_all(db_sms_cursor)
    db_sms_table_sync_deleted_attachments_delete_all(db_sms_cursor)
    db_sms_table_sync_deleted_chats_delete_all(db_sms_cursor)
    db_sms_table_sync_deleted_messages_delete_all(db_sms_cursor)

    db_sms_trigger_create_before_delete_chat_update_sync_chat_deletes(db_sms_cursor)

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

    list_attachment_file_ids = list()

    db_files_rows = db_manifest_table_files_find_sms_db(cursor)
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
        file_path = os.path.join(args.path, item[0:2], item)
        new_path = os.path.join(args.output_path, item[0:2])
        new_file_path = os.path.join(args.output_path, item[0:2], item)

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

    rows = db_manifest_table_files(cursor)
    for row in rows:
        if row["fileID"] not in list_attachment_file_ids:
            if "Library/SMS/sms.db" not in row["relativePath"]:
                db_manifest_table_files_delete_by_fileid(row["fileID"])

    connection.commit()
    connection.close()

    # if year filter is all then skip SMS DB clean up
    if 0 == args.year:
        return

    # clean message db rows not outside year
    connection = sqlite3.connect(new_file_db_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    rows = db_manifest_table_files_find_sms_db(cursor)
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
