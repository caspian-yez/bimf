#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import sys
import os
import datetime
import zoneinfo
import sqlite3
import email.message
import email.utils

COCOA_TIMESTAMP_UNIX_TIMESTAMP_DIFF_SECONDS = 978307200


def auto_dec_seconds_or_nanoseconds(cocoa_timestamp):
    """
    this function is limited
    won't work after 2032-09-09
    """
    if 0 == cocoa_timestamp:
        return "ns"
    if datetime.datetime.now().year > 2030:
        return "unknow"
    if cocoa_timestamp / 1000000000 > 1:
        return "ns"
    else:
        return "s"


def get_attachment_info_from_file_db(
    db_file_cursor: sqlite3.Cursor, guid: str, base_path: str
) -> dict:
    result: dict = {"result": False, "path": ""}
    db_file_cursor.execute(
        "SELECT * FROM Files WHERE relativePath LIKE '%{}%';".format(guid)
    )
    db_file_rows = db_file_cursor.fetchall()
    if 1 == len(db_file_rows):
        for db_file_row in db_file_rows:
            result["result"] = True
            result["path"] = os.path.join(
                base_path, db_file_row["fileID"][0:2], db_file_row["fileID"]
            )
    else:
        print("ERROR when try to find file using GUID {}".format(guid))

    return result


def get_attachment_info(db_sms_cursor: sqlite3.Cursor, attach_id: int) -> dict:
    result: dict = {"result": False, "guid": "", "transfer_name": "", "total_bytes": 0}
    # CREATE TABLE attachment (
    # ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    # guid TEXT UNIQUE NOT NULL,
    # created_date INTEGER DEFAULT 0,
    # start_date INTEGER DEFAULT 0,
    # filename TEXT,
    # uti TEXT,
    # mime_type TEXT,
    # transfer_state INTEGER DEFAULT 0,
    # is_outgoing INTEGER DEFAULT 0,
    # user_info BLOB,
    # transfer_name TEXT,
    # total_bytes INTEGER DEFAULT 0,
    # is_sticker INTEGER DEFAULT 0,
    # sticker_user_info BLOB,
    # attribution_info BLOB,
    # hide_attachment INTEGER DEFAULT 0)
    db_sms_cursor.execute("SELECT * FROM attachment WHERE ROWID={}".format(attach_id))
    db_attachment_rows = db_sms_cursor.fetchall()
    if 1 == len(db_attachment_rows):
        for db_attachment_row in db_attachment_rows:
            result["result"] = True
            result["guid"] = db_attachment_row["guid"]
            result["transfer_name"] = db_attachment_row["transfer_name"]
            result["mime_type"] = db_attachment_row["mime_type"]
            result["total_bytes"] = db_attachment_row["total_bytes"]
    else:
        print("ERROR when try to find attachment using attach_id: {}".format(attach_id))

    return result


def get_attachment_name_and_path(
    db_file_cursor: sqlite3.Cursor,
    db_sms_cursor: sqlite3.Cursor,
    row_id: int,
    base_path: str,
) -> dict:
    # one attachment info:
    # "name": "",
    # "path": "",
    # "size": 0,
    # "mime_type": "",
    result: dict = {"result": False, "attachments_list": None}
    attachments_list: list = []
    # CREATE TABLE message_attachment_join (
    # message_id INTEGER REFERENCES message (ROWID) ON DELETE CASCADE,
    # attachment_id INTEGER REFERENCES attachment (ROWID) ON DELETE CASCADE,
    # UNIQUE(message_id, attachment_id))
    db_sms_cursor.execute(
        "SELECT * FROM message_attachment_join WHERE message_id={}".format(row_id)
    )
    db_message_attachment_rows = db_sms_cursor.fetchall()
    for db_msg_attach_row in db_message_attachment_rows:
        attachment_info = get_attachment_info(
            db_sms_cursor, db_msg_attach_row["attachment_id"]
        )
        if attachment_info["result"]:
            attachment_info_in_file_db = get_attachment_info_from_file_db(
                db_file_cursor, attachment_info["guid"], base_path
            )
            if attachment_info_in_file_db["result"]:
                one_attachemnt_info: dict = {}
                one_attachemnt_info["name"] = attachment_info["transfer_name"]
                one_attachemnt_info["path"] = attachment_info_in_file_db["path"]
                one_attachemnt_info["size"] = attachment_info["total_bytes"]
                one_attachemnt_info["mime_type"] = attachment_info["mime_type"]
                attachments_list.append(one_attachemnt_info)

    if 0 != len(attachments_list):
        result["result"] = True
        result["attachments_list"] = attachments_list
    else:
        print("ERROR when try to find attachment id using msg id {}".format(row_id))

    return result


