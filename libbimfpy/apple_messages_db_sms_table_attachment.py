#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_sms_table_attachment_datatype_mapping = {
    "guid": "TEXT",
    "created_date": "INTEGER",
    "start_date": "INTEGER",
    "filename": "TEXT",
    "uti": "TEXT",
    "mime_type": "TEXT",
    "transfer_state": "INTEGER",
    "is_outgoing": "INTEGER",
    "user_info": "BLOB",
    "transfer_name": "TEXT",
    "total_bytes": "INTEGER",
    "is_sticker": "INTEGER",
    "sticker_user_info": "BLOB",
    "attribution_info": "BLOB",
    "hide_attachment": "INTEGER",
    "ck_sync_state": "INTEGER",
    "ck_server_change_token_blob": "BLOB",
    "ck_record_id": "TEXT",
    "original_guid": "TEXT",
    "sr_ck_record_id": "TEXT",
    "sr_ck_sync_state": "INTEGER",
    "sr_ck_server_change_token_blob": "BLOB",
    "is_commsafety_sensitive": "INTEGER",
    "emoji_image_content_identifier": "TEXT",
    "emoji_image_short_description": "TEXT",
    "preview_generation_state": "INTEGER",
    "preflight_info": "BLOB",
    "sensitivity_analysis": "INTEGER",
    "fields_needing_sync": "INTEGER",
}


def db_sms_table_attachment_update_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        str_temp = '"{}"={}'.format(
            key, sql_value_gen(db_sms_table_attachment_datatype_mapping, key, row[key])
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_attachment_update(
    cursor: sqlite3.Cursor, attach_row_id: int, attach_row_data: sqlite3.Row
):
    list_str_update = db_sms_table_attachment_update_data_list(attach_row_data)
    sql = 'UPDATE "attachment" SET {} WHERE "ROWID"={};'.format(
        ", ".join(list_str_update), attach_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_attachment_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        list_temp.append('"{}"'.format(key))
    return list_temp


def db_sms_table_attachment_insert_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        str_temp = sql_value_gen(
            db_sms_table_attachment_datatype_mapping, key, row[key]
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_attachment_insert(
    cursor: sqlite3.Cursor, row_data: sqlite3.Row
) -> list:
    list_column_names = db_sms_table_attachment_insert_column_list(row_data)
    list_row_values = db_sms_table_attachment_insert_data_list(row_data)
    sql = 'INSERT INTO "attachment" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_attachment_match_by_attach_row_id(
    cursor: sqlite3.Cursor, attach_row_id: int
) -> list:
    sql = 'SELECT * FROM "attachment" WHERE "ROWID"={};'.format(attach_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_attachment_match_by_guid(
    cursor: sqlite3.Cursor, attach_guid: str
) -> list:
    sql = 'SELECT * FROM "attachment" WHERE "guid"=\'{}\';'.format(attach_guid)
    return db_cursor_execute(sql, cursor)
