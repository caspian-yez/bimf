#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *


def db_sms_table_chat_handle_join_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_handle_join" WHERE "chat_id"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_handle_join_match_by_chat_row_id_and_handle_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int, handle_row_id: int
):
    sql = 'SELECT * FROM "chat_handle_join" WHERE "chat_id"={} AND "handle_id"={};'.format(
        chat_row_id, handle_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_handle_join_insert(
    cursor: sqlite3.Cursor, chat_row_id: int, handle_row_id: int
):
    sql = 'INSERT INTO "chat_handle_join" ("chat_id", "handle_id") VALUES ({}, {});'.format(
        chat_row_id,
        handle_row_id,
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_handle_join_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_handle_join" WHERE "chat_id"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)
