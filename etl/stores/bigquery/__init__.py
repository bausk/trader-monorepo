from google.cloud import bigquery
from .table_operations import create_table
from .write_data import write_data
from secrets_management import get_environment


class BigQueryStore():
    def __init__(self, name, schema, *args, **kwargs):
        self.is_table_created = False
        self.client = bigquery.Client()
        self.name = name
        self.table_schema = schema

    def get_table_name(self):
        env = get_environment()
        return f"{self.client.project}.{env}.{self.name}"
    
    async def write(self, data):
        if not self.is_table_created:
            await create_table(self.client, self.get_table_name(), self.table_schema)
            self.is_table_created = True
        write_data(self.client, data)
        return True
