"""add book rating

Revision ID: af26f9f287f
Revises: 4b24fcc9fbbc
Create Date: 2013-09-19 16:27:26.894128

"""

# revision identifiers, used by Alembic.
revision = 'af26f9f287f'
down_revision = '4b24fcc9fbbc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('books',
        sa.Column('rating', sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column('books', 'rating')
