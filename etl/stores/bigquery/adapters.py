from formats.time import get_utcnow_sql_timestamp, get_unixtime_sql_timestamp


def like(adapter):
    return adapter.waits_for


class adapt_trades_to_bigquery():
    waits_for = list

    def __new__(cls, trades):
        queried_at = get_utcnow_sql_timestamp()
        return (
            None,
            None,
            queried_at,
            None,
            [(x['price'], get_unixtime_sql_timestamp(x['timestamp']), x['volume']) for x in trades]
        )


class adapt_orderbook_to_bigquery():
    waits_for = dict

    def __new__(cls, orderbook):
        queried_at = get_utcnow_sql_timestamp()
        return (
            None,
            None,
            queried_at,
            None,
            [(
                x['id'],
                get_unixtime_sql_timestamp(x['created_at']),
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
                get_unixtime_sql_timestamp(x['created_at']),
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
