
history_format = ['timestamp', 'id', 'created_at', 'price', 'volume']
orderbook_format = ['timestamp', 'bid', 'ask', 'bid_volume', 'bid_weight', 'ask_volume', 'ask_weight']

signal_format = [
    'buy',
    'sell',
    'buy_datetime',
    'sell_datetime',
    'decision'
]

datastore_records = dict(
    created_at="timestamp with time zone NOT NULL",
    collected_at="timestamp with time zone NOT NULL",
    data="jsonb",
    metadata="jsonb",
    id="bigserial NOT NULL",
)

trading_records = dict(
    id="bigserial NOT NULL",
    created_at="timestamp with time zone",
    price="real NOT NULL",
    volume="double precision NOT NULL"
)

status_records = dict(
    id="bigserial NOT NULL",
    created_at="timestamp with time zone",
    name="varchar(128) UNIQUE NOT NULL",
    value="boolean",
    multivalue="jsonb"
)
