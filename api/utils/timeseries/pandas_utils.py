import json
from datetime import timedelta
import pandas as pd

from utils.schemas.dataflow_schemas import SignalResultSchema, PrimitivesSchema


def resample_primitives(signal: dict, period: int) -> SignalResultSchema:
    try:
        primitives = PrimitivesSchema(__root__=json.loads(signal['primitives']))
    except Exception as e:
        return None
    resampled = []
    for primitive in primitives.__root__:
        idx, vals = zip(*((x.timestamp, x.value) for x in primitive))
        series = pd.Series(vals, index=idx)
        series = series.resample(timedelta(minutes=period), base=0).max().fillna(method='ffill')
        series = [{'timestamp': x, 'value': y} for x, y in series.items()]
        resampled.append(series)
    return SignalResultSchema(**{**signal, 'primitives': resampled})
