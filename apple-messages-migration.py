#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import sqlite3
import argparse
import shutil
from libbimfpy.apple_messages_db_manifest_table_files import *
from libbimfpy.apple_messages_db_sms_table_attachment import *
from libbimfpy.apple_messages_db_sms_table_chat_handle_join import *
from libbimfpy.apple_messages_db_sms_table_chat_lookup import *
from libbimfpy.apple_messages_db_sms_table_chat_message_join import *
from libbimfpy.apple_messages_db_sms_table_chat_service import *
from libbimfpy.apple_messages_db_sms_table_chat import *
from libbimfpy.apple_messages_db_sms_table_handle import *
from libbimfpy.apple_messages_db_sms_table_message_attachment_join import *
from libbimfpy.apple_messages_db_sms_table_message import *
from libbimfpy.apple_messages_db import *
from libbimfpy.apple_streamtyped import *
from libbimfpy.cocoa_timestamp import *


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


def get_db_sms_attachments(cursor_sms_db: sqlite3.Cursor, msg_id: int) -> list:
    db_msg_attach_join_rows = (
        db_sms_table_message_attachment_join_match_by_message_row_id(
            cursor_sms_db, msg_id
        )
    )
    list_attachments = list()
    assert 0 != len(
        db_msg_attach_join_rows
    ), "ERROR: cannot find message_attachment_join rows using msg row id: {}".format(
        msg_id
    )

    for db_msg_attach_join_row in db_msg_attach_join_rows:
        db_attach_rows = db_sms_table_attachment_match_by_attach_row_id(
            cursor_sms_db, db_msg_attach_join_row["attachment_id"]
        )
        assert 1 == len(
            db_attach_rows
        ), "ERROR: 0 or multiple attachments found using attachment row id: {}".format(
            db_msg_attach_join_row["attachment_id"]
        )
        for row in db_attach_rows:
            list_attachments.append(row)

    return list_attachments


def get_db_files_attachment_info(
    db_file_cursor: sqlite3.Cursor, db_sms_attach_rows: list
) -> list:
    list_db_file_attach_rows = list()
    for row in db_sms_attach_rows:
        db_file_rows = db_manifest_table_files_relativepath_match_by_attach_guid(
            db_file_cursor, row["guid"]
        )
        assert 1 == len(
            db_file_rows
        ), "ERROR when try to find file using GUID {}".format(row["guid"])
        for db_file_row in db_file_rows:
            list_db_file_attach_rows.append(db_file_row)

    return list_db_file_attach_rows


def get_db_sms_chat(db_sms_cursor: sqlite3.Cursor, chat_id: int) -> list:
    db_sms_chat_rows = db_sms_table_chat_match_by_chat_row_id(db_sms_cursor, chat_id)
    assert 1 == len(
        db_sms_chat_rows
    ), "ERROR: multiple or none chat found using chat id: {}".format(chat_id)
    return db_sms_chat_rows


def get_db_sms_chat_msg_join(db_sms_cursor: sqlite3.Cursor, msg_id: int) -> list:
    db_sms_chat_msg_join_rows = db_sms_table_chat_message_join_match_by_msg_row_id(
        db_sms_cursor, msg_id
    )
    assert 1 >= len(
        db_sms_chat_msg_join_rows
    ), "ERROR: multiple chat msg join found using msg_id: {}".format(msg_id)
    return db_sms_chat_msg_join_rows


def get_db_sms_handle_by_handle_id(
    db_sms_cursor: sqlite3.Cursor, handle_id: int
) -> list:
    db_sms_handle_rows = db_sms_table_handle_match_by_handle_row_id(
        db_sms_cursor, handle_id
    )
    assert 1 == len(
        db_sms_handle_rows
    ), "ERROR: multiple rows or none handle found using handle id: {}".format(handle_id)
    return db_sms_handle_rows


def get_db_sms_handles_by_chat_id(db_sms_cursor: sqlite3.Cursor, chat_id: int) -> list:
    list_handles = list()
    db_sms_chat_handle_join_rows = db_sms_table_chat_handle_join_match_by_chat_row_id(
        db_sms_cursor, chat_id
    )
    assert 0 != len(
        db_sms_chat_handle_join_rows
    ), "ERROR: cannot find handles using chat id: {}".format(chat_id)
    for db_sms_chat_handle_join_row in db_sms_chat_handle_join_rows:
        db_sms_handle_rows = get_db_sms_handle_by_handle_id(
            db_sms_cursor, db_sms_chat_handle_join_row["handle_id"]
        )
        for db_sms_handle_row in db_sms_handle_rows:
            list_handles.append(db_sms_handle_row)
    return list_handles


