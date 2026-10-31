#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
import datetime
import sqlite3
import email.message
import email.utils
import argparse
from libbimfpy.apple_messages_db import *
from libbimfpy.apple_streamtyped import *
from libbimfpy.cocoa_timestamp import *
from libbimfpy.timestamp_filename import *


def get_attachment_info_from_file_db(
    db_file_cursor: sqlite3.Cursor, guid: str, base_path: str
) -> dict:
    result: dict = {"result": False, "path": ""}
    db_file_rows = db_manifest_table_files_relativepath_match_by_attach_guid(
        db_file_cursor, guid
    )
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
    db_attachment_rows = db_sms_table_attachment_match_by_attach_row_id(
        db_sms_cursor, attach_id
    )
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
    db_message_attachment_rows = (
        db_sms_table_message_attachment_join_match_by_message_row_id(
            db_sms_cursor, row_id
        )
    )
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
        print("ERROR cannot find attachment id using msg id {}".format(row_id))

    return result


def get_phone_number_by_handle(cursor: sqlite3.Cursor, handle: int):
    phone_number = ""
    db_handle_rows = db_sms_table_handle_match_by_handle_row_id(cursor, handle)
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


def get_phone_number_by_msg_id(cursor: sqlite3.Cursor, msg_id: int) -> list:
    chat_id = None
    list_phone_numbers = list()

    chat_message_rows = db_sms_table_chat_message_join_match_by_msg_row_id(
        cursor, msg_id
    )
    if 1 == len(chat_message_rows):
        for chat_message_row in chat_message_rows:
            chat_id = chat_message_row["chat_id"]
    else:
        print(
            "ERROR: None or more than one chat id found using msg handle {}".format(
                msg_id
            )
        )
        return list_phone_numbers

    chat_handle_rows = db_sms_table_chat_handle_join_match_by_chat_row_id(
        cursor, chat_id
    )
    for chat_handle_row in chat_handle_rows:
        handle_rows = db_sms_table_handle_match_by_handle_row_id(
            cursor, chat_handle_row["handle_id"]
        )
        if 1 == len(handle_rows):
            for handle_row in handle_rows:
                list_phone_numbers.append(handle_row["id"])
        else:
            print(
                "ERROR: None or more than one handle id found using msg handle {}".format(
                    chat_handle_row["handle_id"]
                )
            )

    return list_phone_numbers


def get_chat_room_name_by_msg_id(cursor: sqlite3.Cursor, msg_id: int):
    room_name = None
    chat_msg_join_rows = db_sms_table_chat_message_join_match_by_msg_row_id(
        cursor, msg_id
    )
    if 1 == len(chat_msg_join_rows):
        chat_rows = db_sms_table_chat_match_by_chat_row_id(
            cursor, chat_msg_join_rows[0]["chat_id"]
        )
        if 1 == len(chat_rows):
            room_name = chat_rows[0]["room_name"]
        else:
            print(
                "ERROR: chat id {}, belongs to multiple chats or no chat".format(
                    chat_msg_join_rows[0]["chat_id"]
                )
            )
    else:
        print("Warning: msg id {}, belongs to multiple chats or no chat".format(msg_id))

    return room_name


def save_as_eml(eml_text: str, guid_name: str, timestamp: datetime.datetime):
    filename = get_timestamp_filename(timestamp, guid_name) + ".eml"
    if os.path.exists(filename):
        print('ERROR eml "{}"already exists'.format(filename))
    else:
        f = open(filename, "w")
        f.write(eml_text)
        f.close()


