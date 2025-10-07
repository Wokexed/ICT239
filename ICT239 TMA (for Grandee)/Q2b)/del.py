from flask import Flask, render_template, request, redirect, url_for, session, flash

try:
    from books import all_books
except ImportError:
    all_books = []
    print("Warning: books.py not found. Using empty book list.")

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Create an admin user account (admin@lib.sg, password 12345, name Admin). 
# Create also a non-admin user account (poh@lib.sg, password 12345, name Peter Oh).
users = {
    'admin@lib.sg': {
        'password': '12345',
        'is_admin': True
    },
    'peter@lib.sg': {
        'password': '12345',
        'is_admin': False
    }
}

def get_books_list():
    """Convert books from books.py format to display format"""
    books_list = []
    for idx, book in enumerate(all_books):
        # Join genres
        genre_str = ', '.join(book.get('genres', []))
        
        # Join description paragraphs
        description = '\n\n'.join(book.get('description', []))
        
        # Join authors
        author_str = ', '.join(book.get('authors', ['Unknown Author']))
        
        books_list.append({
            'id': idx + 1,
            'title': book.get('title', 'Unknown'),
            'author': author_str,
            'genre': genre_str,
            'category': book.get('category', 'Adult'),
            'pages': book.get('pages', 0),
            'cover_image': book.get('url', ''),
            'description': description,
            'copies_available': book.get('available', 1),
            'total_copies': book.get('copies', 1)
        })
    
    return books_list

@app.route("/")
def index():
    books = get_books_list()
    books_sorted = sorted(books, key=lambda x: x['title'])
    return render_template("index.html")

@app.route('/book/<int:book_id>')
def book_details(book_id):
    """Display detailed information about a specific book"""
    books = get_books_list()
    
    # Find book by id (id is index + 1)
    if 0 < book_id <= len(books):
        book = books[book_id - 1]
        return render_template('book_details.html', book=book)
    else:
        flash('Book not found.', 'danger')
        return redirect(url_for('index'))

print(f"Loaded {len(all_books)} books from books.py")