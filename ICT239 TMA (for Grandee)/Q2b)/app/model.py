from app import db

class Book(db.Document):
    title = db.StringField(required=True)
    authors = db.ListField(db.StringField())
    genres = db.ListField(db.StringField())
    category = db.StringField()
    pages = db.IntField()
    url = db.StringField()
    description = db.ListField(db.StringField())
    available = db.IntField()
    copies = db.IntField()

    meta = {'collection': 'books'}

    @staticmethod
    def get_book_by_id(book_id):
        return Book.objects(id=book_id).first()
    
    @staticmethod
    def delete_book_by_id(book_id):
        book = Book.get_book_by_id(book_id)
        if book:
            book.delete()
            return True
        return False
    
    @staticmethod
    def update_book(book_id, data):
        book = Book.get_book_by_id(book_id)
        if book:
            for key, value in data.items():
                setattr(book, key, value)
            book.save()
            return True
        return False    
    
    @staticmethod
    def add_book(data):
        book = Book(**data)
        book.save()
        return book
    
    