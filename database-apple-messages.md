database apple messages
=======================

# table `attachment`

```sql
CREATE TABLE attachment (
    ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    created_date INTEGER DEFAULT 0,
    start_date INTEGER DEFAULT 0,
    filename TEXT,
    uti TEXT,
    mime_type TEXT,
    transfer_state INTEGER DEFAULT 0,
    is_outgoing INTEGER DEFAULT 0,
    user_info BLOB,
    transfer_name TEXT,
    total_bytes INTEGER DEFAULT 0,
    is_sticker INTEGER DEFAULT 0,
    sticker_user_info BLOB,
    attribution_info BLOB,
    hide_attachment INTEGER DEFAULT 0,
    ck_sync_state INTEGER DEFAULT 0,
    ck_server_change_token_blob BLOB DEFAULT NULL,
    ck_record_id TEXT DEFAULT NULL,
    original_guid TEXT,
    sr_ck_record_id TEXT DEFAULT NULL,
    sr_ck_sync_state INTEGER DEFAULT 0,
    sr_ck_server_change_token_blob BLOB DEFAULT NULL,
    is_commsafety_sensitive INTEGER DEFAULT 0,
    emoji_image_content_identifier TEXT DEFAULT NULL,
    emoji_image_short_description TEXT DEFAULT NULL,
    preview_generation_state INTEGER DEFAULT 0
);
```

|Column |Description    |
|-------|---------------|
|`ROWID`    |Primary key for attachment info.   |
|`guid`     |GUID for attachment info.  |
|`created_date` | Cocoa timestamp in seconds.   |
|`start_date`   | Cocoa timestamp in seconds.   |
|`filename` |Filename with absolute path.   |
|`uti`      |Apple's Uniform Type Identifier.   |
|`mime_type`    |A media type (formerly known as a Multipurpose Internet Mail Extensions).  |
|`transfer_state`   |TODO   |
|`is_outgoing`  |1 = outgoing, 0 = not outgoing.    |
|`user_info`    |TODO   |
|`transfer_name`    |The real filename without path.    |
|`total_bytes`  |File size. |
|`is_sticker`   |TODO   |
|`sticker_user_info`    |TODO   |
|`attribution_info`     |TODO   |
|`hide_attachment`      |TODO   |
|`ck_sync_state`        |TODO   |
|`ck_server_change_token_blob`  |TODO   |
|`ck_record_id`     |TODO   |
|`original_guid`    |Original GUID. Guess: the `guid` in older database, the latest `guid` format is `at_*_guid`.   |
|`sr_ck_record_id`  |TODO   |
|`sr_ck_sync_state` |TODO   |
|`sr_ck_server_change_token_blob`   |TODO   |
|`is_commsafety_sensitive`  |TODO   |
|`emoji_image_content_identifier`   |TODO   |
|`emoji_image_short_description`    |TODO   |
|`preview_generation_state` |TODO   |

# table `chat`

```sql
CREATE TABLE chat (
    ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    style INTEGER,
    state INTEGER,
    account_id TEXT,
    properties BLOB,
    chat_identifier TEXT,
    service_name TEXT,
    room_name TEXT,
    account_login TEXT,
    is_archived INTEGER DEFAULT 0,
    last_addressed_handle TEXT,
    display_name TEXT,
    group_id TEXT,
    is_filtered INTEGER,
    successful_query INTEGER,
    engram_id TEXT,
    server_change_token TEXT,
    ck_sync_state INTEGER DEFAULT 0,
    last_read_message_timestamp INTEGER DEFAULT 0,
    ck_record_system_property_blob BLOB,
    original_group_id TEXT DEFAULT NULL,
    sr_server_change_token TEXT,
    sr_ck_sync_state INTEGER DEFAULT 0,
    cloudkit_record_id TEXT DEFAULT NULL,
    sr_cloudkit_record_id TEXT DEFAULT NULL,
    last_addressed_sim_id TEXT DEFAULT NULL,
    is_blackholed INTEGER DEFAULT 0,
    syndication_date INTEGER DEFAULT 0,
    syndication_type INTEGER DEFAULT 0,
    is_recovered INTEGER DEFAULT 0,
    is_deleting_incoming_messages INTEGER DEFAULT 0,
    is_pending_review INTEGER DEFAULT 0
);
```

