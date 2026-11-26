#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *


def db_sms_table_chat_service_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_service" WHERE "chat"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_service_match_by_chat_row_id_and_service(
    cursor: sqlite3.Cursor, chat_row_id: int, service: str
) -> list:
    sql = 'SELECT * FROM "chat_service" WHERE "chat"={} AND service=\'{}\';'.format(
        chat_row_id, service
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_service_insert(
    cursor: sqlite3.Cursor, chat_row_id: int, service: str
) -> list:
    sql = 'INSERT INTO "chat_service" ("service", "chat") VALUES (\'{}\', {}));'.format(
        service,
        chat_row_id,
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_chat_service_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_service" WHERE "chat"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)
