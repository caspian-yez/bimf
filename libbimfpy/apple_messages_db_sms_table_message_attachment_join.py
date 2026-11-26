#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *


def db_sms_table_message_attachment_join_insert(
    cursor: sqlite3.Cursor, msg_row_id: int, attach_row_id: int
):
    sql = 'INSERT INTO "message_attachment_join" ("message_id", "attachment_id") VALUES ({}, {});'.format(
        msg_row_id,
        attach_row_id,
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_attachment_join_match_by_message_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'SELECT * FROM "message_attachment_join" WHERE "message_id"={};'.format(
        msg_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_attachment_join_match_by_message_row_id_and_attch_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int, attach_row_id: int
) -> list:
    sql = 'SELECT * FROM "message_attachment_join" WHERE "message_id"={} AND "attachment_id"={};'.format(
        msg_row_id, attach_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_attachment_join_delete_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'DELETE FROM "message_attachment_join" WHERE "message_id"={};'.format(
        msg_row_id
    )
    return db_cursor_execute(sql, cursor)
