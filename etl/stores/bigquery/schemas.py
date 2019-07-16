CRYPTOWATCH_SNAPSHOT_SCHEMA = [
    {
        "name": "hash",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "saved_at",
        "type": "TIMESTAMP",
        "mode": "NULLABLE"
    },
    {
        "name": "queried_at",
        "type": "TIMESTAMP",
        "mode": "REQUIRED"
    },
    {
        "name": "metadata",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "trades",
        "type": "RECORD",
        "mode": "REPEATED",
        "fields": [
            {
                "name": "price",
                "type": "FLOAT"
            },
            {
                "name": "timestamp",
                "type": "TIMESTAMP"
            },
            {
                "name": "volume",
                "type": "FLOAT"
            }
        ]
    }
]

KUNAIO_SNAPSHOT_SCHEMA = [
    {
        "name": "hash",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "saved_at",
        "type": "TIMESTAMP",
        "mode": "NULLABLE"
    },
    {
        "name": "queried_at",
        "type": "TIMESTAMP",
        "mode": "REQUIRED"
    },
    {
        "name": "metadata",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "trades",
        "type": "RECORD",
        "mode": "REPEATED",
        "fields": [
            {
                "name": "id",
                "type": "INTEGER"
            },
            {
                "name": "price",
                "type": "FLOAT"
            },
            {
                "name": "timestamp",
                "type": "TIMESTAMP"
            },
            {
                "name": "volume",
                "type": "FLOAT"
            }
        ]
    }
]

KUNAIO_ORDERBOOK_SCHEMA = [
    {
        "name": "hash",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "saved_at",
        "type": "TIMESTAMP",
        "mode": "NULLABLE"
    },
    {
        "name": "queried_at",
        "type": "TIMESTAMP",
        "mode": "REQUIRED"
    },
    {
        "name": "metadata",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "trades",
        "type": "RECORD",
        "mode": "REPEATED",
        "fields": [
            {
                "name": "avg_price",
                "type": "FLOAT"
            },
            {
                "name": "created_at",
                "type": "TIMESTAMP"
            },
            {
                "name": "executed_volume",
                "type": "FLOAT"
            },
            {
                "name": "id",
                "type": "INTEGER"
            },
            {
                "name": "market",
                "type": "STRING"
            },
            {
                "name": "ord_type",
                "type": "STRING"
            },
            {
                "name": "price",
                "type": "FLOAT"
            },
            {
                "name": "remaining_volume",
                "type": "FLOAT"
            },
            {
                "name": "side",
                "type": "STRING"
            },
            {
                "name": "state",
                "type": "STRING"
            },
            {
                "name": "trades_count",
                "type": "INTEGER"
            },
            {
                "name": "volume",
                "type": "FLOAT"
            }
        ]
    }
]
