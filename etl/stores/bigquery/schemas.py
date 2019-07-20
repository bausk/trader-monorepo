from google.cloud.bigquery import SchemaField

CRYPTOWATCH_SNAPSHOT_SCHEMA = [
    SchemaField("hash", "STRING", mode="NULLABLE"),
    SchemaField("saved_at", "TIMESTAMP", mode="NULLABLE"),
    SchemaField("queried_at", "TIMESTAMP", mode="REQUIRED"),
    SchemaField("metadata", "STRING", mode="NULLABLE"),
    SchemaField("trades", "RECORD", mode="REPEATED", fields=(
        SchemaField("price", "FLOAT"),
        SchemaField("timestamp", "TIMESTAMP"),
        SchemaField("volume", "FLOAT")
    ))
]

CRYPTOWATCH_TICKS_SCHEMA = [
    SchemaField("queried_at", "TIMESTAMP", mode="REQUIRED"),
    SchemaField("price", "FLOAT"),
    SchemaField("timestamp", "TIMESTAMP"),
    SchemaField("volume", "FLOAT")
]

KUNAIO_TICKS_SCHEMA = [
    SchemaField("queried_at", "TIMESTAMP", mode="REQUIRED"),
    SchemaField("price", "FLOAT"),
    SchemaField("timestamp", "TIMESTAMP"),
    SchemaField("volume", "FLOAT")
]

KUNAIO_SNAPSHOT_SCHEMA = [
    SchemaField("hash", "STRING", mode="NULLABLE"),
    SchemaField("saved_at", "TIMESTAMP", mode="NULLABLE"),
    SchemaField("queried_at", "TIMESTAMP", mode="REQUIRED"),
    SchemaField("metadata", "STRING", mode="NULLABLE"),
    SchemaField("trades", "RECORD", mode="REPEATED", fields=(
        SchemaField("price", "FLOAT"),
        SchemaField("timestamp", "TIMESTAMP"),
        SchemaField("volume", "FLOAT")
    ))
]

KUNAIO_ORDERBOOK_SCHEMA = [
    SchemaField("hash", "STRING", mode="NULLABLE"),
    SchemaField("saved_at", "TIMESTAMP", mode="NULLABLE"),
    SchemaField("queried_at", "TIMESTAMP", mode="REQUIRED"),
    SchemaField("metadata", "STRING", mode="NULLABLE"),
    SchemaField("asks", "RECORD", mode="REPEATED", fields=(
        SchemaField("id", "INTEGER"),
        SchemaField("created_at", "TIMESTAMP"),
        SchemaField("avg_price", "FLOAT"),
        SchemaField("executed_volume", "FLOAT"),
        SchemaField("market", "STRING"),
        SchemaField("ord_type", "STRING"),
        SchemaField("price", "FLOAT"),
        SchemaField("remaining_volume", "FLOAT"),
        SchemaField("side", "STRING"),
        SchemaField("state", "STRING"),
        SchemaField("trades_count", "INTEGER"),
        SchemaField("volume", "FLOAT")
    )),
    SchemaField("bids", "RECORD", mode="REPEATED", fields=(
        SchemaField("id", "INTEGER"),
        SchemaField("created_at", "TIMESTAMP"),
        SchemaField("avg_price", "FLOAT"),
        SchemaField("executed_volume", "FLOAT"),
        SchemaField("market", "STRING"),
        SchemaField("ord_type", "STRING"),
        SchemaField("price", "FLOAT"),
        SchemaField("remaining_volume", "FLOAT"),
        SchemaField("side", "STRING"),
        SchemaField("state", "STRING"),
        SchemaField("trades_count", "INTEGER"),
        SchemaField("volume", "FLOAT")
    ))
]
