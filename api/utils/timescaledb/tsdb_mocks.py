import logging
from datetime import datetime, timedelta
from utils.schemas.response_schemas import OHLCSchema
from utils.schemas.request_schemas import DataRequestSchema


logger = logging.getLogger(__name__)


def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta


async def mock_get_terminal_data(
    session_id, request_params: DataRequestSchema, request
):
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    period = timedelta(minutes=request_params.period)
    from_dt = ceil_dt(request_params.from_datetime, period)
    to_dt = ceil_dt(request_params.to_datetime, period)
    assert from_dt < to_dt
    data = []
    while from_dt < to_dt:
        ohlc = OHLCSchema(
            time=from_dt,
            open=10.0,
            high=15.5,
            low=8.1,
            close=14.1,
            volume=20,
        )
        data.append(ohlc)
        from_dt = from_dt + period
    return data
