from dbmodels.db import SourceSchema, SourceTypesEnum
from .bigquery_source import BigquerySource
from .abstract_source import AbstractSource


def select_source(source_definition: SourceSchema) -> AbstractSource:
    sources_map = {
        SourceTypesEnum.bigquery: BigquerySource,
    }

    return sources_map[source_definition.typename]
