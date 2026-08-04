Backup as Internet Message Format
=================================

# Introduction

We have many instant messaging apps today, such as SMS, MMS, RCS, Whatsapp, Facebook Messenger, Telegram, Snapchat, WeChat, QQ, Signal, Slack, Microsoft Teams etc. But the core is the same to email so I start this project to backup messages as eml format for archival. I choose email format as it is an open standard, human machine readable.

# NOTICE

This project will convert the original data into email format, so the result should not be used as legal evidence as it's easy to forge.

# Andriod Messages Converter

As I only have Andriod 4.2 database at hand so this converter may not work with higher version of databases.

Reference: https://www.synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/

email header to database table sms column map:

|email header                               |database column                                                                            |
|-------------------------------------------|-------------------------------------------------------------------------------------------|
|`Application`                              |defaults to `Android-Google-Messages`                                                      |
|`Database-ID`                              |`_id` in database                                                                          |
|`Date-Unix-Timestamp-Milliseconds`         |`date` in milliseconds                                                                     |
|`Date-Sent-Unix-Timestamp-Milliseconds`    |`date_send` in milliseconds                                                                |
|`Protocol`                                 |`protocol` in integer                                                                      |
|`Service-Center`                           |`service_center`                                                                           |
|`Status`                                   |`status` in integer and string                                                             |
|`Type`                                     |`type` in integer and string                                                               |
|`Date`                                     |`date_send` or `date` if `date_send` is 0                                                  |
|`From`                                     |`address` if `type` is 1 (Received) or the phone number if `type` is 2 (Sent), 5 (Failed)  |
|`To`                                       |the phone number if `type` is 1 (Received) or `address` if `type` is 2 (Sent), 5 (Failed)  |
|`Subject`                                  |`subject`                                                                                  |
|message body                               |`body`                                                                                     |