def sms_db_process(
    db_files_cursor: sqlite3.Cursor,
    db_sms_path: str,
    base_path: str,
    year: int,
    default_number: str,
    skip_write: bool,
):
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()

    db_sms_rows = db_sms_table_message(db_sms_cursor)
    for db_sms_row in db_sms_rows:

        if db_sms_row["attributedBody"] is None:
            if db_sms_row["text"] is None:
                print(
                    "msg guid: {}, both attributedBody and text is empty".format(
                        db_sms_row["guid"]
                    )
                )
                continue

        msg = email.message.EmailMessage()

        if db_sms_row["account"] is None:
            msg["Account"] = ""
        else:
            msg["Account"] = db_sms_row["account"]

        if db_sms_row["account_guid"] is None:
            msg["Account-GUID"] = ""
        else:
            msg["Account-GUID"] = db_sms_row["account_guid"]

        msg["Application"] = "Apple-Messages"

        # older database cocoa timestamp is in seconds
        msg["Date-Cocoa-Timestamp-Nanoseconds"] = str(
            get_cocoa_timestamp_in_ns(db_sms_row["date"])
        )

        # older database cocoa timestamp is in seconds
        msg["Date-Read-Cocoa-Timestamp-Nanoseconds"] = str(
            get_cocoa_timestamp_in_ns(db_sms_row["date_read"])
        )

        # older database cocoa timestamp is in seconds
        msg["Date-Delivered-Cocoa-Timestamp-Nanoseconds"] = str(
            get_cocoa_timestamp_in_ns(db_sms_row["date_delivered"])
        )

        msg["GUID"] = db_sms_row["guid"]

        room_name = get_chat_room_name_by_msg_id(db_sms_cursor, db_sms_row["ROWID"])
        if room_name is not None:
            msg["Chat-Room-Name"] = room_name

        if db_sms_row["service"] is None:
            msg["Service"] = ""
        else:
            msg["Service"] = db_sms_row["service"]

        if db_sms_row["service_center"] is None:
            msg["Service-Center"] = ""
        else:
            msg["Service-Center"] = db_sms_row["service_center"]

        # older database cocoa timestamp is in seconds
        datetime_timestamp = get_datetime_from_cocoa_timestamp(db_sms_row["date"])

        if 0 != year:
            if year != datetime_timestamp.year:
                continue

        msg["Date"] = email.utils.format_datetime(datetime_timestamp)

        sender_number = get_phone_number_by_handle(
            db_sms_cursor, db_sms_row["handle_id"]
        )
        if 0 == len(sender_number):
            print(
                "ERROR: cannot find phone number by handle_id {}".format(
                    db_sms_row["handle_id"]
                )
            )
            break

        phone_numbers = get_phone_number_by_msg_id(db_sms_cursor, db_sms_row["ROWID"])
        if 0 == len(phone_numbers):
            print(
                "ERROR: cannot find phone numbers by message id {} and chat id".format(
                    db_sms_row["ROWID"]
                )
            )
            break
        elif 1 < len(phone_numbers):
            print(
                "Warning: message id {} multiple participants".format(
                    db_sms_row["ROWID"]
                )
            )

        # older database do not have "destination_caller_id"
        my_phone_number = default_number
        if "destination_caller_id" in db_sms_row.keys():
            if db_sms_row["destination_caller_id"] is not None:
                my_phone_number = db_sms_row["destination_caller_id"]

        if 0 == db_sms_row["is_from_me"]:
            list_recipients = list()
            list_recipients.append(my_phone_number)
            for phone_number in phone_numbers:
                if sender_number != phone_number:
                    list_recipients.append(phone_number)
            msg["From"] = sender_number
            msg["To"] = ", ".join(list_recipients)
        else:
            msg["From"] = my_phone_number
            msg["To"] = ", ".join(phone_numbers)

        if db_sms_row["subject"] is None:
            msg["Subject"] = ""
        else:
            msg["Subject"] = db_sms_row["subject"]

        if db_sms_row["balloon_bundle_id"] is not None:
            print(
                "Warning: msg guid {}, balloon_bundle_id not NULL: {}".format(
                    db_sms_row["guid"], db_sms_row["balloon_bundle_id"]
                )
            )

        if db_sms_row["text"] is None:
            body_text = decode_streamtyped(db_sms_row["attributedBody"])
            if (body_text is None) or (0 == len(body_text)):
                print(
                    "ERROR: msg guid {} parse attributedBody failed".format(
                        db_sms_row["guid"]
                    )
                )
            else:
                msg.set_content(body_text)
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

        if not skip_write:
            save_as_eml(msg.as_string(), db_sms_row["guid"], datetime_timestamp)

    db_sms_conn.close()


