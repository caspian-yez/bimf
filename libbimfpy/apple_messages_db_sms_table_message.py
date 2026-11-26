#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sqlite3
from .apple_messages_db import *

db_sms_table_message_datatype_mapping: dict = {
    "guid": "TEXT",
    "text": "TEXT",
    "replace": "INTEGER",
    "service_center": "TEXT",
    "handle_id": "INTEGER",
    "subject": "TEXT",
    "country": "TEXT",
    "attributedBody": "BLOB",
    "version": "INTEGER",
    "type": "INTEGER",
    "service": "TEXT",
    "account": "TEXT",
    "account_guid": "TEXT",
    "error": "INTEGER",
    "date": "INTEGER",
    "date_read": "INTEGER",
    "date_delivered": "INTEGER",
    "is_delivered": "INTEGER",
    "is_finished": "INTEGER",
    "is_emote": "INTEGER",
    "is_from_me": "INTEGER",
    "is_empty": "INTEGER",
    "is_delayed": "INTEGER",
    "is_auto_reply": "INTEGER",
    "is_prepared": "INTEGER",
    "is_read": "INTEGER",
    "is_system_message": "INTEGER",
    "is_sent": "INTEGER",
    "has_dd_results": "INTEGER",
    "is_service_message": "INTEGER",
    "is_forward": "INTEGER",
    "was_downgraded": "INTEGER",
    "is_archive": "INTEGER",
    "cache_has_attachments": "INTEGER",
    "cache_roomnames": "TEXT",
    "was_data_detected": "INTEGER",
    "was_deduplicated": "INTEGER",
    "is_audio_message": "INTEGER",
    "is_played": "INTEGER",
    "date_played": "INTEGER",
    "item_type": "INTEGER",
    "other_handle": "INTEGER",
    "group_title": "TEXT",
    "group_action_type": "INTEGER",
    "share_status": "INTEGER",
    "share_direction": "INTEGER",
    "is_expirable": "INTEGER",
    "expire_state": "INTEGER",
    "message_action_type": "INTEGER",
    "message_source": "INTEGER",
    "associated_message_guid": "TEXT",
    "associated_message_type": "INTEGER",
    "balloon_bundle_id": "TEXT",
    "payload_data": "BLOB",
    "expressive_send_style_id": "TEXT",
    "associated_message_range_location": "INTEGER",
    "associated_message_range_length": "INTEGER",
    "time_expressive_send_played": "INTEGER",
    "message_summary_info": "BLOB",
    "ck_sync_state": "INTEGER",
    "ck_record_id": "TEXT",
    "ck_record_change_tag": "TEXT",
    "destination_caller_id": "TEXT",
    "sr_ck_sync_state": "INTEGER",
    "sr_ck_record_id": "TEXT",
    "sr_ck_record_change_tag": "TEXT",
    "is_corrupt": "INTEGER",
    "reply_to_guid": "TEXT",
    "sort_id": "INTEGER",
    "is_spam": "INTEGER",
    "has_unseen_mention": "INTEGER",
    "thread_originator_guid": "TEXT",
    "thread_originator_part": "TEXT",
    "syndication_ranges": "TEXT",
    "was_delivered_quietly": "INTEGER",
    "did_notify_recipient": "INTEGER",
    "synced_syndication_ranges": "TEXT",
    "date_retracted": "INTEGER",
    "date_edited": "INTEGER",
    "was_detonated": "INTEGER",
    "part_count": "INTEGER",
    "is_stewie": "INTEGER",
    "is_kt_verified": "INTEGER",
    "is_sos": "INTEGER",
    "is_critical": "INTEGER",
    "bia_reference_id": "TEXT",
    "fallback_hash": "TEXT",
    "associated_message_emoji": "TEXT",
    "is_pending_satellite_send": "INTEGER",
    "needs_relay": "INTEGER",
    "schedule_type": "INTEGER",
    "schedule_state": "INTEGER",
    "sent_or_received_off_grid": "INTEGER",
    "date_recovered": "INTEGER",
    "is_time_sensitive": "INTEGER",
    "ck_chat_id": "TEXT",
    "index_state": "INTEGER",
    "filter_action": "INTEGER",
    "filter_sub_action": "INTEGER",
    "is_preview_sent": "INTEGER",
    "is_preview_delivered": "INTEGER",
    "date_preview_sent": "INTEGER",
    "date_preview_delivered": "INTEGER",
    "date_updated": "INTEGER",
    "retry_count": "INTEGER",
}


def db_sms_table_message(cursor: sqlite3.Cursor) -> list:
    sql = 'SELECT * FROM "message";'
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_match_by_guid(cursor: sqlite3.Cursor, msg_guid: str) -> list:
    sql = 'SELECT * FROM "message" WHERE "guid"=\'{}\';'.format(msg_guid)
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_insert_column_list(row: sqlite3.Row) -> list:
    list_temp = list()
    keys = row.keys()
    for key in keys:
        if "ROWID" == key:
            continue
        list_temp.append('"{}"'.format(key))
    return list_temp


def db_sms_table_handle_insert_data_list(
    row: sqlite3.Row, handle_id_in_row: int
) -> list:
    list_temp = list()
    keys = row.keys()
    temp_str = None
    for key in keys:
        if "ROWID" == key:
            continue
        elif "handle_id" == key:
            temp_str = sql_value_gen(
                db_sms_table_message_datatype_mapping, key, handle_id_in_row
            )
        else:
            temp_str = sql_value_gen(
                db_sms_table_message_datatype_mapping, key, row[key]
            )
        list_temp.append(temp_str)
    return list_temp


def db_sms_table_message_insert(
    cursor: sqlite3.Cursor, row_data: sqlite3.Row, handle_id_in_row: int
) -> list:
    list_column_names = db_sms_table_message_insert_column_list(row_data)
    list_row_values = db_sms_table_handle_insert_data_list(row_data, handle_id_in_row)
    sql = 'INSERT INTO "message" ({}) VALUES ({});'.format(
        ", ".join(list_column_names),
        ", ".join(list_row_values),
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_update_data_list(
    row: sqlite3.Row, handle_id_in_row: int
) -> list:
    list_temp = list()
    keys = row.keys()
    str_temp = None
    for key in keys:
        if "ROWID" == key:
            continue
        elif "handle_id" == key:
            str_temp = '"{}"={}'.format(
                key,
                sql_value_gen(
                    db_sms_table_message_datatype_mapping, key, handle_id_in_row
                ),
            )
        else:
            str_temp = '"{}"={}'.format(
                key, sql_value_gen(db_sms_table_message_datatype_mapping, key, row[key])
            )
        list_temp.append(str_temp)
    return list_temp


def db_sms_table_message_update(
    cursor: sqlite3.Cursor,
    msg_row_id: int,
    row_data: sqlite3.Row,
    handle_id_in_msg: int,
) -> list:
    list_str_update = db_sms_table_message_update_data_list(row_data, handle_id_in_msg)
    sql = 'UPDATE "message" SET {} WHERE "rowid"={};'.format(
        ", ".join(list_str_update), msg_row_id
    )
    return db_cursor_execute(sql, cursor)


def db_sms_table_message_delete_by_msg_row_id(
    cursor: sqlite3.Cursor, msg_row_id: int
) -> list:
    sql = 'DELETE FROM "message" WHERE "ROWID"={};'.format(msg_row_id)
    return db_cursor_execute(sql, cursor)
