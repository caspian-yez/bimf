#!/usr/bin/env python3
import sys
import os
import datetime
import zoneinfo
import sqlite3
import email.message
import email.utils

# CREATE TABLE sms (
# _id INTEGER PRIMARY KEY,          /* row index 00 */
# thread_id INTEGER,                /* row index 01 */
# address TEXT,                     /* row index 02 */
# m_size INTEGER,                   /* row index 03 */
# person INTEGER,                   /* row index 04 */
# date INTEGER,                     /* row index 05, received unix timestamp */
# date_sent INTEGER DEFAULT 0,      /* row index 06, sent unix timestamp of sender */
# protocol INTEGER,                 /* row index 07, Protocol used by the message, its mostly 0 in case of SMS messages. */
# read INTEGER DEFAULT 0,           /* row index 08, Read Message = 1, Unread Message = 0. */
# status INTEGER DEFAULT -1,        /* row index 09, None = -1, Complete = 0, Pending = 32, Failed = 64. */
# type INTEGER,                     /* row index 10, 1 = Received, 2 = Sent, 3 = Draft, 4 = Outbox, 5 = Failed, 6 = Queued */
# reply_path_present INTEGER,       /* row index 11 */
# subject TEXT,                     /* row index 12 */
# body TEXT,                        /* row index 13 */
# service_center TEXT,              /* row index 14 */
# locked INTEGER DEFAULT 0,         /* row index 15 */
# sim_id INTEGER DEFAULT -1,        /* row index 16, id of the phone subscription (SIM). These are values like 0, 1, 2  etc. based on how the phone assigns the index to the sim being used. */
# error_code INTEGER DEFAULT 0,     /* row index 17 */
# seen INTEGER DEFAULT 0,           /* row index 18 */
# ipmsg_id INTEGER DEFAULT 0        /* row index 19 */
# )


def db_type_to_str(num: int) -> str:
    type_string: str = ""
    match num:
        case 1:
            type_string = "Received"
        case 2:
            type_string = "Sent"
        case 3:
            type_string = "Draft"
        case 4:
            type_string = "Outbox"
        case 5:
            type_string = "Failed"
        case 6:
            type_string = "Queued"
        case _:
            type_string = "Unknown"

    return type_string


def db_status_to_str(num: int) -> str:
    status_string: str = ""
    match num:
        case -1:
            status_string = "None"
        case 0:
            status_string = "Complete"
        case 32:
            status_string = "Pending"
        case 64:
            status_string = "Failed"
        case _:
            status_string = "Unknown"

    return status_string


def main():
    if 3 != len(sys.argv):
        print("need parameters: <database filepath> <phone number>")
        return

    print(sys.argv[0])  # program name
    print(sys.argv[1])  # database file path
    print(sys.argv[2])  # phone number

    # 1. Connect to the database file
    conn = sqlite3.connect(sys.argv[1])

    # 2. Create a cursor object
    cursor = conn.cursor()

    # 3. Execute the SQL query
    cursor.execute("SELECT * FROM sms")

    # 4. Fetch the data
    rows = cursor.fetchall()

    la_tz = zoneinfo.ZoneInfo("Asia/Shanghai")

    # 5. Loop through and print the results
    for row in rows:
        msg = email.message.EmailMessage()

        msg["Application"] = "Android-Google-Messages"

        msg["Database-ID"] = str(row[0])

        msg["Date-Unix-Timestamp-Milliseconds"] = str(row[5])

        msg["Date-Sent-Unix-Timestamp-Milliseconds"] = str(row[6])

        if row[7]:
            msg["Protocol"] = str(row[7])
        else:
            msg["Protocol"] = ""

        if row[14]:
            msg["Service-Center"] = row[14]
        else:
            msg["Service-Center"] = ""

        if row[9]:
            status_string = db_status_to_str(row[9])
            if "Unknown" == status_string:
                print("Unknow status: {}".format(row[9]))
                print(row)
                break
            else:
                msg["Status"] = str(row[9]) + "; " + status_string
        else:
            msg["Status"] = ""

        if row[10]:
            type_string = db_type_to_str(row[10])
            if "Unknown" == type_string:
                print("Unknow type: {}".format(row[10]))
                print(row)
                break
            else:
                msg["Type"] = str(row[10]) + "; " + type_string
        else:
            msg["Type"] = ""

        # common email headers
        if 0 == row[6]:
            local_datetime = datetime.datetime.fromtimestamp(row[5] / 1000, la_tz)
        else:
            local_datetime = datetime.datetime.fromtimestamp(row[6] / 1000, la_tz)

        msg["Date"] = email.utils.format_datetime(local_datetime)

        match row[10]:
            case 1:
                msg["From"] = row[2]
                msg["To"] = sys.argv[2]
            case 2 | 5:
                msg["From"] = sys.argv[2]
                msg["To"] = row[2]
            case _:
                print("Unknow type: {}".format(row[10]))
                print(row)
                break

        if row[12]:
            msg["Subject"] = row[12]
        else:
            msg["Subject"] = ""

        if row[13]:
            msg.set_content(row[13])

        filename = str(row[0]) + ".eml"

        if os.path.exists(filename):
            print("filename {} exists".format(filename))
        else:
            fp = open(filename, "w")
            fp.write(msg.as_string())
            fp.close()

    # 6. Close the connection
    conn.close()


if __name__ == "__main__":
    main()
