#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_manifest_table_files_datatype_mapping = {
    "fileID": "TEXT",
    "domain": "TEXT",
    "relativePath": "TEXT",
    "flags": "INTEGER",
    "file": "BLOB",
}


def db_manifest_table_files_update_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "fileID" == key:
            continue
        str_temp = '"{}"={}'.format(
            key, sql_value_gen(db_manifest_table_files_datatype_mapping, key, row[key])
        )
        list_temp.append(str_temp)
    return list_temp


def db_manifest_table_files_update(cursor: sqlite3.Cursor, files_row_data: sqlite3.Row):
    list_str_update = db_manifest_table_files_update_data_list(files_row_data)
    sql = 'UPDATE "Files" SET {} WHERE "fileID"={};'.format(
        ", ".join(list_str_update), files_row_data["fileID"]
    )
    return db_cursor_execute(sql, cursor)


def db_manifest_table_files_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        list_temp.append(key)
    return list_temp


def db_manifest_table_files_insert_data_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        str_temp = sql_value_gen(
            db_manifest_table_files_datatype_mapping, key, row[key]
        )
        list_temp.append(str_temp)
    return list_temp


def db_manifest_table_files_insert(cursor: sqlite3.Cursor, files_row_data: sqlite3.Row):
    list_column_names = db_manifest_table_files_insert_column_list(files_row_data)
    list_row_values = db_manifest_table_files_insert_data_list(files_row_data)
    sql = 'INSERT INTO "Files" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)


def db_manifest_table_files(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "Files";'
    return db_cursor_execute(sql, cursor)


def db_manifest_table_files_relativepath_match_by_attach_guid(
    cursor: sqlite3.Cursor, attach_guid: str
) -> list:
    sql = 'SELECT * FROM "Files" WHERE "relativePath" LIKE \'%{}%\' AND "flags"=1;'.format(
        attach_guid
    )
    return db_cursor_execute(sql, cursor)


def db_manifest_table_files_match_by_file_id(
    cursor: sqlite3.Cursor, file_id: str
) -> list:
    sql = 'SELECT * FROM "Files" WHERE "fileID"=\'{}\';'.format(file_id)
    return db_cursor_execute(sql, cursor)


def db_manifest_table_files_find_sms_db(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "Files" WHERE "relativePath"=\'Library/SMS/sms.db\';'
    return db_cursor_execute(sql, cursor)


def db_manifest_table_files_delete_by_fileid(
    cursor: sqlite3.Cursor, file_id: int
) -> list:
    sql = 'DELETE FROM "Files" WHERE "fileID"=\'{}\';'.format(file_id)
    return db_cursor_execute(sql, cursor)