def sms_db_check_attachments(
    db_files_cursor: sqlite3.Cursor,
    db_sms_path: str,
    base_path: str,
    year: int,
):
    if not os.path.exists(db_sms_path):
        print("Cannot find {}".format(db_sms_path))
        return
    else:
        print(db_sms_path)

    db_sms_conn = sqlite3.connect(db_sms_path)
    db_sms_conn.row_factory = sqlite3.Row
    db_sms_cursor = db_sms_conn.cursor()

    db_sms_rows = db_sms_table_message(db_sms_cursor)
    for db_sms_row in db_sms_rows:
        if db_sms_row["attributedBody"] is None:
            if db_sms_row["text"] is None:
                continue

        # older database cocoa timestamp is in seconds
        datetime_timestamp = get_datetime_from_cocoa_timestamp(db_sms_row["date"])

        if 0 != year:
            if year != datetime_timestamp.year:
                continue

        if 0 != db_sms_row["cache_has_attachments"]:
            # get text for searching
            body_text = None
            if db_sms_row["text"] is None:
                body_text = decode_streamtyped(db_sms_row["attributedBody"])
                if (body_text is None) or (0 == len(body_text)):
                    body_text = ""
            else:
                body_text = db_sms_row["text"]

            subject_text = None
            if db_sms_row["subject"] is None:
                subject_text = ""
            else:
                subject_text = db_sms_row["subject"]

            attachments = get_attachment_name_and_path(
                db_files_cursor, db_sms_cursor, db_sms_row["ROWID"], base_path
            )
            if attachments["result"]:
                for attachment in attachments["attachments_list"]:
                    if not os.path.exists(attachment["path"]):
                        print(
                            "msg guid: {}, cannot find {} for {}".format(
                                db_sms_row["guid"],
                                attachment["path"],
                                attachment["name"],
                            )
                        )
            else:
                print(
                    'msg guid: {} cannot find attachments, datetime: "{}", subject: "{}", text: "{}"'.format(
                        db_sms_row["guid"],
                        datetime_timestamp.isoformat(),
                        subject_text,
                        body_text,
                    )
                )

    db_sms_conn.close()


def main(args):
    print("Target backup path: {}".format(args.target_backup_path))
    print("Year {}, 0 is all".format(args.year))
    print("Skip write: {}".format(args.skip_write))

    db_files_path = os.path.join(args.target_backup_path, "Manifest.db")
    print(db_files_path)
    db_files_conn = sqlite3.connect(db_files_path)
    db_files_conn.row_factory = sqlite3.Row
    db_files_cursor = db_files_conn.cursor()

    db_files_rows = db_manifest_table_files_find_sms_db(db_files_cursor)
    if 1 == len(db_files_rows):
        for db_files_row in db_files_rows:
            db_sms_path = os.path.join(
                args.target_backup_path,
                db_files_row["fileID"][0:2],
                db_files_row["fileID"],
            )
            if args.check_attachments:
                sms_db_check_attachments(
                    db_files_cursor,
                    db_sms_path,
                    args.target_backup_path,
                    args.year,
                )
            else:
                sms_db_process(
                    db_files_cursor,
                    db_sms_path,
                    args.target_backup_path,
                    args.year,
                    args.default_number,
                    args.skip_write,
                )
    else:
        print('ERROR: Multiple "Library/SMS/sms.db" found')

    db_files_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # define each option with: parser.add_argument
    parser.add_argument(
        "-t", "--target-backup-path", required=True, help="Path to the target backup"
    )
    parser.add_argument(
        "-n",
        "--default-number",
        required=True,
        help="in older database destination_caller_id do not exists so user have to set default number",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        required=False,
        help="Process this year, all when it is 0",
        default=0,
    )
    parser.add_argument(
        "--check-attachments",
        action="store_true",
        help="check if the attachments are missing, default not check mode",
    )
    parser.add_argument(
        "--skip-write",
        action="store_true",
        help="skip writing the eml file, default no skip",
    )
    args = parser.parse_args()  # automatically looks at sys.argv
    main(args)
