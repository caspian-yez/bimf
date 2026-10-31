#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import sqlite3


def db_manifest_table_files(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "Files";'
    return cursor.execute(sql).fetchall()


def db_manifest_table_files_relativepath_match_by_attach_guid(
    cursor: sqlite3.Cursor, attach_guid: str
) -> list:
    sql = (
        'SELECT * FROM "Files" WHERE "relativePath" LIKE "%{}%" AND "flags"=1;'.format(
            attach_guid
        )
    )
    return cursor.execute(sql).fetchall()


def db_manifest_table_files_find_sms_db(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "Files" WHERE "relativePath"="Library/SMS/sms.db";'
    return cursor.execute(sql).fetchall()


def db_manifest_table_files_delete_by_fileid(
    cursor: sqlite3.Cursor, file_id: int
) -> list:
    sql = 'DELETE FROM "Files" WHERE "fileID" = "{}";'.format(file_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_attachment_match_by_attach_row_id(
    cursor: sqlite3.Cursor, attach_row_id: int
) -> list:
    sql = 'SELECT * FROM "attachment" WHERE "ROWID"={};'.format(attach_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "chat";'
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat" WHERE "ROWID"={};'.format(chat_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_handle_join_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_handle_join" WHERE "chat_id"={};'.format(chat_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_handle_join_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_handle_join" WHERE "chat_id"={};'.format(chat_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_message_join_match_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_message_join" WHERE "message_id"={};'.format(msg_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_message_join_match_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'SELECT * FROM "chat_message_join" WHERE "chat_id"={};'.format(chat_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_message_join_delete_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_message_join" WHERE "message_id"={};'.format(msg_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_chat_service_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "chat_service" WHERE "chat"={};'.format(chat_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_deleted_messages_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "deleted_messages";'
    return cursor.execute(sql).fetchall()


def db_sms_table_handle_match_by_handle_row_id(
    cursor: sqlite3.Cursor, handle_row_id: int
) -> list:
    sql = 'SELECT * FROM "handle" WHERE "ROWID"={};'.format(handle_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_message(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "message";'
    return cursor.execute(sql).fetchall()


def db_sms_table_message_delete_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'DELETE FROM "message" WHERE "ROWID"={};'.format(msg_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_message_attachment_join_match_by_message_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'SELECT * FROM "message_attachment_join" WHERE "message_id"={};'.format(
        msg_row_id
    )
    return cursor.execute(sql).fetchall()


def db_sms_table_message_attachment_join_delete_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'DELETE FROM "message_attachment_join" WHERE "message_id"={};'.format(
        msg_row_id
    )
    return cursor.execute(sql).fetchall()


def db_sms_table_sync_chat_slice_delete_by_chat_row_id(
    cursor: sqlite3.Cursor, chat_row_id: int
) -> list:
    sql = 'DELETE FROM "sync_chat_slice" WHERE "chat"={};'.format(chat_row_id)
    return cursor.execute(sql).fetchall()


def db_sms_table_sync_deleted_attachments_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "sync_deleted_attachments";'
    return cursor.execute(sql).fetchall()


def db_sms_table_sync_deleted_chats_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "sync_deleted_chats";'
    return cursor.execute(sql).fetchall()


def db_sms_table_sync_deleted_messages_delete_all(cursor: sqlite3.Cursor) -> list:
    sql = 'DELETE FROM "sync_deleted_messages";'
    return cursor.execute(sql).fetchall()


def db_sms_trigger_drop_before_delete_chat_update_sync_chat_deletes(
    cursor: sqlite3.Cursor,
) -> list:
    sql = 'DROP TRIGGER "before_delete_chat_update_sync_chat_deletes";'
    return cursor.execute(sql).fetchall()


def db_sms_trigger_create_before_delete_chat_update_sync_chat_deletes(
    cursor: sqlite3.Cursor,
) -> list:
    sql = 'CREATE TRIGGER "before_delete_chat_update_sync_chat_deletes"     \
BEFORE DELETE ON chat WHEN is_mic_enabled() = 1\
BEGIN\
    INSERT INTO sync_deleted_chats (guid, recordID, timestamp) \
    SELECT guid_for_chat(OLD.chat_identifier, scl.service_name, OLD.style, scl.filter_action, scl.filter_sub_action), scl.ck_record_id, m.date \
    FROM sync_chat_slice scl \
    INNER JOIN message m ON m.rowid = ( \
        SELECT m.rowid FROM chat_recoverable_message_join crmj \
        INNER JOIN message m ON m.rowid = crmj.message_id \
        WHERE chat_id = scl.chat \
        ORDER BY m.date DESC \
        LIMIT 1 \
    ) \
    WHERE OLD.rowid = scl.chat \
    AND scl.ck_record_id IS NOT NULL; \
END;'
    return cursor.execute(sql).fetchall()
