def upgrade() -> None:
    op.add_column('article', sa.Column('tsv', postgresql.TSVECTOR(), nullable=True))

def downgrade() -> None:
    op.drop_column('article', 'tsv')

def upgrade():
    op.add_column('article', sa.Column('tsv_zh', sa.dialects.postgresql.TSVECTOR(), nullable=True))
    op.add_column('article', sa.Column('tsv_en', sa.dialects.postgresql.TSVECTOR(), nullable=True))
    op.create_index('idx_article_tsv_zh', 'article', ['tsv_zh'], postgresql_using='gin')
    op.create_index('idx_article_tsv_en', 'article', ['tsv_en'], postgresql_using='gin')
    op.drop_index('idx_article_tsv', table_name='article')
    op.drop_column('article', 'tsv')

def downgrade():
    op.add_column('article', sa.Column('tsv', sa.dialects.postgresql.TSVECTOR(), nullable=True))
    op.create_index('idx_article_tsv', 'article', ['tsv'], postgresql_using='gin')
    op.drop_index('idx_article_tsv_zh', table_name='article')
    op.drop_index('idx_article_tsv_en', table_name='article')
    op.drop_column('article', 'tsv_zh')
    op.drop_column('article', 'tsv_en')


alembic revision -m "split tsv to tsv_zh and tsv_en"
docker compose -f docker-compose.dev.yml run --rm backend alembic upgrade head