|Column |Description    |
|-------|---------------|
|`ROWID`    |Primary key for chat info. |
|`guid`     |GUID for chat info. |
|`style`    |TODO   |
|`state`    |TODO   |
|`account_id`   | Account GUID. |
|`properties`   |TODO   |
|`chat_identifier`  |TODO   |
|`service_name` |Service type: `SMS`, `iMessage` or `RCS`.   |
|`room_name`    |TODO   |
|`account_login`    |The account used for this message. |
|`is_archived`  |TODO   |
|`last_addressed_handle`    |The last addressed phone number.   |
|`display_name` |TODO   |
|`group_id` |GUID for group.    |
|`is_filtered`  |TODO   |
|`successful_query` |TODO   |
|`engram_id`    |TODO   |
|`server_change_token`  |TODO   |
|`ck_sync_state`    |TODO   |
|`last_read_message_timestamp`  |TODO   |
|`ck_record_system_property_blob`   |TODO   |
|`original_group_id`    |TODO   |
|`sr_server_change_token`   |TODO   |
|`sr_ck_sync_state` |TODO   |
|`cloudkit_record_id`   |TODO   |
|`sr_cloudkit_record_id`    |TODO   |
|`last_addressed_sim_id`    |TODO   |
|`is_blackholed`    |TODO   |
|`syndication_date` |TODO   |
|`syndication_type` |TODO   |
|`is_recovered`     |TODO   |
|`is_deleting_incoming_messages`    |TODO   |
|`is_pending_review`    |TODO   |

# table `chat_handle_join`

```sql
CREATE TABLE chat_handle_join (
    chat_id INTEGER REFERENCES chat (ROWID) ON DELETE CASCADE,
    handle_id INTEGER REFERENCES handle (ROWID) ON DELETE CASCADE,
    UNIQUE (chat_id, handle_id)
);
```

|Column |Description    |
|-------|---------------|
|`chat_id`      |Table `chat.ROWID`     |
|`handle_id`    |Table `handle.ROWID`   |

This table records `handle.ROWID`s in a `chat.ROWID`.

# table `chat_message_join`

```sql
CREATE TABLE "chat_message_join" (
    "chat_id" INTEGER,
    "message_id" INTEGER,
    "message_date" INTEGER DEFAULT 0,
    PRIMARY KEY ("chat_id", "message_id")
);
```

|Column |Description    |
|-------|---------------|
|`chat_id`      |Table `chat.ROWID`     |
|`message_id`   |Table `message.ROWID`  |
|`message_date` |Cocoa timestamp in nanoseconds. Cocoa timestamp in seconds in older database.  |

This table records `message.ROWID`s in a `chat.ROWID`.

# table `chat_service`

```sql
CREATE TABLE chat_service (
    service TEXT NOT NULL,
    chat INTEGER NOT NULL REFERENCES chat (ROWID) ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE (service, chat)
);
```

|Column |Description    |
|-------|---------------|
|`service`  |Service type: `SMS`, `iMessage` or `RCS`.  |
|`chat`     |Table `chat.ROWID` |

# table `handle`

```sql
CREATE TABLE "handle" (
    "ROWID" INTEGER UNIQUE,
    "id" TEXT NOT NULL,
    "country" TEXT,
    "service" TEXT NOT NULL,
    "uncanonicalized_id" TEXT,
    "person_centric_id" TEXT DEFAULT NULL,
    PRIMARY KEY ("ROWID" AUTOINCREMENT)
);
```

|Column |Description    |
|-------|---------------|
|`ROWID`    |Primary key for handle.    |
|`id`       |The phone number or email this handle represents.   |
|`country`  |The country of phone number or email.   |
|`service`  |The service of phone number or email, `SMS`, `iMessage` or `RCS`.  |
|`uncanonicalized_id`   |Uncanonical form of the phone number or email. |
|`person_centric_id`    |TODO   |

# table `message`

