"""Remove page count and add word count

Revision ID: 2623007f4871
Revises: 522483334984
Create Date: 2015-11-15 18:58:25.188320

"""

# revision identifiers, used by Alembic.
revision = '2623007f4871'
down_revision = '522483334984'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('books',
        sa.Column('word_count', sa.Integer())
    )
    op.drop_column('books', 'pages')


def downgrade():
    op.add_column('books',
        sa.Column('pages', sa.Integer())
    )
    op.drop_column('books', 'word_count')
