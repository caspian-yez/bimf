#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_sms_table_chat_datatype_mapping = {
    "guid": "TEXT",
    "style": "INTEGER",
    "state": "INTEGER",
    "account_id": "TEXT",
    "properties": "BLOB",
    "chat_identifier": "TEXT",
    "service_name": "TEXT",
    "room_name": "TEXT",
    "account_login": "TEXT",
    "is_archived": "INTEGER",
    "last_addressed_handle": "TEXT",
    "display_name": "TEXT",
    "group_id": "TEXT",
    "is_filtered": "INTEGER",
    "successful_query": "INTEGER",
    "engram_id": "TEXT",
    "server_change_token": "TEXT",
    "ck_sync_state": "INTEGER",
    "last_read_message_timestamp": "INTEGER",
    "ck_record_system_property_blob": "BLOB",
    "original_group_id": "TEXT",
    "sr_server_change_token": "TEXT",
    "sr_ck_sync_state": "INTEGER",
    "cloudkit_record_id": "TEXT",
    "sr_cloudkit_record_id": "TEXT",
    "last_addressed_sim_id": "TEXT",
    "is_blackholed": "INTEGER",
    "syndication_date": "INTEGER",
    "syndication_type": "INTEGER",
    "is_recovered": "INTEGER",
    "is_deleting_incoming_messages": "INTEGER",
    "is_pending_review": "INTEGER",
}


def db_sms_table_chat(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "chat";'
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_update_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        str_temp = '"{}"={}'.format(
            key, sql_value_gen(db_sms_table_chat_datatype_mapping, key, row[key])
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_chat_update(
    cursor: sqlite3.Cursor, chat_row_id: int, chat_row_data: sqlite3.Row
):
    list_str_update = db_sms_table_chat_update_data_list(chat_row_data)
    sql = 'UPDATE "attachment" SET {} WHERE "ROWID"={};'.format(
        ", ".join(list_str_update), chat_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        list_temp.append(key)
    return list_temp


def db_sms_table_chat_insert_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        str_temp = sql_value_gen(db_sms_table_chat_datatype_mapping, key, row[key])
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_chat_insert(cursor: sqlite3.Cursor, chat_row_data: sqlite3.Row):
    list_column_names = db_sms_table_chat_insert_column_list(chat_row_data)
    list_row_values = db_sms_table_chat_insert_data_list(chat_row_data)
    sql = 'INSERT INTO "attachment" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_match_by_chat_identifier(
    cursor: sqlite3.Cursor, chat_identifier: str
) -> list:
    sql = 'SELECT * FROM "chat" WHERE "chat_identifier"=\'{}\';'.format(chat_identifier)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat" WHERE "ROWID"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat" WHERE "ROWID"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)