def get_db_sms_chat_lookup(db_sms_cursor: sqlite3.Cursor, chat_id: int) -> list:
    chat_lookup_rows = db_sms_table_chat_lookup_match_by_chat_row_id(
        db_sms_cursor, chat_id
    )
    return chat_lookup_rows


def get_db_sms_chat_service(db_sms_cursor: sqlite3.Cursor, chat_id: int) -> list:
    chat_service_rows = db_sms_table_chat_service_match_by_chat_row_id(
        db_sms_cursor, chat_id
    )
    return chat_service_rows


def process_one_message(
    db_files_cursor: sqlite3.Cursor,
    db_sms_row: sqlite3.Row,
    db_sms_cursor: sqlite3.Cursor,
) -> dict:
    dict_msg = dict()
    dict_msg["db_sms_message_row"] = list()
    dict_msg["db_sms_message_row"].append(db_sms_row)

    if 0 != db_sms_row["cache_has_attachments"]:
        dict_msg["db_sms_attachment_rows"] = get_db_sms_attachments(
            db_sms_cursor, db_sms_row["ROWID"]
        )
        dict_msg["db_file_attachments_rows"] = get_db_files_attachment_info(
            db_files_cursor, dict_msg["db_sms_attachment_rows"]
        )
    else:
        dict_msg["db_sms_attachment_rows"] = list()
        dict_msg["db_file_attachments_rows"] = list()

    chat_msg_join_rows = get_db_sms_chat_msg_join(db_sms_cursor, db_sms_row["ROWID"])
    dict_msg["db_sms_chat_msg_join_row"] = chat_msg_join_rows
    dict_msg["db_sms_msg_handle_row"] = get_db_sms_handle_by_handle_id(
        db_sms_cursor, db_sms_row["handle_id"]
    )
    if 1 == len(chat_msg_join_rows):
        for chat_msg_join_row in chat_msg_join_rows:
            dict_msg["db_sms_chat_row"] = get_db_sms_chat(
                db_sms_cursor, chat_msg_join_row["chat_id"]
            )
            dict_msg["db_sms_chat_handle_rows"] = get_db_sms_handles_by_chat_id(
                db_sms_cursor, chat_msg_join_row["chat_id"]
            )
            dict_msg["db_sms_chat_lookup_rows"] = get_db_sms_chat_lookup(
                db_sms_cursor, chat_msg_join_row["chat_id"]
            )
            dict_msg["db_sms_chat_service_rows"] = get_db_sms_chat_service(
                db_sms_cursor, chat_msg_join_row["chat_id"]
            )

    return dict_msg


def get_source_messages_data(
    cursor_file_db: sqlite3.Cursor, path_sms_db: str, year: int
) -> list:
    list_message_data = list()
    db_sms_conn = sqlite3.connect(path_sms_db)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()

    db_sms_rows = db_sms_table_message(db_sms_cursor)
    for db_sms_row in db_sms_rows:
        # older database cocoa timestamp is in seconds
        datetime_timestamp = get_datetime_from_cocoa_timestamp(db_sms_row["date"])
        if 0 != year:
            if year != datetime_timestamp.year:
                continue

        list_message_data.append(
            process_one_message(cursor_file_db, db_sms_row, db_sms_cursor)
        )

    db_sms_conn.close()

    return list_message_data


def check_paths_failed(list_paths: list) -> bool:
    bool_path_check_failed = False
    for path in list_paths:
        if not os.path.exists(path):
            print("ERROR: path not exists, path: {}".format(path))
            bool_path_check_failed = True

    return bool_path_check_failed


def check_sms_db_file(db_file_rows: list, path: str, path_db: str) -> str:
    if 1 == len(db_file_rows):
        for row in db_file_rows:
            path_db_sms = os.path.join(
                path,
                row["fileID"][0:2],
                row["fileID"],
            )
            if os.path.exists(path_db_sms):
                return path_db_sms
            else:
                print("ERROR: path not found: {}".format(path_db_sms))
                return ""
    else:
        print(
            'ERROR: Multiple or no "Library/SMS/sms.db" found in "{}"'.format(path_db)
        )

    return ""


