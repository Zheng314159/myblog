import os
from sqlalchemy.engine.url import make_url

from app.core.search.sqlite_search_impl import SQLiteFTSSearch
from app.core.search.pg_search_impl import PostgresFTSSearch
from app.core.config import settings
from typing import Type
from app.core.search.fts_base_interface import BaseFTSSearch

FTSSearch: Type[BaseFTSSearch]

db_url = make_url(settings.database_url)

if db_url.drivername.startswith("sqlite"):
    FTSSearch = SQLiteFTSSearch
else:
    FTSSearch = PostgresFTSSearch

__all__ = ["FTSSearch"]

