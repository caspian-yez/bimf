#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import sqlite3


def sql_value_gen(mapping: dict, key: str, value) -> str:
    match mapping[key]:
        case "TEXT":
            if value is None:
                return "NULL"
            else:
                return "'{}'".format(value)
        case "INTEGER" | "REAL":
            if value is None:
                return "NULL"
            else:
                return "{}".format(value)
        case "BLOB":
            if value is None:
                return "NULL"
            else:
                return "X'{}'".format(value.hex())
        case _:
            assert False, "sql_value_gen() Unknown data type: {}".format(mapping[key])


def db_cursor_execute(sql: str, cursor: sqlite3.Cursor) -> list:
    print("SQL: {}".format(sql))
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_recoverable_message_join_delete_all(
    cursor: sqlite3.Cursor,
) -> list:
    sql = 'DELETE FROM "chat_recoverable_message_join";'
    return db_cursor_execute(sql, cursor)


def db_sms_table_deleted_messages_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "deleted_messages";'
    return db_cursor_execute(sql, cursor)


def db_sms_table_sync_chat_slice_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "sync_chat_slice" WHERE "chat"={};'.format(chat_row_id)
    return db_cursor_execute(sql, cursor)


def db_sms_table_sync_deleted_attachments_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "sync_deleted_attachments";'
    return db_cursor_execute(sql, cursor)


def db_sms_table_sync_deleted_chats_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "sync_deleted_chats";'
    return db_cursor_execute(sql, cursor)


def db_sms_table_sync_deleted_messages_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "sync_deleted_messages";'
    return db_cursor_execute(sql, cursor)


def db_sms_trigger_drop_before_delete_chat_update_sync_chat_deletes(
    cursor: sqlite3.Cursor,
) -> list:
    sql = 'DROP TRIGGER "before_delete_chat_update_sync_chat_deletes";'
    return db_cursor_execute(sql, cursor)


def db_sms_trigger_create_before_delete_chat_update_sync_chat_deletes(
    cursor: sqlite3.Cursor,
) -> list:
    sql = 'CREATE TRIGGER "before_delete_chat_update_sync_chat_deletes" \
BEFORE DELETE ON chat WHEN is_mic_enabled() = 1 \
BEGIN   \
    INSERT INTO sync_deleted_chats (guid, recordID, timestamp)  \
    SELECT guid_for_chat(OLD.chat_identifier, scl.service_name, OLD.style, scl.filter_action, scl.filter_sub_action), scl.ck_record_id, m.date  \
    FROM sync_chat_slice scl    \
    INNER JOIN message m ON m.rowid = ( \
        SELECT m.rowid FROM chat_recoverable_message_join crmj  \
        INNER JOIN message m ON m.rowid = crmj.message_id   \
        WHERE chat_id = scl.chat    \
        ORDER BY m.date DESC    \
        LIMIT 1 \
    )   \
    WHERE OLD.rowid = scl.chat  \
    AND scl.ck_record_id IS NOT NULL;   \
END;'
    return db_cursor_execute(sql, cursor)
