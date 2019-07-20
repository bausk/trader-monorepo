from google.cloud import bigquery
from secrets_management import get_environment

from .table_operations import create_table, append_to_table
from .adapters import adapt_orderbook_to_bigquery, adapt_trades_to_bigquery, like


class BigQueryStore():
    def __init__(self, name, schema, *args, **kwargs):
        self.is_table_created = False
        self.client = bigquery.Client()
        self.name = name
        self.table_schema = schema

    def get_table_name(self):
        env = get_environment()
        return (self.client.project, env, self.name)
    
    async def write(self, data):
        if not self.is_table_created:
            self.table = await create_table(self.client, self.get_table_name(), self.table_schema)
            self.is_table_created = True
        adapted_data = None
        if type(data) is like(adapt_orderbook_to_bigquery):
            adapted_data = adapt_orderbook_to_bigquery(data)
        elif type(data) is like(adapt_trades_to_bigquery):
            adapted_data = adapt_trades_to_bigquery(data)
        return await append_to_table(self.client, self.table, adapted_data)