def get_phone_number_by_handle(cursor: sqlite3.Cursor, handle: int):
    # CREATE TABLE handle (
    # ROWID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    # id TEXT NOT NULL,
    # country TEXT,
    # service TEXT NOT NULL,
    # uncanonicalized_id TEXT,
    # UNIQUE (id, service) )
    phone_number = None
    cursor.execute("SELECT * FROM handle WHERE ROWID={}".format(handle))
    db_handle_rows = cursor.fetchall()
    if 1 == len(db_handle_rows):
        for handle_row in db_handle_rows:
            phone_number = handle_row["id"]
    else:
        print(
            "ERROR: None or more than one phone number found using handle {}".format(
                handle
            )
        )

    return phone_number


def save_as_eml(eml_text: str, guid_name: str):
    filename = guid_name + ".eml"
    f = open(filename, "w")
    f.write(eml_text)
    f.close()


def sms_db_process(db_files_cursor: sqlite3.Cursor, db_sms_path: str, base_path: str):
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

    # CREATE TABLE message (
    # ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    # guid TEXT UNIQUE NOT NULL,
    # text TEXT,
    # replace INTEGER DEFAULT 0,
    # service_center TEXT,
    # handle_id INTEGER DEFAULT 0,
    # subject TEXT,
    # country TEXT,
    # attributedBody BLOB,
    # version INTEGER DEFAULT 0,
    # type INTEGER DEFAULT 0,
    # service TEXT,
    # account TEXT,
    # account_guid TEXT,
    # error INTEGER DEFAULT 0,
    # date INTEGER,
    # date_read INTEGER,
    # date_delivered INTEGER,
    # is_delivered INTEGER DEFAULT 0,
    # is_finished INTEGER DEFAULT 0,
    # is_emote INTEGER DEFAULT 0,
    # is_from_me INTEGER DEFAULT 0,
    # is_empty INTEGER DEFAULT 0,
    # is_delayed INTEGER DEFAULT 0,
    # is_auto_reply INTEGER DEFAULT 0,
    # is_prepared INTEGER DEFAULT 0,
    # is_read INTEGER DEFAULT 0,
    # is_system_message INTEGER DEFAULT 0,
    # is_sent INTEGER DEFAULT 0,
    # has_dd_results INTEGER DEFAULT 0,
    # is_service_message INTEGER DEFAULT 0,
    # is_forward INTEGER DEFAULT 0,
    # was_downgraded INTEGER DEFAULT 0,
    # is_archive INTEGER DEFAULT 0,
    # cache_has_attachments INTEGER DEFAULT 0,
    # cache_roomnames TEXT,
    # was_data_detected INTEGER DEFAULT 0,
    # was_deduplicated INTEGER DEFAULT 0,
    # is_audio_message INTEGER DEFAULT 0,
    # is_played INTEGER DEFAULT 0,
    # date_played INTEGER,
    # item_type INTEGER DEFAULT 0,
    # other_handle INTEGER DEFAULT 0,
    # group_title TEXT,
    # group_action_type INTEGER DEFAULT 0,
    # share_status INTEGER DEFAULT 0,
    # share_direction INTEGER DEFAULT 0,
    # is_expirable INTEGER DEFAULT 0,
    # expire_state INTEGER DEFAULT 0,
    # message_action_type INTEGER DEFAULT 0,
    # message_source INTEGER DEFAULT 0,
    # associated_message_guid TEXT,
    # associated_message_type INTEGER DEFAULT 0,
    # balloon_bundle_id TEXT,
    # payload_data BLOB,
    # expressive_send_style_id TEXT,
    # associated_message_range_location INTEGER DEFAULT 0,
    # associated_message_range_length INTEGER DEFAULT 0,
    # time_expressive_send_played INTEGER,
    # message_summary_info BLOB,
    # ck_sync_state INTEGER DEFAULT 0,
    # ck_record_id TEXT DEFAULT NULL,
    # ck_record_change_tag TEXT DEFAULT NULL,
    # destination_caller_id TEXT DEFAULT NULL,
    # sr_ck_sync_state INTEGER DEFAULT 0,
    # sr_ck_record_id TEXT DEFAULT NULL,
    # sr_ck_record_change_tag TEXT DEFAULT NULL,
    # is_corrupt INTEGER DEFAULT 0
    # )
    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()
    db_sms_cursor.execute("SELECT * FROM message")
    db_sms_rows = db_sms_cursor.fetchall()

    local_timezone = zoneinfo.ZoneInfo("UTC")

    for db_sms_row in db_sms_rows:
        msg = email.message.EmailMessage()

        if db_sms_row["account"] is None:
            msg["Account"] = ""
        else:
            msg["Account"] = db_sms_row["account"]

        if db_sms_row["account_guid"] is None:
            msg["Account-GUID"] = ""
        else:
            msg["Account-GUID"] = db_sms_row["account_guid"]

        msg["Application"] = "iMessage"

        match (auto_dec_seconds_or_nanoseconds(db_sms_row["date"])):
            case "s":
                msg["Date-Cocoa-Timestamp-Seconds"] = str(db_sms_row["date"])
            case "ns":
                msg["Date-Cocoa-Timestamp-Nanoseconds"] = str(db_sms_row["date"])
            case _:
                print(
                    "ERROR: {} cannot determin date timestamp unit".format(
                        db_sms_row["guid"]
                    )
                )
                break

        match (auto_dec_seconds_or_nanoseconds(db_sms_row["date_read"])):
            case "s":
                msg["Date-Read-Cocoa-Timestamp-Seconds"] = str(db_sms_row["date_read"])
            case "ns":
                msg["Date-Read-Cocoa-Timestamp-Nanoseconds"] = str(
                    db_sms_row["date_read"]
                )
            case _:
                print(
                    "ERROR: {} cannot determin date_read timestamp unit".format(
                        db_sms_row["guid"]
                    )
                )
                break

        match (auto_dec_seconds_or_nanoseconds(db_sms_row["date_delivered"])):
            case "s":
                msg["Date-Delivered-Cocoa-Timestamp-Seconds"] = str(
                    db_sms_row["date_delivered"]
                )
            case "ns":
                msg["Date-Delivered-Cocoa-Timestamp-Nanoseconds"] = str(
                    db_sms_row["date_delivered"]
                )
            case _:
                print(
                    "ERROR: {} cannot determin date_delivered timestamp unit".format(
                        db_sms_row["guid"]
                    )
                )
                break

        msg["GUID"] = db_sms_row["guid"]

        if db_sms_row["service"] is None:
            msg["Service"] = ""
        else:
            msg["Service"] = db_sms_row["service"]

        if db_sms_row["service_center"] is None:
            msg["Service-Center"] = ""
        else:
            msg["Service-Center"] = db_sms_row["service_center"]

        match (auto_dec_seconds_or_nanoseconds(db_sms_row["date"])):
            case "s":
                local_datetime = datetime.datetime.fromtimestamp(
                    db_sms_row["date"] + COCOA_TIMESTAMP_UNIX_TIMESTAMP_DIFF_SECONDS,
                    local_timezone,
                )
            case "ns":
                local_datetime = datetime.datetime.fromtimestamp(
                    db_sms_row["date"] / 1000000000
                    + COCOA_TIMESTAMP_UNIX_TIMESTAMP_DIFF_SECONDS,
                    local_timezone,
                )
            case _:
                print(
                    "ERROR: {} cannot determin date timestamp unit".format(
                        db_sms_row["guid"]
                    )
                )
                break

        msg["Date"] = email.utils.format_datetime(local_datetime)

        phone_number = get_phone_number_by_handle(
            db_sms_cursor, db_sms_row["handle_id"]
        )
        if phone_number is None:
            print("ERROR: cannot find phone number")
            break

        my_phone_number = sys.argv[2]
        if db_sms_row["destination_caller_id"] is not None:
            my_phone_number = db_sms_row["destination_caller_id"]

        if 0 == db_sms_row["is_from_me"]:
            msg["From"] = phone_number
            msg["To"] = my_phone_number
        else:
            msg["From"] = my_phone_number
            msg["To"] = phone_number

        if db_sms_row["subject"] is None:
            msg["Subject"] = ""
        else:
            msg["Subject"] = db_sms_row["subject"]

        if db_sms_row["text"] is None:
            continue
        else:
            msg.set_content(db_sms_row["text"])

        if 0 != db_sms_row["cache_has_attachments"]:
            attachments = get_attachment_name_and_path(
                db_files_cursor, db_sms_cursor, db_sms_row["ROWID"], base_path
            )
            if attachments["result"]:
                for attachment in attachments["attachments_list"]:
                    if os.path.exists(attachment["path"]):
                        file = open(attachment["path"], "rb")
                        file_data = file.read()
                        if attachment["size"] != len(file_data):
                            print(
                                "msg guid: {}, {} file size mismatch, actual: {}, size in database: {}".format(
                                    db_sms_row["guid"],
                                    attachment["name"],
                                    len(file_data),
                                    attachment["size"],
                                )
                            )
                        maintype, subtype = attachment["mime_type"].split("/", 1)
                        msg.add_attachment(
                            file_data,
                            maintype=maintype,
                            subtype=subtype,
                            filename=attachment["name"],
                        )
                        file.close()
                    else:
                        print(
                            "msg guid: {}, cannot find {} for {}".format(
                                db_sms_row["guid"],
                                attachment["path"],
                                attachment["name"],
                            )
                        )

        save_as_eml(msg.as_string(), db_sms_row["guid"])

    db_sms_conn.close()


