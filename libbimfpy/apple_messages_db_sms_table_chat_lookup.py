#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_sms_table_chat_lookup_datatype_mapping = {
    "identifier": "TEXT",
    "domain": "TEXT",
    "chat": "INTEGER",
    "priority": "INTEGER",
}


def db_sms_table_chat_lookup_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_lookup" WHERE "chat"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_lookup_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_lookup" WHERE "chat"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_lookup_update_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "chat" == key:
            continue
        str_temp = '"{}"={}'.format(
            key, sql_value_gen(db_sms_table_chat_lookup_datatype_mapping, key, row[key])
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_chat_lookup_update(
    cursor: sqlite3.Cursor, chat_lookup_row_data: sqlite3.Row, chat_row_id: int
):
    list_str_update = db_sms_table_chat_lookup_update_data_list(chat_lookup_row_data)
    sql = 'UPDATE "chat_lookup" SET {} WHERE "chat"={};'.format(
        ", ".join(list_str_update), chat_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_lookup_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        list_temp.append(key)
    return list_temp


def db_sms_table_chat_lookup_insert_data_list(
    row: sqlite3.Row, chat_row_id: int
) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "chat" == key:
            str_temp = sql_value_gen(
                db_sms_table_chat_lookup_datatype_mapping, key, chat_row_id
            )
        else:
            str_temp = sql_value_gen(
                db_sms_table_chat_lookup_datatype_mapping, key, row[key]
            )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_chat_lookup_insert(
    cursor: sqlite3.Cursor, chat_lookup_row_data: sqlite3.Row, chat_row_id: int
):
    list_column_names = db_sms_table_chat_lookup_insert_column_list(
        chat_lookup_row_data
    )
    list_row_values = db_sms_table_chat_lookup_insert_data_list(
        chat_lookup_row_data, chat_row_id
    )
    sql = 'INSERT INTO "chat_lookup" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)
