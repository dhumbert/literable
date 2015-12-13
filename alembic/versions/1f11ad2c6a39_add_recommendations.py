"""add recommendations

Revision ID: 1f11ad2c6a39
Revises: d563174e641
Create Date: 2015-12-12 16:13:26.279230

"""

# revision identifiers, used by Alembic.
revision = '1f11ad2c6a39'
down_revision = 'd563174e641'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('recommendations',
                    sa.Column('from_user_id', sa.Integer(), primary_key=True),
                    sa.Column('to_user_id', sa.Integer(), primary_key=True),
                    sa.Column('book_id', sa.Integer(), primary_key=True),
                    sa.Column('message', sa.String(), nullable=True),
                    sa.Column('seen', sa.Boolean()),
                    sa.Column('created_at', sa.DateTime()),
                    sa.ForeignKeyConstraint(['from_user_id'], ['users.id']),
                    sa.ForeignKeyConstraint(['to_user_id'], ['users.id']),
                    sa.ForeignKeyConstraint(['book_id'], ['books.id']))


def downgrade():
    op.drop_table('recommendations')
