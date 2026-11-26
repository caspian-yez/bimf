#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_sms_table_handle_datatype_mapping: dict = {
    "id": "TEXT",
    "country": "TEXT",
    "service": "TEXT",
    "uncanonicalized_id": "TEXT",
    "person_centric_id": "TEXT",
}


def db_sms_table_handle_update_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        str_temp = '"{}"={}'.format(
            key, sql_value_gen(db_sms_table_handle_datatype_mapping, key, row[key])
        )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_handle_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        list_temp.append(key)
    return list_temp


def db_sms_table_handle_insert_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        str_temp = sql_value_gen(db_sms_table_handle_datatype_mapping, key, row[key])
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_handle_match_by_handle_row_id(
    cursor: sqlite3.Cursor, handle_row_id: int
) -> list:
    sql = 'SELECT * FROM "handle" WHERE "ROWID"={};'.format(handle_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_handle_match_by_handle_id_and_service(
    cursor: sqlite3.Cursor, id: str, service: str
) -> list:
    sql = 'SELECT * FROM "handle" WHERE "id"=\'{}\' AND "service"=\'{}\';'.format(
        id, service
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_handle_update(
    cursor: sqlite3.Cursor, handle_row_id: int, row_data: sqlite3.Row
) -> list:
    list_str_update = db_sms_table_handle_update_data_list(row_data)
    sql = 'UPDATE "handle" SET {} WHERE "ROWID"={};'.format(
        ", ".join(list_str_update), handle_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_handle_insert(cursor: sqlite3.Cursor, row_data: sqlite3.Row) -> list:
    list_column_names = db_sms_table_handle_insert_column_list(row_data)
    list_row_values = db_sms_table_handle_insert_data_list(row_data)
    sql = 'INSERT INTO "handle" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)
