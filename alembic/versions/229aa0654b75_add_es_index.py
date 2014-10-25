"""Add ES index

Revision ID: 229aa0654b75
Revises: ad9fe8cc23f
Create Date: 2014-09-25 20:45:35.331963

"""

# revision identifiers, used by Alembic.
revision = '229aa0654b75'
down_revision = 'ad9fe8cc23f'

from elasticutils import get_es
from literable import app


def upgrade():
    es = get_es(urls=app.config['ELASTICSEARCH_NODES'])
    es.indices.create(index=app.config['ELASTICSEARCH_INDEX'])
    es.indices.put_mapping(index=app.config['ELASTICSEARCH_INDEX'],
                           doc_type=app.config['ELASTICSEARCH_DOC_TYPE'],
                           body={
                               app.config['ELASTICSEARCH_DOC_TYPE']: {
                                   'properties': {
                                       'id': {'type': 'integer'},
                                       'title': {'type': 'string', 'analyzer': 'snowball'},
                                       'author': {'type': 'string', 'analyzer': 'snowball'},
                                       'series': {'type': 'string', 'analyzer': 'snowball'},
                                       'description': {'type': 'string', 'analyzer': 'snowball'},
                                       'content': {'type': 'string'},
                                   }
                               }
                           })

def downgrade():
    es = get_es(urls=app.config['ELASTICSEARCH_NODES'])
    es.indices.delete(index=app.config['ELASTICSEARCH_INDEX'])
