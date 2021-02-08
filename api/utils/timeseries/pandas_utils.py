import logging
from datetime import timedelta
import pandas as pd


logger = logging.getLogger(__name__)


def resample_primitives(primitives: list, period: int) -> list:
    try:
        resampled = []
        for primitive in primitives:
            series = pd.Series(primitive["value"], index=primitive["timestamp"])
            series = (
                series.resample(timedelta(minutes=period), base=0)
                .max()
                .fillna(method="ffill")
            )
            series = [{"timestamp": x, "value": y} for x, y in series.items()]
            resampled.append(series)
        return resampled
    except Exception as e:
        logger.error("resample_primitives received unexpected primitives")
        logger.error(e)
        return []
