from datetime import datetime
import pytz
import asyncio
import json
from google.oauth2 import service_account
from google.cloud import bigquery
from typing import Type
from secrets_management.manage import decrypt_credentials
from .abstract_source import AbstractSource

credfile = decrypt_credentials(which=['./.secrets/keyring.json'])
creds_json = json.loads(credfile[0])
creds = service_account.Credentials.from_service_account_info(creds_json)
bigquery_client = bigquery.Client(
    credentials=creds, project=creds_json['project_id']
)


sql_query_get_intervals = r"""
with
  c as (select *,
    TIMESTAMP_ADD(queried_at, INTERVAL 3600 SECOND) as queried_end,
    max(TIMESTAMP_ADD(queried_at, INTERVAL 3600 SECOND)) over (order by queried_at rows between unbounded preceding and 1 preceding) as previous_max
    from `livewater.production.kunaTicksBTCUAH`
  )
select queried_at, 
    coalesce(lead(previous_max) over (order by queried_at),
   (select max(queried_end) from c)
               ) as queried_end
from c 
where previous_max < queried_at 
   or previous_max is null
order by queried_at desc
limit {limit}
"""

sql_query_get_intervals_2 = r"""
with
  origin as
  (select
  queried_at,
  TIMESTAMP_ADD(queried_at, INTERVAL {interval} SECOND) as queried_end
  from `{table_fullname}`
  order by queried_at desc
  ),
  c as
  ( select *, max(queried_end) over (order by queried_at
        rows between unbounded preceding
        and 1 preceding)
                as previous_max
    from origin
  )
select queried_at, 
    coalesce(lead(previous_max) over (order by queried_at),
   (select max(queried_end) from origin)
               ) as queried_end
from c 
where previous_max < queried_at 
   or previous_max is null
order by queried_at desc
limit {limit}
"""


def exec_query(query, client, **kwargs) -> bigquery.table.RowIterator:
    print(client)
    print(query)
    job = client.query(query, **kwargs)
    return job.result()


class BigquerySource(AbstractSource):
    @classmethod
    async def list_availability_intervals(cls, interval: int, table_fullname: str, limit: int=100) -> list:
        sql_query = sql_query_get_intervals_2.format(
            interval=interval,
            table_fullname=table_fullname,
            limit=limit,
        )
        loop = asyncio.get_running_loop()
        bigquery_result = await loop.run_in_executor(None, exec_query, sql_query, bigquery_client)
        return bigquery_result
