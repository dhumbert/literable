"""Create users

Revision ID: 189579d72332
Revises: af26f9f287f
Create Date: 2013-09-19 17:44:52.912852

"""

# revision identifiers, used by Alembic.
revision = '189579d72332'
down_revision = 'af26f9f287f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('users', 
        sa.Column('id', sa.Integer()),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(40), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('users')
