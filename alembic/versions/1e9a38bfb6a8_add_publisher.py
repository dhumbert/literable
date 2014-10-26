"""Add publisher

Revision ID: 1e9a38bfb6a8
Revises: 229aa0654b75
Create Date: 2014-10-25 21:49:20.383025

"""

# revision identifiers, used by Alembic.
revision = '1e9a38bfb6a8'
down_revision = '229aa0654b75'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('publishers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('books',
        sa.Column('publisher_id', sa.Integer(), sa.ForeignKey('publishers.id'))
    )


def downgrade():
    op.drop_table('publishers')
    op.drop_column('books', 'publisher_id')