def insert_or_update_table_handle(
    db_sms_cursor: sqlite3.Cursor, handle_row_data: sqlite3.Row
):
    db_sms_table_handle_rows = db_sms_table_handle_match_by_handle_id_and_service(
        db_sms_cursor, handle_row_data["id"], handle_row_data["service"]
    )
    assert 1 >= len(
        db_sms_table_handle_rows
    ), "ERROR: multiple handle rows found using id {}, service {}".format(
        handle_row_data["id"], handle_row_data["service"]
    )
    if 1 == len(db_sms_table_handle_rows):
        for row in db_sms_table_handle_rows:
            db_sms_table_handle_update(db_sms_cursor, row["ROWID"], handle_row_data)
            return row["ROWID"]
    elif 0 == len(db_sms_table_handle_rows):
        db_sms_table_handle_insert(db_sms_cursor, handle_row_data)
        return db_sms_cursor.lastrowid
    return -1


def insert_or_update_table_msg(
    db_sms_cursor: sqlite3.Cursor, msg_row_data: sqlite3.Row, handle_id_in_row: int
):
    db_sms_table_msg_rows = db_sms_table_message_match_by_guid(
        db_sms_cursor, msg_row_data["guid"]
    )
    assert 1 >= len(
        db_sms_table_msg_rows
    ), "ERROR: multiple message rows fund using msg guid {}".format(
        msg_row_data["guid"]
    )
    if 1 == len(db_sms_table_msg_rows):
        for row in db_sms_table_msg_rows:
            db_sms_table_message_update(
                db_sms_cursor, row["ROWID"], msg_row_data, handle_id_in_row
            )
            return row["ROWID"]
    elif 0 == len(db_sms_table_msg_rows):
        db_sms_table_message_insert(db_sms_cursor, msg_row_data, handle_id_in_row)
        return db_sms_cursor.lastrowid
    return -1


def insert_or_update_table_attachment(
    db_sms_cursor: sqlite3.Cursor, attach_row_data: sqlite3.Row
) -> int | None:
    attach_rows = db_sms_table_attachment_match_by_guid(
        db_sms_cursor, attach_row_data["guid"]
    )
    assert 1 >= len(
        attach_rows
    ), "ERROR: multiple attach rows found using guid: {}".format(
        attach_row_data["guid"]
    )
    if 1 == len(attach_rows):
        for row in attach_rows:
            db_sms_table_attachment_update(db_sms_cursor, row["ROWID"], attach_row_data)
            return row["ROWID"]
    elif 0 == len(attach_rows):
        db_sms_table_attachment_insert(db_sms_cursor, attach_row_data)
        return db_sms_cursor.lastrowid
    return -1


def insert_or_update_table_files(
    db_file_cursor: sqlite3.Cursor, files_row_data: sqlite3.Row
) -> str:
    db_manifest_files_rows = db_manifest_table_files_match_by_file_id(
        db_file_cursor, files_row_data["fileID"]
    )
    assert 1 >= len(
        db_manifest_files_rows
    ), "ERROR: multiple files rows found using fileID: {}".format(
        files_row_data["fileID"]
    )
    if 1 == len(db_manifest_files_rows):
        db_manifest_table_files_update(db_file_cursor, files_row_data)
    elif 0 == len(db_manifest_files_rows):
        db_manifest_table_files_insert(db_file_cursor, files_row_data)
    return files_row_data["fileID"]


def copy_files(file_id: str, path_source: str, path_target: str):
    path_source_file = os.path.join(path_source, file_id[0:2], file_id)
    path_target_path = os.path.join(path_target, file_id[0:2])
    path_target_file = os.path.join(path_target, file_id[0:2], file_id)

    if os.path.exists(path_source_file):
        os.makedirs(name=path_target_path, exist_ok=True)
        shutil.copy2(path_source_file, path_target_file)
    else:
        print("ERROR: {} do not exists".format(path_source_file))


def insert_table_message_attachment_join(
    db_sms_cursor: sqlite3.Cursor, msg_id: int, attach_id: int
):
    db_sms_msg_attach_join_rows = (
        db_sms_table_message_attachment_join_match_by_message_row_id_and_attch_row_id(
            db_sms_cursor, msg_id, attach_id
        )
    )
    assert 1 >= len(
        db_sms_msg_attach_join_rows
    ), "ERROR: multiple msg_attach_join rows found using msg id: {}, attach id: {}".format(
        msg_id, attach_id
    )
    if 0 == len(db_sms_msg_attach_join_rows):
        db_sms_table_message_attachment_join_insert(db_sms_cursor, msg_id, attach_id)


