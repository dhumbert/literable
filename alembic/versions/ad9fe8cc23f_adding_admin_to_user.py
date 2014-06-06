"""Adding admin to user

Revision ID: ad9fe8cc23f
Revises: 17f94907316b
Create Date: 2014-06-05 21:38:21.542539

"""

# revision identifiers, used by Alembic.
revision = 'ad9fe8cc23f'
down_revision = '17f94907316b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users',
                  sa.Column('admin', sa.Boolean(), server_default=sa.DefaultClause('0'), nullable=False))

    # make all current users admins
    connection = op.get_bind()
    users = sa.Table('users', sa.MetaData(), autoload=True, autoload_with=connection)
    connection.execute(
        users.update().values(admin=True)
    )


def downgrade():
    op.drop_column('users', 'admin')
