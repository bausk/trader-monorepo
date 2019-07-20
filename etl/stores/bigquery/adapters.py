from formats.time import get_utcnow_sql_timestamp, get_unixtime_sql_timestamp, get_stringtime_sql_timestamp


def adapt_trades_to_bigquery(trades):
    queried_at = get_utcnow_sql_timestamp()
    return (
        None,
        None,
        queried_at,
        None,
        [(x['price'], get_unixtime_sql_timestamp(x['timestamp']), x['volume'])
         for x in trades]
    )


def adapt_orderbook_to_bigquery(orderbook):
    queried_at = get_utcnow_sql_timestamp()
    return (
        None,
        None,
        queried_at,
        None,
        [(
            x['id'],
            get_stringtime_sql_timestamp(x['created_at']),
            x["avg_price"],
            x["executed_volume"],
            x["market"],
            x["ord_type"],
            x["price"],
            x["remaining_volume"],
            x["side"],
            x["state"],
            x["trades_count"],
            x["volume"])
            for x in orderbook['asks']
         ],
        [(
            x['id'],
            get_stringtime_sql_timestamp(x['created_at']),
            x["avg_price"],
            x["executed_volume"],
            x["market"],
            x["ord_type"],
            x["price"],
            x["remaining_volume"],
            x["side"],
            x["state"],
            x["trades_count"],
            x["volume"])
            for x in orderbook['bids']
         ]
    )


def adapt_ticks_to_bigquery(ticks):
    queried_at = get_utcnow_sql_timestamp()
    return [(
        queried_at,
        x['price'],
        get_unixtime_sql_timestamp(x['timestamp']),
        x['volume']
    ) for x in ticks]
