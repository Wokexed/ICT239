from app import app, db
from app.model import Book, Author
from app.books import all_books  # Your dataset

# Initialize Flask app and MongoEngine
app.app_context().push()  # Needed to use db outside Flask routes

# First, clear old books to avoid conflicts
Book.objects.delete()
print("Cleared old books...")

# Insert all books into MongoDB
for book in all_books:
    try:
        # Transform authors from strings to Author objects
        authors_list = []
        if 'authors' in book and book['authors']:
            for author_name in book['authors']:
                # If author_name is a string, create Author with that name
                if isinstance(author_name, str):
                    author = Author(name=author_name, is_illustrator=False)
                    authors_list.append(author)
                # If it's already an Author object, just add it
                else:
                    authors_list.append(author_name)
        
        # Create book with transformed data
        new_book = Book(
            title=book.get('title'),
            authors=authors_list,
            genres=book.get('genres', []),
            category=book.get('category'),
            pages=book.get('pages'),
            url=book.get('url'),
            description=book.get('description', []) if isinstance(book.get('description'), list) else [book.get('description', '')],
            available=book.get('available', book.get('copies', 1)),
            copies=book.get('copies', 1)
        )
        
        new_book.save()
        print(f"✅ Uploaded: {book.get('title')}")
        
    except Exception as e:
        print(f"❌ Error uploading {book.get('title')}: {str(e)}")
        import traceback
        traceback.print_exc()

print("\nAll books uploaded successfully!")