def insert_or_update_table_chat(
    db_sms_cursor: sqlite3.Cursor, chat_row_data: sqlite3.Row
):
    db_sms_chat_rows = db_sms_table_chat_match_by_chat_identifier(
        db_sms_cursor, chat_row_data["chat_identifier"]
    )
    assert 1 >= len(
        db_sms_chat_rows
    ), "ERROR: multiple chat rows found using chat_identifier: {}".format(
        chat_row_data["chat_identifier"]
    )
    if 1 == len(db_sms_chat_rows):
        for row in db_sms_chat_rows:
            db_sms_table_chat_update(db_sms_cursor, row["ROWID"], chat_row_data)
            return row["ROWID"]
    elif 0 == len(db_sms_chat_rows):
        db_sms_table_chat_insert(db_sms_cursor, chat_row_data)
        return db_sms_cursor.lastrowid
    return -1


def insert_chat_msg_join(
    db_sms_cursor: sqlite3.Cursor,
    chat_id: int,
    msg_id: int,
    chat_msg_join_row_data: sqlite3.Row,
):
    db_sms_table_chat_msg_join_rows = (
        db_sms_table_chat_message_join_match_by_chat_row_id_and_message_row_id(
            db_sms_cursor, chat_id, msg_id
        )
    )
    assert 1 >= len(
        db_sms_table_chat_msg_join_rows
    ), "ERROR: multiple chat msg join rows found using chat id: {}, msg id: {}".format(
        chat_id, msg_id
    )
    if 1 == len(db_sms_table_chat_msg_join_rows):
        db_sms_table_chat_message_join_update(
            db_sms_cursor, chat_id, msg_id, chat_msg_join_row_data
        )
    elif 0 == len(db_sms_table_chat_msg_join_rows):
        db_sms_table_chat_message_join_insert(
            db_sms_cursor, chat_id, msg_id, chat_msg_join_row_data
        )


def insert_chat_handle_join(
    db_sms_cursor: sqlite3.Cursor, chat_id: int, handle_id: int
):
    db_sms_chat_handle_join_rows = (
        db_sms_table_chat_handle_join_match_by_chat_row_id_and_handle_row_id(
            db_sms_cursor, chat_id, handle_id
        )
    )
    assert 1 >= len(
        db_sms_chat_handle_join_rows
    ), "ERROR: multiple chat handle join rows found using chat id: {}, handle id: {}".format(
        chat_id, handle_id
    )
    if 0 == len(db_sms_chat_handle_join_rows):
        db_sms_table_chat_handle_join_insert(db_sms_cursor, chat_id, handle_id)


def insert_or_update_chat_lookup(
    db_sms_cursor: sqlite3.Cursor, chat_lookup_row_data: sqlite3.Row, chat_row_id: int
):
    db_sms_chat_lookup_rows = db_sms_table_chat_lookup_match_by_chat_row_id_and_others(
        db_sms_cursor,
        chat_row_id,
        chat_lookup_row_data["identifier"],
        chat_lookup_row_data["domain"],
    )
    assert 1 >= len(
        db_sms_chat_lookup_rows
    ), "ERROR: multiple chat lookup rows found using chat id: {}".format(chat_row_id)
    if 1 == len(db_sms_chat_lookup_rows):
        db_sms_table_chat_lookup_update(
            db_sms_cursor, chat_lookup_row_data, chat_row_id
        )
    elif 0 == len(db_sms_chat_lookup_rows):
        db_sms_table_chat_lookup_insert(
            db_sms_cursor, chat_lookup_row_data, chat_row_id
        )


def insert_or_update_chat_service(
    db_sms_cursor: sqlite3.Cursor, chat_service_row_data: sqlite3.Row, chat_row_id: int
):
    db_sms_chat_service_rows = (
        db_sms_table_chat_service_match_by_chat_row_id_and_service(
            db_sms_cursor, chat_row_id, chat_service_row_data["service"]
        )
    )
    assert 1 >= len(
        db_sms_chat_service_rows
    ), "ERROR: multiple char service rows found using chat id: {}, service: {}".format(
        chat_row_id, chat_service_row_data["service"]
    )
    if 0 == len(db_sms_chat_service_rows):
        db_sms_table_chat_service_insert(
            db_sms_cursor, chat_row_id, chat_service_row_data["service"]
        )


