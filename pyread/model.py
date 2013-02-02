from pyread import book_upload_set, db

def get_books():
    return Book.query.order_by(Book.title).all()

def save_book(attrs):
        filename = book_upload_set.save(attrs[2])
        book = Book(attrs[0], attrs[1], filename)
        db.session.add(book)
        db.session.commit()

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    filename = db.Column(db.String)

    def __init__(self, title, author, filename):
        self.title = title
        self.author = author
        self.filename = filename