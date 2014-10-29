"""Add sort value to taxonomy

Revision ID: 3a878f4565bb
Revises: 438588d08e4f
Create Date: 2014-10-29 15:09:26.066248

"""

# revision identifiers, used by Alembic.
revision = '3a878f4565bb'
down_revision = '438588d08e4f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('taxonomies', sa.Column('name_sort', sa.String(), nullable=True))

    connection = op.get_bind()
    taxonomies = sa.Table('taxonomies', sa.MetaData(), autoload=True, autoload_with=connection)
    for tax in connection.execute(sa.select([taxonomies])).fetchall():
        name_sort = tax['name']

        if tax['type'] == 'author':
            name_split = tax['name'].split(' ')
            if len(name_split) > 1:
                name_sort = u"{}, {}".format(name_split[-1], " ".join(name_split[0:-1]))

        connection.execute(
            taxonomies.update().where(taxonomies.c.id == tax['id']).values(name_sort=name_sort)
        )

    op.alter_column('taxonomies', 'name_sort', nullable=False)


def downgrade():
    op.drop_column('taxonomies', 'name_sort')