```sql
CREATE TABLE "message" (
    "ROWID" INTEGER,
    "guid" TEXT NOT NULL,
    "text" TEXT,
    "replace" INTEGER DEFAULT 0,
    "service_center" TEXT,
    "handle_id" INTEGER DEFAULT 0,
    "subject" TEXT,
    "country" TEXT,
    "attributedBody" BLOB,
    "version" INTEGER DEFAULT 0,
    "type" INTEGER DEFAULT 0,
    "service" TEXT,
    "account" TEXT,
    "account_guid" TEXT,
    "error" INTEGER DEFAULT 0,
    "date" INTEGER,
    "date_read" INTEGER,
    "date_delivered" INTEGER,
    "is_delivered" INTEGER DEFAULT 0,
    "is_finished" INTEGER DEFAULT 0,
    "is_emote" INTEGER DEFAULT 0,
    "is_from_me" INTEGER DEFAULT 0,
    "is_empty" INTEGER DEFAULT 0,
    "is_delayed" INTEGER DEFAULT 0,
    "is_auto_reply" INTEGER DEFAULT 0,
    "is_prepared" INTEGER DEFAULT 0,
    "is_read" INTEGER DEFAULT 0,
    "is_system_message" INTEGER DEFAULT 0,
    "is_sent" INTEGER DEFAULT 0,
    "has_dd_results" INTEGER DEFAULT 0,
    "is_service_message" INTEGER DEFAULT 0,
    "is_forward" INTEGER DEFAULT 0,
    "was_downgraded" INTEGER DEFAULT 0,
    "is_archive" INTEGER DEFAULT 0,
    "cache_has_attachments" INTEGER DEFAULT 0,
    "cache_roomnames" TEXT,
    "was_data_detected" INTEGER DEFAULT 0,
    "was_deduplicated" INTEGER DEFAULT 0,
    "is_audio_message" INTEGER DEFAULT 0,
    "is_played" INTEGER DEFAULT 0,
    "date_played" INTEGER,
    "item_type" INTEGER DEFAULT 0,
    "other_handle" INTEGER DEFAULT 0,
    "group_title" TEXT,
    "group_action_type" INTEGER DEFAULT 0,
    "share_status" INTEGER DEFAULT 0,
    "share_direction" INTEGER DEFAULT 0,
    "is_expirable" INTEGER DEFAULT 0,
    "expire_state" INTEGER DEFAULT 0,
    "message_action_type" INTEGER DEFAULT 0,
    "message_source" INTEGER DEFAULT 0,
    "associated_message_guid" TEXT,
    "associated_message_type" INTEGER DEFAULT 0,
    "balloon_bundle_id" TEXT,
    "payload_data" BLOB,
    "expressive_send_style_id" TEXT,
    "associated_message_range_location" INTEGER DEFAULT 0,
    "associated_message_range_length" INTEGER DEFAULT 0,
    "time_expressive_send_played" INTEGER,
    "message_summary_info" BLOB,
    "ck_sync_state" INTEGER DEFAULT 0,
    "ck_record_id" TEXT DEFAULT NULL,
    "ck_record_change_tag" TEXT DEFAULT NULL,
    "destination_caller_id" TEXT DEFAULT NULL,
    "sr_ck_sync_state" INTEGER DEFAULT 0,
    "sr_ck_record_id" TEXT DEFAULT NULL,
    "sr_ck_record_change_tag" TEXT DEFAULT NULL,
    "is_corrupt" INTEGER DEFAULT 0,
    "reply_to_guid" TEXT DEFAULT NULL,
    "sort_id" INTEGER DEFAULT 0,
    "is_spam" INTEGER DEFAULT 0,
    "has_unseen_mention" INTEGER DEFAULT 0,
    "thread_originator_guid" TEXT DEFAULT NULL,
    "thread_originator_part" TEXT DEFAULT NULL,
    "syndication_ranges" TEXT DEFAULT NULL,
    "was_delivered_quietly" INTEGER DEFAULT 0,
    "did_notify_recipient" INTEGER DEFAULT 0,
    "synced_syndication_ranges" TEXT DEFAULT NULL,
    "date_retracted" INTEGER DEFAULT 0,
    "date_edited" INTEGER DEFAULT 0,
    "was_detonated" INTEGER DEFAULT 0,
    "part_count" INTEGER,
    "is_stewie" INTEGER DEFAULT 0,
    "is_kt_verified" INTEGER DEFAULT 0,
    "is_sos" INTEGER DEFAULT 0,
    "is_critical" INTEGER DEFAULT 0,
    "bia_reference_id" TEXT DEFAULT NULL,
    "fallback_hash" TEXT DEFAULT NULL,
    "associated_message_emoji" TEXT DEFAULT NULL,
    "is_pending_satellite_send" INTEGER DEFAULT 0,
    "needs_relay" INTEGER DEFAULT 0,
    "schedule_type" INTEGER DEFAULT 0,
    "schedule_state" INTEGER DEFAULT 0,
    "sent_or_received_off_grid" INTEGER DEFAULT 0,
    "date_recovered" INTEGER DEFAULT 0,
    "is_time_sensitive" INTEGER DEFAULT 0,
    "ck_chat_id" TEXT,
    PRIMARY KEY ("ROWID" AUTOINCREMENT)
);
```

