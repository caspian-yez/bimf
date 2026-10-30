database google messages
========================

# table `sms`

```sql
CREATE TABLE sms (
    _id INTEGER PRIMARY KEY,
    thread_id INTEGER,
    address TEXT,
    m_size INTEGER,
    person INTEGER,
    date INTEGER,
    date_sent INTEGER DEFAULT 0,
    protocol INTEGER,
    read INTEGER DEFAULT 0,
    status INTEGER DEFAULT -1,
    type INTEGER,
    reply_path_present INTEGER,
    subject TEXT,
    body TEXT,
    service_center TEXT,
    locked INTEGER DEFAULT 0,
    sim_id INTEGER DEFAULT -1,
    error_code INTEGER DEFAULT 0,
    seen INTEGER DEFAULT 0,
    ipmsg_id INTEGER DEFAULT 0
);
```

|Column |Description    |
|-------|---------------|
|`address`          |Phone number of the sender or recipient.   |
|`date`             |Unix timestamp in milliseconds the message was sent or received. |
|`date_sent`        |Unix timestamp in milliseconds the message was sent.   |
|`protocol`         |Mostly 0 for sms messages. |
|`read`             |1 = Read, 0 = Unread.  |
|`status`           |-1 = None, 0 = Complete, 32 = Pending, 64 = Failed.    |
|`type`             |1 = Received, 2 = Sent, 3 = Draft, 4 = Outbox, 5 = Failed, 6 = Queued. |
|`subject`          |Usually NULL for SMS messages. |
|`body`             |The message text.  |
|`service_center`   |Service center number. Usually NULL for sent messages. |
|`locked`           |1 if the message is locked in the messaging app, otherwise 0.  |
|`sim_id`           |Identifier of the SIM / phone subscription the message belongs to. |