def migrate_one_message(
    msg: dict,
    db_sms_cursor: sqlite3.Cursor,
    db_file_cursor: sqlite3.Cursor,
    path_source: str,
    path_target: str,
):
    handle_row_id_in_msg = -1
    msg_row_id = -1
    list_sms_attach_row_id = list()
    chat_row_id = -1

    # table handle
    for handle_row in msg["db_sms_msg_handle_row"]:
        handle_row_id_in_msg = insert_or_update_table_handle(db_sms_cursor, handle_row)

    for msg_row in msg["db_sms_message_row"]:
        msg_row_id = insert_or_update_table_msg(
            db_sms_cursor, msg_row, handle_row_id_in_msg
        )

    for attach_row in msg["db_sms_attachment_rows"]:
        attach_row_id = insert_or_update_table_attachment(db_sms_cursor, attach_row)
        list_sms_attach_row_id.append(attach_row_id)

    for file_row in msg["db_file_attachments_rows"]:
        file_id = insert_or_update_table_files(db_file_cursor, file_row)
        copy_files(file_id, path_source, path_target)

    for attach_row_id in list_sms_attach_row_id:
        insert_table_message_attachment_join(db_sms_cursor, msg_row_id, attach_row_id)

    if 0 != len(msg["db_sms_chat_msg_join_row"]):
        for chat_row in msg["db_sms_chat_row"]:
            chat_row_id = insert_or_update_table_chat(db_sms_cursor, chat_row)

        for chat_msg_join_row in msg["db_sms_chat_msg_join_row"]:
            insert_chat_msg_join(
                db_sms_cursor, chat_row_id, msg_row_id, chat_msg_join_row
            )

        list_handle_row_id = list()
        for handle_row in msg["db_sms_chat_handle_rows"]:
            handle_row_id = insert_or_update_table_handle(db_sms_cursor, handle_row)
            list_handle_row_id.append(handle_row_id)

        for handle_row_id in list_handle_row_id:
            insert_chat_handle_join(db_sms_cursor, chat_row_id, handle_row_id)

        for chat_lookup_row in msg["db_sms_chat_lookup_rows"]:
            insert_or_update_chat_lookup(db_sms_cursor, chat_lookup_row, chat_row_id)

        for chat_service_row in msg["db_sms_chat_service_rows"]:
            insert_or_update_chat_service(db_sms_cursor, chat_service_row, chat_row_id)


def migrate_data_to_target_db(
    list_source_msg_data: list,
    path_target_db_sms: str,
    db_target_file_cursor: sqlite3.Cursor,
    path_source_root: str,
    path_target_root: str,
):
    db_sms_conn = sqlite3.connect(path_target_db_sms)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()
    for item in list_source_msg_data:
        migrate_one_message(
            item,
            db_sms_cursor,
            db_target_file_cursor,
            path_source_root,
            path_target_root,
        )
    db_sms_conn.commit()
    db_sms_conn.close()


def main(args: argparse.Namespace):
    print("iphone backup database: {}".format(args.path_source))
    print("target database path: {}".format(args.path_target))
    print("year: {}".format(args.year))

    path_source_file_db = os.path.join(args.path_source, "Manifest.db")
    path_target_file_db = os.path.join(args.path_target, "Manifest.db")

    list_paths = list()
    list_paths.append(path_source_file_db)
    list_paths.append(path_target_file_db)

    if check_paths_failed(list_paths):
        return

    print("path_source_file_db: {}".format(path_source_file_db))
    print("path_target_file_db: {}".format(path_target_file_db))

    connection_source_file_db = sqlite3.connect(path_source_file_db)
    connection_target_file_db = sqlite3.connect(path_target_file_db)
    connection_source_file_db.row_factory = sqlite3.Row
    connection_target_file_db.row_factory = sqlite3.Row
    cursor_source_file_db = connection_source_file_db.cursor()
    cursor_target_file_db = connection_target_file_db.cursor()

    db_source_files_rows = db_manifest_table_files_find_sms_db(cursor_source_file_db)
    db_target_files_rows = db_manifest_table_files_find_sms_db(cursor_target_file_db)

    path_source_sms_db = check_sms_db_file(
        db_source_files_rows, args.path_source, path_source_file_db
    )
    path_target_sms_db = check_sms_db_file(
        db_target_files_rows, args.path_target, path_target_file_db
    )

    if 0 == len(path_source_sms_db) or 0 == len(path_target_sms_db):
        return

    print("path_source_sms_db: {}".format(path_source_sms_db))
    print("path_target_sms_db: {}".format(path_target_sms_db))

    list_source_messages = get_source_messages_data(
        cursor_source_file_db, path_source_sms_db, args.year
    )

    migrate_data_to_target_db(
        list_source_messages,
        path_target_sms_db,
        cursor_target_file_db,
        args.path_source,
        args.path_target,
    )

    connection_source_file_db.close()
    connection_target_file_db.commit()
    connection_target_file_db.close()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate apple message database from iphone backup database to new folder "
        "and keep the data same logically. "
        "This will recreate logically identical database at new folder."
    )
    # define each option with: parser.add_argument
    parser.add_argument("-s", "--path-source", required=True, help="iPhone backup path")
    parser.add_argument(
        "-t",
        "--path-target",
        required=True,
        help="Target path to database to save data",
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