|Column |Description    |
|-------|---------------|
|`ROWID`    |Primary key for message.   |
|`guid`     |GUID for message.  |
|`text`     |Message text.  |
|`replace`  |TODO   |
|`service_center`   |Service center number. Usually NULL for apple messages.    |
|`handle_id`    |Table `handle.ROWID`. For incoming message it is the sender, for outgoing message it is the message sent to.   |
|`subject`  |Message subject field, usually NULL.   |
|`country`  |The country of this message, usually NULL. |
|`attributedBody`   |Apple's streamtyped data containing message text.  |
|`version`  |TODO   |
|`type`     |TODO   |
|`service`  |`SMS`, `iMessage` or `RCS`.    |
|`account`  |TODO   |
|`account_guid` |TODO   |
|`error`    |TODO   |
|`date`             |Cocoa timestamp in nanoseconds, cocoa timestamp in seconds in older database.  |
|`date_read`        |Cocoa timestamp in nanoseconds, cocoa timestamp in seconds in older database.  |
|`date_delivered`   |Cocoa timestamp in nanoseconds, cocoa timestamp in seconds in older database.  |
|`is_delivered`     |TODO, 1 = delivered.   |
|`is_finished`      |TODO, 1 = finished.    |
|`is_emote`     |TODO   |
|`is_from_me`   |1 = from me, 0 = from `handle_id`. |
|`is_empty`     |1 = empty, 0 = not empty.  |
|`is_delayed`   |1 = delayed, 0 = not delayed.  |
|`is_auto_reply`    |1 = auto reply, 0 = not auto reply.    |
|`is_prepared`  |TODO   |
|`is_read`      |1 = read, 0 = not read.    |
|`is_system_message`    |1 = system message, 0 = not system message.    |
|`is_sent`  |1 = sent, 0 = not sent.    |
|`has_dd_results`   |TODO   |
|`is_service_message`   |1 = service message, 0 = not service message.  |
|`is_forward`   |1 = forward, 0 = not forward.  |
|`was_downgraded`   |TODO   |
|`is_archive`   |TODO   |
|`cache_has_attachments`    |1 = has attachments, 0 = no attachments.   |
|`cache_roomnames`  |TODO   |
|`was_data_detected`    |TODO   |
|`was_deduplicated`     |TODO   |
|`is_audio_message`     |1 = audio message, 0 = not audio message.  |
|`is_played`    |1 = played, 0 = not played.    |
|`date_played`  |Cocoa timestamp in nanoseconds |
|`item_type`    |TODO   |
|`other_handle` |TODO   |
|`group_title`  |TODO   |
|`group_action_type`    |TODO   |
|`share_status` |TODO   |
|`share_direction`  |TODO   |
|`is_expirable` |TODO   |
|`expire_state` |1 = expired, 0 = not expired.  |
|`message_action_type`  |TODO   |
|`message_source`   |TODO   |
|`associated_message_guid`  |TODO   |
|`associated_message_type`  |TODO   |
|`balloon_bundle_id`    |TODO   |
|`payload_data` |TODO   |
|`expressive_send_style_id` |TODO   |
|`associated_message_range_location`    |TODO   |
|`associated_message_range_length`      |TODO   |
|`time_expressive_send_played`  |TODO   |
|`message_summary_info` |TODO   |
|`ck_sync_state`    |TODO   |
|`ck_record_id`     |TODO   |
|`ck_record_change_tag`     |TODO   |
|`destination_caller_id`    |The message for which phone number if multiple SIM cards.  |
|`sr_ck_sync_state` |TODO   |
|`sr_ck_record_id`  |TODO   |
|`sr_ck_record_change_tag`  |TODO   |
|`is_corrupt`   |1 = corrupted, 0 = not corrupted.  |
|`reply_to_guid`    |TODO   |
|`sort_id`  |TODO   |
|`is_spam`  |1 = spam, 0 = not spam.    |
|`has_unseen_mention`   |TODO   |
|`thread_originator_guid`   |TODO   |
|`thread_originator_part`   |TODO   |
|`syndication_ranges`   |TODO   |
|`was_delivered_quietly`    |TODO   |
|`did_notify_recipient`     |TODO   |
|`synced_syndication_ranges`    |TODO   |
|`date_retracted`   |TODO   |
|`date_edited`      |TODO   |
|`was_detonated`    |TODO   |
|`part_count`   |TODO   |
|`is_stewie`    |TODO   |
|`is_kt_verified`   |TODO   |
|`is_sos`   |TODO   |
|`is_critical`  |TODO   |
|`bia_reference_id` |TODO   |
|`fallback_hash`    |TODO   |
|`associated_message_emoji`     |TODO   |
|`is_pending_satellite_send`    |TODO   |
|`needs_relay`      |TODO   |
|`schedule_type`    |TODO   |
|`schedule_state`   |TODO   |
|`sent_or_received_off_grid`    |TODO   |
|`date_recovered`       |TODO   |
|`is_time_sensitive`    |TODO   |
|`ck_chat_id`   |TODO   |

# table `message_attachment_join`

```sql
CREATE TABLE message_attachment_join (
    message_id INTEGER REFERENCES message (ROWID) ON DELETE CASCADE,
    attachment_id INTEGER REFERENCES attachment (ROWID) ON DELETE CASCADE,
    UNIQUE (message_id, attachment_id)
);
```

|Column |Description    |
|-------|---------------|
|`message_id`       |Table `message.ROWID`.     |
|`attachment_id`    |Table `attachment.ROWID`.  |

This table records `attachment.ROWID`s in a `message.ROWID`.
