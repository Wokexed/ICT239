from app import app, db
from app.model import Book
from app.books import all_books  # Your dataset

# Initialize Flask app and MongoEngine
app.app_context().push()  # Needed to use db outside Flask routes

# Insert all books into MongoDB
for book in all_books:
    if not Book.objects(title=book['title']).first():  # Avoid duplicates
        Book.add_book(book)

print("All books uploaded successfully!")
