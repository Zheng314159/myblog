# app/models/fts_pg.py

from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

tsv_zh_column = Column("tsv_zh", TSVECTOR, nullable=True)
tsv_en_column = Column("tsv_en", TSVECTOR, nullable=True)
tsv_zh_index = Index("idx_article_tsv_zh", tsv_zh_column, postgresql_using="gin")
tsv_en_index = Index("idx_article_tsv_en", tsv_en_column, postgresql_using="gin")
