LIBRARY_PATH = "../library/"
SECRET_KEY = "=JbX0gvs3ivIZkST+HI"
SQLALCHEMY_DATABASE_URI = "sqlite:///../library.db"
BOOKS_PER_PAGE = 5
EBOOK_EXTENSIONS = ('epub', 'pdf', 'ibooks')
WRITE_META_ON_SAVE = True
ADD_SERIES_TO_META_TITLE = True
DEMO = False
ELASTICSEARCH_NODES = (
    {"host": "localhost", "port": 9200},
)
ELASTICSEARCH_INDEX = "literable"
ELASTICSEARCH_DOC_TYPE = "book"