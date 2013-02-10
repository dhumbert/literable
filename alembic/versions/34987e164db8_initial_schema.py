"""Initial schema

Revision ID: 34987e164db8
Revises: None
Create Date: 2013-02-09 15:53:56.890188

"""

# revision identifiers, used by Alembic.
revision = '34987e164db8'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('genres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['genres.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('filename', sa.String(), nullable=True),
        sa.Column('cover', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('genre_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('books_tags',
        sa.Column('tag_id', sa.Integer(), nullable=True),
        sa.Column('book_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint()
    )


def downgrade():
    op.drop_table('books_tags')
    op.drop_table('books')
    op.drop_table('tags')
    op.drop_table('genres')
