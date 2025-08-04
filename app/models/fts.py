# app/models/fts.py

from sqlalchemy import Text, Column, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

def get_fts_columns(is_postgres: bool):
    """根据数据库类型动态返回 tsvector 或 Text 字段及索引"""
    if is_postgres:
        tsv_zh = Column("tsv_zh", TSVECTOR, nullable=True)
        tsv_en = Column("tsv_en", TSVECTOR, nullable=True)
        tsv_zh_idx = Index("idx_article_tsv_zh", tsv_zh, postgresql_using="gin")
        tsv_en_idx = Index("idx_article_tsv_en", tsv_en, postgresql_using="gin")
    else:
        tsv_zh = Column("tsv_zh", Text, nullable=True)
        tsv_en = Column("tsv_en", Text, nullable=True)
        tsv_zh_idx = None
        tsv_en_idx = None

    return {
        "tsv_zh": tsv_zh,
        "tsv_en": tsv_en,
        "indexes": [tsv_zh_idx, tsv_en_idx] if tsv_zh_idx else []
    }