def main():
    if 3 != len(sys.argv):
        print("need parameters: <database filepath> <phone number>")
        return

    print(sys.argv[0])  # program name
    print(sys.argv[1])  # unencrypted backup path
    print(sys.argv[2])  # reserved

    # CREATE TABLE Files (
    # fileID TEXT PRIMARY KEY,
    # domain TEXT,
    # relativePath TEXT,
    # flags INTEGER,
    # file BLOB
    # )
    db_files_path = os.path.join(sys.argv[1], "Manifest.db")
    print(db_files_path)
    db_files_conn = sqlite3.connect(db_files_path)
    db_files_conn.row_factory = sqlite3.Row

    db_files_cursor = db_files_conn.cursor()
    db_files_cursor.execute(
        'SELECT * FROM Files WHERE relativePath = "Library/SMS/sms.db"'
    )
    db_files_rows = db_files_cursor.fetchall()

    if 1 == len(db_files_rows):
        for db_files_row in db_files_rows:
            db_sms_path = os.path.join(
                sys.argv[1],
                db_files_row["fileID"][0:2],
                db_files_row["fileID"],
            )
            sms_db_process(db_files_cursor, db_sms_path, sys.argv[1])
    else:
        print('ERROR: Multiple "Library/SMS/sms.db" found')

    db_files_conn.close()


if __name__ == "__main__":
    main()
