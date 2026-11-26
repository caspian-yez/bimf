#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_sms_table_chat_message_join_datatype_mapping = {
    "message_date": "INTEGER",
    "index_state": "INTEGER",
    "filter_action": "INTEGER",
    "filter_sub_action": "INTEGER",
}


def db_sms_table_chat_message_join_match_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_message_join" WHERE "message_id"={};'.format(msg_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_message_join_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_message_join" WHERE "chat_id"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_message_join_match_by_chat_row_id_and_message_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int, msg_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_message_join" WHERE "chat_id"={} AND "message_id"={};'.format(
        chat_row_id, msg_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_message_join_update_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "chat_id" == key or "message_id" == key:
            continue
        str_temp = '"{}"={}'.format(
            key,
            sql_value_gen(
                db_sms_table_chat_message_join_datatype_mapping, key, row[key]
            ),
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_chat_message_join_update(
    cursor: sqlite3.Cursor,
    chat_row_id: int,
    msg_row_id: int,
    chat_msg_join_row_data: sqlite3.Row,
) -> list:
    list_str_update = db_sms_table_chat_message_join_update_data_list(
        chat_msg_join_row_data
    )
    if 0 == len(list_str_update):
        return list()
    sql = 'UPDATE "chat_message_join" SET {} WHERE "chat_id"={} AND "message_id"={};'.format(
        ", ".join(list_str_update), chat_row_id, msg_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_message_join_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        list_temp.append('"{}"'.format(key))
    return list_temp


def db_sms_table_chat_message_join_insert_data_list(
    row: sqlite3.Row, chat_row_id: int, msg_row_id: int
) -> list:
    list_temp = list()
    list_temp.append("{}".format(chat_row_id))
    list_temp.append("{}".format(msg_row_id))
    keys = row.keys()
    for key in keys:
        if "chat_id" == key or "message_id" == key:
            continue
        str_temp = sql_value_gen(
            db_sms_table_chat_message_join_datatype_mapping, key, row[key]
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_chat_message_join_insert(
    cursor: sqlite3.Cursor,
    chat_row_id: int,
    msg_row_id: int,
    chat_msg_join_row_data: sqlite3.Row,
) -> list:
    list_column_names = db_sms_table_chat_message_join_insert_column_list(
        chat_msg_join_row_data
    )
    list_row_values = db_sms_table_chat_message_join_insert_data_list(
        chat_msg_join_row_data, chat_row_id, msg_row_id
    )
    sql = 'INSERT INTO "chat_message_join" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_message_join_delete_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_message_join" WHERE "message_id"={};'.format(msg_row_id)
    return db_cursor_execute(sql, cursor)
