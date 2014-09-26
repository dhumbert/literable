"""Add ES index

Revision ID: 229aa0654b75
Revises: ad9fe8cc23f
Create Date: 2014-09-25 20:45:35.331963

"""

# revision identifiers, used by Alembic.
revision = '229aa0654b75'
down_revision = 'ad9fe8cc23f'

from alembic import op
import sqlalchemy as sa
from elasticsearch import Elasticsearch
from literable import config


def upgrade():
    es = Elasticsearch(config.ELASTICSEARCH_NODES)
    es.indices.create(index=config.ELASTICSEARCH_INDEX)
    es.indices.put_mapping(index=config.ELASTICSEARCH_INDEX,
                           doc_type=config.ELASTICSEARCH_DOC_TYPE,
                           body={
                               config.ELASTICSEARCH_DOC_TYPE: {
                                   'properties': {
                                       'title': {'type': 'string', 'analyzer': 'snowball'},
                                       'author': {'type': 'string', 'analyzer': 'snowball'},
                                       'series': {'type': 'string', 'analyzer': 'snowball'},
                                       'description': {'type': 'string', 'analyzer': 'snowball'},
                                       'content': {'type': 'string'},
                                   }
                               }
                           })

def downgrade():
    es = Elasticsearch(config.ELASTICSEARCH_NODES)
    es.indices.delete(index=config.ELASTICSEARCH_INDEX)
